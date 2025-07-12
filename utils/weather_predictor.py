# utils/weather_predictor.py

import pandas as pd
import numpy as np
import joblib
import os
import matplotlib.pyplot as plt
import pickle
from datetime import datetime, timedelta
from matplotlib import rcParams
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
        """
        天气预测器初始化
        Args:
            days_to_predict: 默认预测天数（5天）
            model_path: 模型存储路径
        """
        # 添加中文字体配置
        rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei']  # 设置支持中文的字体
        rcParams['axes.unicode_minus'] = False  # 解决负号显示问题
        self.days_to_predict = days_to_predict
        self.model_path = model_path
        self.feature_cols = None
        self.target_cols = ['temp_max', 'temp_min']
        self.model = None
        self.engine = create_engine(Config.SQLALCHEMY_DATABASE_URI)
        self.X_train = None  # 训练数据存储
        self.y_train = None

        os.makedirs(self.model_path, exist_ok=True)

    def load_data(self, city_name, start_date=None, end_date=None):
        """
        从数据库加载指定城市的历史天气数据
        Args:
            city_name: 城市名称 
            start_date: 数据开始日期（可选）
            end_date: 数据结束日期（可选）
        Returns:
            pandas.DataFrame: 包含温度数据的数据框
        """
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
        """
        特征工程处理（机器学习流程核心部分）
        处理步骤：
        1. 清理非数值数据
        2. 添加时间特征
        3. 创建滞后特征
        4. 生成滚动统计特征
        5. 添加温度变化率特征
        6. 异常值处理
        7. 特征选择
        """
        # 补齐日期缺失，保证数据连续
        if 'date' in df.columns:
            df['date'] = pd.to_datetime(df['date'], errors='coerce')
            df = df.dropna(subset=['date'])
            df = df.sort_values('date')
            # 生成完整日期序列
            full_range = pd.date_range(df['date'].min(), df['date'].max(), freq='D')
            df = df.set_index('date').reindex(full_range).reset_index()
            df = df.rename(columns={'index': 'date'})

        non_numeric_cols = ['city_code', 'city_name', 'weather', 'wind_dir']
        df = df.drop(columns=non_numeric_cols, errors='ignore')

        df['date'] = pd.to_datetime(df['date'], errors='coerce')
        df = df.dropna(subset=['date'])
        df.set_index('date', inplace=True)

        # 异常值处理
        for col in ['temp_max', 'temp_min']:
            # 使用3倍标准差作为异常值界限
            mean = df[col].mean()
            std = df[col].std()
            df[col] = df[col].clip(lower=mean - 3*std, upper=mean + 3*std)

        # 日期特征生成
        df['day_of_year'] = df.index.dayofyear.astype(float)
        df['day_of_week'] = df.index.dayofweek.astype(float)
        df['month'] = df.index.month.astype(float)
        df['season'] = (df.index.month % 12 + 3) // 3
        df['is_weekend'] = df['day_of_week'].isin([5, 6]).astype(float)

        # 滞后特征创建（只使用最近3天的数据）
        for i in range(1, 4):
            df[f'temp_max_lag_{i}'] = df['temp_max'].shift(i).astype(float)
            df[f'temp_min_lag_{i}'] = df['temp_min'].shift(i).astype(float)

        # 温度变化率特征
        df['temp_max_change'] = df['temp_max'].diff().astype(float)
        df['temp_min_change'] = df['temp_min'].diff().astype(float)

        # 滚动统计特征（只使用7天窗口）
        window_size = 7
        for col in ['temp_max', 'temp_min']:
            df[f'{col}_rolling_mean_{window_size}'] = df[col].rolling(window=window_size).mean().astype(float)
            df[f'{col}_rolling_std_{window_size}'] = df[col].rolling(window=window_size).std().astype(float)

        # 温度范围特征
        df['temp_range'] = (df['temp_max'] - df['temp_min']).astype(float)
        df['temp_range_rolling_mean_7'] = df['temp_range'].rolling(window=7).mean().astype(float)

        df = df.dropna()
        numeric_check = df.apply(lambda s: pd.to_numeric(s, errors='coerce').notnull().all())
        if not numeric_check.all():
            non_numeric = numeric_check[~numeric_check].index.tolist()
            raise ValueError(f"非数值列残留: {non_numeric}")

        df = df.astype(float)
        self.feature_cols = [col for col in df.columns 
                            if col not in self.target_cols and df[col].dtype == float]
        
        print(f"特征数量: {len(self.feature_cols)}")
        print(f"特征列表: {self.feature_cols}")
        return df

    def prepare_data(self, df):
        """
        准备训练和测试数据
        - 使用80%的数据作为训练集
        - 使用20%的数据作为测试集
        - 保持时间序列的连续性
        """
        X = df[self.feature_cols].values
        y = df[self.target_cols].values

        # 使用80%的数据作为训练集
        train_size = int(len(df) * 0.8)
        X_train, X_test = X[:train_size], X[train_size:]
        y_train, y_test = y[:train_size], y[train_size:]

        print(f"训练集大小: {len(X_train)}, 测试集大小: {len(X_test)}")
        return X_train, X_test, y_train, y_test

    def build_model(self):
        """
        构建机器学习管道：
        1. 标准化特征
        2. 多输出梯度提升回归
        """
        base_model = GradientBoostingRegressor(
            n_estimators=300,  # 树的数量
            learning_rate=0.03,  # 学习率
            max_depth=6,  # 树的最大深度
            min_samples_split=10,  # 分裂节点所需的最小样本数
            min_samples_leaf=5,  # 叶节点所需的最小样本数
            subsample=0.8,  # 每棵树使用的样本比例
            max_features='sqrt',  # 每次分裂考虑的特征数
            random_state=42 # 随机种子，确保结果可复现
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
        """评估方法"""
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
        # 保存特征名
        feature_file = os.path.join(self.model_path, f'{city_name}_features.pkl')
        with open(feature_file, 'wb') as f:
            pickle.dump(self.feature_cols, f)
        print(f"模型和特征保存至 {model_filename} 和 {feature_file}")

    def load_model(self, city_name):
        model_filename = os.path.join(self.model_path, f'{city_name}_weather_model.joblib')
        self.model = joblib.load(model_filename)
        # 加载特征名
        feature_file = os.path.join(self.model_path, f'{city_name}_features.pkl')
        with open(feature_file, 'rb') as f:
            self.feature_cols = pickle.load(f)
        print(f"从 {model_filename} 和 {feature_file} 加载模型和特征")

    def predict_future(self, city_name, days=None):
        """
        递归式多步预测策略
        多步预测流程：
        1. 加载最新数据
        2. 生成未来日期序列
        3. 迭代预测（使用前一天预测结果更新特征）
        4. 维护特征窗口（滞后特征滚动更新）
        """
        if days is None:
            days = self.days_to_predict

        recent_data = self.load_data(city_name=city_name, end_date=datetime.now().strftime('%Y-%m-%d'))
        recent_data['date'] = pd.to_datetime(recent_data['date'])
        max_date = recent_data['date'].max()  # 用原始数据的最大日期作为预测起点

        processed_data = self.feature_engineering(recent_data)
        last_date = max_date.to_pydatetime()  
        future_dates = [last_date + timedelta(days=i + 1) for i in range(days)]

        predictions = []
        if max_date in processed_data.index:
            current_data = processed_data.loc[max_date].copy()
        else:
            current_data = processed_data.iloc[-1].copy()

        for future_date in future_dates:
            current_data['day_of_year'] = float(future_date.timetuple().tm_yday)
            current_data['day_of_week'] = float(future_date.weekday())
            current_data['month'] = float(future_date.month)
            current_data['season'] = float((future_date.month % 12 + 3) // 3)
            current_data['is_weekend'] = float(future_date.weekday() in [5, 6])

            pred_features = {}
            for col in self.feature_cols:
                pred_features[col] = current_data[col] if col in current_data else np.nan
            X_pred = np.array([list(pred_features.values())])
            y_pred = self.model.predict(X_pred)

            predictions.append({
                'date': future_date.strftime('%Y-%m-%d'),
                'temp_max': float(y_pred[0][0]),
                'temp_min': float(y_pred[0][1])
            })

            for lag in range(3, 1, -1):
                current_data[f'temp_max_lag_{lag}'] = current_data[f'temp_max_lag_{lag - 1}']
                current_data[f'temp_min_lag_{lag}'] = current_data[f'temp_min_lag_{lag - 1}']
            current_data['temp_max_lag_1'] = y_pred[0][0]
            current_data['temp_min_lag_1'] = y_pred[0][1]

            current_data['temp_max_change'] = y_pred[0][0] - current_data['temp_max_lag_1']
            current_data['temp_min_change'] = y_pred[0][1] - current_data['temp_min_lag_1']

            current_data['temp_range'] = y_pred[0][0] - y_pred[0][1]

        df_predictions = pd.DataFrame(predictions).astype({
            'date': 'str',
            'temp_max': 'float64',
            'temp_min': 'float64'
        })
        return df_predictions

    def run_full_pipeline(self, city_name, retrain=False):
        """
        完整预测流水线：
        1. 模型检查（根据retrain标志决定是否重新训练）
        2. 数据预处理（加载 -> 特征工程 -> 分割数据集）
        3. 模型训练与评估
        4. 未来温度预测
        """
        model_filename = os.path.join(self.model_path, f'{city_name}_weather_model.joblib')
        feature_file = os.path.join(self.model_path, f'{city_name}_features.pkl')
        eval_results = None

        try:
            # 加载数据（无论是否重新训练都需要用于评估）
            data = self.load_data(city_name)
            processed_data = self.feature_engineering(data)
            X_train, X_test, y_train, y_test = self.prepare_data(processed_data)

            # 检查是否需要训练模型（模型或特征文件不存在也要训练）
            if retrain or not (os.path.exists(model_filename) and os.path.exists(feature_file)):
                print(f"正在为{city_name}训练新模型...")
                # 构建并训练模型
                self.build_model()
                self.train_model(X_train, y_train)
                # 保存模型和特征
                self.save_model(city_name)
                print(f"模型已保存到 {model_filename} 和 {feature_file}")
            else:
                # 加载现有模型和特征
                print(f"正在加载{city_name}的现有模型...")
                self.load_model(city_name)

            # 评估模型性能
            eval_results = self.evaluate_model(X_test, y_test)
            # 预测未来天气
            predictions = self.predict_future(city_name)

            # 计算MAE和RMSE（对temp_max和temp_min分别取平均）
            mae_list = []
            rmse_list = []
            for col in self.target_cols:
                if col in eval_results:
                    mae_list.append(eval_results[col]['MAE'])
                    rmse_list.append(eval_results[col]['RMSE'])
            mae = float(np.mean(mae_list)) if mae_list else None
            rmse = float(np.mean(rmse_list)) if rmse_list else None
            metrics = {'mae': mae, 'rmse': rmse}

            return predictions, metrics
        except Exception as e:
            print(f"运行预测流水线时出错: {str(e)}")
            raise

    def analyze_weather_trends(self, city_name):
        """
        分析天气趋势
        包括：
        1. 温度长期趋势（自适应按年、月、天聚合）
        2. 季节性变化
        3. 极端天气事件
        4. 温度变化率分析
        """
        data = self.load_data(city_name)
        data['date'] = pd.to_datetime(data['date'])
        data.set_index('date', inplace=True)
        days_span = (data.index.max() - data.index.min()).days

        # 自动选择聚合粒度
        if days_span > 700:
            group = data.groupby(data.index.year)
            x_label = 'year'
        elif days_span > 60:
            group = data.groupby([data.index.year, data.index.month])
            x_label = 'month'
        else:
            group = data.groupby(data.index.date)
            x_label = 'day'

        max_temp = group['temp_max'].mean()
        min_temp = group['temp_min'].mean()

        # 组装x轴
        if x_label == 'year':
            x = [str(y) for y in max_temp.index]
        elif x_label == 'month':
            x = [f'{y[0]}-{y[1]:02d}' for y in max_temp.index]
        else:
            x = [str(d) for d in max_temp.index]

        # 计算月度平均温度
        monthly_avg = data.groupby(data.index.month)[['temp_max', 'temp_min']].mean()
        # 计算年度趋势
        yearly_avg = data.groupby(data.index.year)[['temp_max', 'temp_min']].mean()
        # 计算温度变化率
        data['temp_max_change'] = data['temp_max'].diff()
        data['temp_min_change'] = data['temp_min'].diff()
        # 检测异常值（使用3倍标准差）
        max_temp_mean = data['temp_max'].mean()
        max_temp_std = data['temp_max'].std()
        min_temp_mean = data['temp_min'].mean()
        min_temp_std = data['temp_min'].std()
        anomalies = data[
            (data['temp_max'] > max_temp_mean + 3*max_temp_std) |
            (data['temp_max'] < max_temp_mean - 3*max_temp_std) |
            (data['temp_min'] > min_temp_mean + 3*min_temp_std) |
            (data['temp_min'] < min_temp_mean - 3*min_temp_std)
        ]
        analysis_results = {
            'monthly_stats': {
                'max_temp': monthly_avg['temp_max'].to_dict(),
                'min_temp': monthly_avg['temp_min'].to_dict()
            },
            'yearly_trend': {
                'max_temp': yearly_avg['temp_max'].to_dict(),
                'min_temp': yearly_avg['temp_min'].to_dict()
            },
            'trend_x': x,
            'trend_max_temp': max_temp.tolist(),
            'trend_min_temp': min_temp.tolist(),
            'anomalies': {
                'dates': anomalies.index.strftime('%Y-%m-%d').tolist(),
                'max_temps': anomalies['temp_max'].tolist(),
                'min_temps': anomalies['temp_min'].tolist()
            },
            'summary_stats': {
                'max_temp_mean': float(max_temp_mean),
                'max_temp_std': float(max_temp_std),
                'min_temp_mean': float(min_temp_mean),
                'min_temp_std': float(min_temp_std),
                'max_temp_change_mean': float(data['temp_max_change'].mean()),
                'min_temp_change_mean': float(data['temp_min_change'].mean())
            }
        }
        return analysis_results

    def analyze_seasonal_patterns(self, city_name):
        """
        分析季节性模式
        包括：
        1. 季节性温度变化
        2. 季节转换特征
        3. 季节性异常检测
        """
        data = self.load_data(city_name)
        data['date'] = pd.to_datetime(data['date'])
        data.set_index('date', inplace=True)
        # 添加季节信息
        data['season'] = (data.index.month % 12 + 3) // 3
        # 计算每个季节的统计信息
        seasonal_stats = data.groupby('season').agg({
            'temp_max': ['mean', 'std', 'min', 'max'],
            'temp_min': ['mean', 'std', 'min', 'max']
        })
        # 扁平化列名
        seasonal_stats.columns = ['_'.join(col) for col in seasonal_stats.columns]
        seasonal_stats = seasonal_stats.to_dict(orient='index')
        # 重新组织成前端需要的结构
        result = {
            'max_temp': {'mean': {}, 'std': {}, 'min': {}, 'max': {}},
            'min_temp': {'mean': {}, 'std': {}, 'min': {}, 'max': {}},
            'range': {}  # 每个季节的平均日温差
        }
        for season, stats in seasonal_stats.items():
            result['max_temp']['mean'][season] = stats['temp_max_mean']
            result['max_temp']['std'][season] = stats['temp_max_std']
            result['max_temp']['min'][season] = stats['temp_max_min']
            result['max_temp']['max'][season] = stats['temp_max_max']
            result['min_temp']['mean'][season] = stats['temp_min_mean']
            result['min_temp']['std'][season] = stats['temp_min_std']
            result['min_temp']['min'][season] = stats['temp_min_min']
            result['min_temp']['max'][season] = stats['temp_min_max']
        # 计算每个季节的平均日温差
        for season, group in data.groupby('season'):
            daily_range = (group['temp_max'] - group['temp_min']).mean()
            result['range'][season] = float(daily_range)
        # 季节转换特征保持不变
        season_transitions = []
        for year in data.index.year.unique():
            year_data = data[data.index.year == year]
            for season in range(1, 5):
                season_data = year_data[year_data['season'] == season]
                if not season_data.empty:
                    season_transitions.append({
                        'year': year,
                        'season': season,
                        'max_temp_mean': float(season_data['temp_max'].mean()),
                        'min_temp_mean': float(season_data['temp_min'].mean()),
                        'temp_range_mean': float((season_data['temp_max'] - season_data['temp_min']).mean())
                    })
        return {
            'seasonal_stats': result,
            'season_transitions': season_transitions
        }

    def analyze_weather_patterns(self, city_name):
        """
        分析天气模式
        包括：
        1. 温度范围分析
        2. 日温差分析
        3. 天气变化频率
        """
        data = self.load_data(city_name)
        data['date'] = pd.to_datetime(data['date'])
        data.set_index('date', inplace=True)
        
        # 计算日温差
        data['daily_temp_range'] = data['temp_max'] - data['temp_min']
        
        # 计算温度范围分布
        temp_range_stats = {
            'mean': float(data['daily_temp_range'].mean()),
            'std': float(data['daily_temp_range'].std()),
            'min': float(data['daily_temp_range'].min()),
            'max': float(data['daily_temp_range'].max())
        }
        
        # 分析温度变化趋势
        data['temp_max_change'] = data['temp_max'].diff()
        data['temp_min_change'] = data['temp_min'].diff()
        
        # 计算温度变化频率
        change_frequency = {
            'max_temp_increase': len(data[data['temp_max_change'] > 0]),
            'max_temp_decrease': len(data[data['temp_max_change'] < 0]),
            'min_temp_increase': len(data[data['temp_min_change'] > 0]),
            'min_temp_decrease': len(data[data['temp_min_change'] < 0])
        }
        
        return {
            'temp_range_stats': temp_range_stats,
            'change_frequency': change_frequency,
            'daily_patterns': {
                'max_temp_mean': float(data['temp_max'].mean()),
                'min_temp_mean': float(data['temp_min'].mean()),
                'temp_range_mean': float(data['daily_temp_range'].mean())
            }
        }

    def generate_analysis_report(self, city_name):
        """
        生成综合分析报告
        整合所有分析结果
        """
        trends = self.analyze_weather_trends(city_name)
        seasonal = self.analyze_seasonal_patterns(city_name)
        patterns = self.analyze_weather_patterns(city_name)
        
        report = {
            'city_name': city_name,
            'analysis_date': datetime.now().strftime('%Y-%m-%d'),
            'trends': trends,
            'seasonal_patterns': seasonal,
            'weather_patterns': patterns,
            'summary': {
                'temperature_trend': '上升' if trends['yearly_trend']['max_temp'][list(trends['yearly_trend']['max_temp'].keys())[-1]] > 
                                    trends['yearly_trend']['max_temp'][list(trends['yearly_trend']['max_temp'].keys())[0]] else '下降',
                'anomaly_count': len(trends['anomalies']['dates']),
                'avg_temp_range': patterns['temp_range_stats']['mean'],
                'most_volatile_season': max(seasonal['seasonal_stats']['max_temp']['std'].items(), 
                                          key=lambda x: x[1])[0]
            }
        }
        
        return report
