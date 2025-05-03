# utils/weather_predictor.py

import pandas as pd
import numpy as np
import joblib
import os
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
from sklearn.model_selection import cross_val_score
from sklearn.pipeline import Pipeline
from sklearn.multioutput import MultiOutputRegressor
from sqlalchemy import create_engine
from models.cleaned_models import CleanedHistoricalWeather
from config import Config
from flask import jsonify, current_app  

class WeatherPredictor:
    def __init__(self, days_to_predict=5, model_path='models/ml_models'):
        self.days_to_predict = days_to_predict
        self.model_path = model_path
        self.feature_cols = None
        self.target_cols = ['temp_max', 'temp_min']
        self.model = None
        self.engine = create_engine(Config.SQLALCHEMY_DATABASE_URI)
        self.X_train = None  # 新增训练数据存储
        self.y_train = None

        os.makedirs(self.model_path, exist_ok=True)

    def load_data(self, city_name, start_date=None, end_date=None):
        query = CleanedHistoricalWeather.query.filter(
            CleanedHistoricalWeather.city_name == city_name
        )
        if start_date:
            query = query.filter(CleanedHistoricalWeather.date >= start_date)
        if end_date:
            query = query.filter(CleanedHistoricalWeather.date <= end_date)

        query = query.with_entities(
            CleanedHistoricalWeather.date,
            CleanedHistoricalWeather.temp_max,
            CleanedHistoricalWeather.temp_min,
            CleanedHistoricalWeather.weather,
            CleanedHistoricalWeather.wind_dir
        )

        df = pd.read_sql(query.statement, self.engine)
        
        if df.empty:
            raise ValueError(f"没有找到{city_name}的历史数据")
        if not {'temp_max', 'temp_min'}.issubset(df.columns):
            raise KeyError("数据缺少温度字段")
            
        return df

    def feature_engineering(self, df):
        non_numeric_cols = ['city_code', 'city_name', 'weather', 'wind_dir']
        df = df.drop(columns=non_numeric_cols, errors='ignore')

        df['date'] = pd.to_datetime(df['date'], errors='coerce')
        df = df.dropna(subset=['date'])
        df.set_index('date', inplace=True)

        df['day_of_year'] = df.index.dayofyear.astype(float)
        df['day_of_week'] = df.index.dayofweek.astype(float)
        df['month'] = df.index.month.astype(float)
        df['season'] = (df.index.month % 12 + 3) // 3

        for i in range(1, 8):
            df[f'temp_max_lag_{i}'] = df['temp_max'].shift(i).astype(float)
            df[f'temp_min_lag_{i}'] = df['temp_min'].shift(i).astype(float)

        window_sizes = [3, 7]
        for col in ['temp_max', 'temp_min']:
            for ws in window_sizes:
                df[f'{col}_rolling_mean_{ws}'] = (
                    df[col]
                    .rolling(window=ws)
                    .mean()
                    .astype(float)
                )

        df = df.dropna()
        numeric_check = df.apply(lambda s: pd.to_numeric(s, errors='coerce').notnull().all())
        if not numeric_check.all():
            non_numeric = numeric_check[~numeric_check].index.tolist()
            raise ValueError(f"非数值列残留: {non_numeric}")

        df = df.astype(float)
        self.feature_cols = [col for col in df.columns 
                            if col not in self.target_cols and df[col].dtype == float]
        return df

    def prepare_data(self, df):
        X = df[self.feature_cols].values
        y = df[self.target_cols].values

        train_size = len(df) - 30
        X_train, X_test = X[:train_size], X[train_size:]
        y_train, y_test = y[:train_size], y[train_size:]

        return X_train, X_test, y_train, y_test

    def build_model(self):
        base_model = GradientBoostingRegressor(
            n_estimators=100,
            learning_rate=0.1,
            max_depth=5,
            random_state=42
        )
        
        # 使用Pipeline整合预处理和模型
        self.model = Pipeline([
            ('scaler', StandardScaler()),
            ('regressor', MultiOutputRegressor(base_model))
        ])
        return self.model

    def train_model(self, X_train, y_train):
        self.X_train = X_train
        self.y_train = y_train
        self.model.fit(X_train, y_train)

    def evaluate_model(self, X_test, y_test):
        """增强后的评估方法"""
        print("\n=== 交叉验证结果 ===")
        try:
            # 5折交叉验证
            cv_scores = cross_val_score(
                self.model,
                self.X_train,
                self.y_train,
                cv=5,
                scoring='neg_mean_squared_error'
            )
            rmse_scores = np.sqrt(-cv_scores)
            print(f"交叉验证平均RMSE: {rmse_scores.mean():.2f} (±{rmse_scores.std():.2f})")
        except Exception as e:
            print(f"交叉验证时发生错误: {str(e)}")

        print("\n=== 测试集评估结果 ===")
        y_pred = self.model.predict(X_test)
        
        results = {}
        for i, col in enumerate(self.target_cols):
            mse = mean_squared_error(y_test[:, i], y_pred[:, i])
            rmse = np.sqrt(mse)
            mae = mean_absolute_error(y_test[:, i], y_pred[:, i])
            r2 = r2_score(y_test[:, i], y_pred[:, i])

            results[col] = {'MSE': mse, 'RMSE': rmse, 'MAE': mae, 'R2': r2}
            print(f"指标 {col}:")
            print(f"  MSE: {mse:.2f}, RMSE: {rmse:.2f}, MAE: {mae:.2f}, R2: {r2:.2f}")

        self._visualize_predictions(y_test, y_pred)
        return results

    def _visualize_predictions(self, y_test, y_pred):
        plt.figure(figsize=(12, 8))
        for i, col in enumerate(self.target_cols):
            plt.subplot(len(self.target_cols), 1, i + 1)
            plt.plot(y_test[:, i], label=f'实际{col}')
            plt.plot(y_pred[:, i], label=f'预测{col}')
            plt.title(f'{col}预测结果对比')
            plt.legend()
        plt.tight_layout()
        plt.savefig(os.path.join(self.model_path, 'prediction_visualization.png'))
        plt.close()

    def save_model(self, city_name):
        model_filename = os.path.join(self.model_path, f'{city_name}_weather_model.joblib')
        joblib.dump(self.model, model_filename)
        print(f"模型保存至 {model_filename}")

    def load_model(self, city_name):
        model_filename = os.path.join(self.model_path, f'{city_name}_weather_model.joblib')
        self.model = joblib.load(model_filename)
        print(f"从 {model_filename} 加载模型")

    def predict_future(self, city_name, days=None):
        if days is None:
            days = self.days_to_predict

        recent_data = self.load_data(city_name=city_name, end_date=datetime.now().strftime('%Y-%m-%d'))
        recent_data.index = pd.to_datetime(recent_data.index)

        processed_data = self.feature_engineering(recent_data)
        last_date = processed_data.index[-1].to_pydatetime()
        future_dates = [last_date + timedelta(days=i + 1) for i in range(days)]

        predictions = []
        current_data = processed_data.iloc[-1].copy()

        for future_date in future_dates:
            current_data['day_of_year'] = float(future_date.timetuple().tm_yday)
            current_data['day_of_week'] = float(future_date.weekday())
            current_data['month'] = float(future_date.month)

            X_pred = current_data[self.feature_cols].values.reshape(1, -1)
            y_pred = self.model.predict(X_pred)

            predictions.append({
                'date': future_date.strftime('%Y-%m-%d'),
                'temp_max': float(y_pred[0][0]),
                'temp_min': float(y_pred[0][1])
            })

            for lag in range(7, 1, -1):
                current_data[f'temp_max_lag_{lag}'] = current_data[f'temp_max_lag_{lag - 1}']
                current_data[f'temp_min_lag_{lag}'] = current_data[f'temp_min_lag_{lag - 1}']
            current_data['temp_max_lag_1'] = y_pred[0][0]
            current_data['temp_min_lag_1'] = y_pred[0][1]

        df_predictions = pd.DataFrame(predictions).astype({
            'date': 'str',
            'temp_max': 'float64',
            'temp_min': 'float64'
        })
        return df_predictions

    def run_full_pipeline(self, city_name, retrain=False):
        model_filename = os.path.join(self.model_path, f'{city_name}_weather_model.joblib')
        if retrain or not os.path.exists(model_filename):
            print(f"训练{city_name}的模型...")
            data = self.load_data(city_name)
            processed_data = self.feature_engineering(data)
            X_train, X_test, y_train, y_test = self.prepare_data(processed_data)
            self.build_model()
            self.train_model(X_train, y_train)
            self.evaluate_model(X_test, y_test)
            self.save_model(city_name)
        else:
            print(f"加载{city_name}的已有模型...")
            self.load_model(city_name)

        predictions = self.predict_future(city_name)
        print("未来天气预测结果:")
        print(predictions)
        return predictions
