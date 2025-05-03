# spider/data_cleaner.py
import os
import json
import pandas as pd
from sqlalchemy import Date, String, Float, Integer, create_engine, DateTime, text
from sqlalchemy.exc import SQLAlchemyError
from config import Config

class DataCleaner:
    def __init__(self):
        self.engine = create_engine(Config.SQLALCHEMY_DATABASE_URI)
        self.city_data = self.load_city_mapping()

    def load_city_mapping(self):
        """加载城市编码对照表"""
        try:
            current_dir = os.path.dirname(os.path.abspath(__file__))
            with open(os.path.join(current_dir, 'china.json'), 'r', encoding='utf-8') as f:
                cities = json.load(f)
            return {
                'code_to_name': {v: k for k, v in cities.items()},
                'valid_codes': list(cities.values())
            }
        except Exception as e:
            print(f"[错误] 加载城市编码文件失败: {str(e)}")
            raise

    def validate_cities(self, df):
        """执行城市编码验证"""
        # 存在性验证
        valid_codes = self.city_data['valid_codes']
        df_valid = df[df['city_code'].isin(valid_codes)].copy()
        # 一致性验证
        df_valid['expected_name'] = df_valid['city_code'].map(
            self.city_data['code_to_name'].get)
        df_valid = df_valid[df_valid['city_name'] == df_valid['expected_name']]
        return df_valid.drop(columns=['expected_name'])

    def clean_temperature(self, df):
        """温度数据处理"""
        # 格式转换
        df['temp_max'] = pd.to_numeric(df['temp_max'], errors='coerce')
        df['temp_min'] = pd.to_numeric(df['temp_min'], errors='coerce')
        # 异常值过滤（-50℃~50℃）
        condition = (
                df['temp_max'].between(-50, 50) &
                df['temp_min'].between(-50, 50) &
                (df['temp_max'] >= df['temp_min'])
        )
        return df[condition]

    def clean_dates(self, df):
        """日期处理"""
        df['date'] = pd.to_datetime(df['date'], format='%Y-%m-%d', errors='coerce')
        df = df.dropna(subset=['date'])
        df['year'] = df['date'].dt.year
        df['month'] = df['date'].dt.month
        return df

    def process_weather(self, df):
        """天气状况统一格式"""
        weather_map = {
            '晴转多云': '多云',
            '阴转小雨': '小雨',
            '雪转晴': '晴'
        }
        df['weather'] = df['weather'].replace(weather_map).fillna('其他')
        return df

    def execute_clean(self):
        """执行完整清洗流程"""
        try:
            # 从数据库读取原始数据
            df = pd.read_sql_table('historical_weather_v1', self.engine)

            # 执行清洗步骤
            df = self.clean_dates(df)
            df = self.clean_temperature(df)
            df = self.process_weather(df)

            # 最终去重
            df = df.sort_values(
                ['city_code', 'date', 'created_at'],
                ascending=[True, True, False]
            ).drop_duplicates(
                subset=['city_code', 'date'],
                keep='first'
            ).reset_index(drop=True)

            if 'id' in df.columns:
                df = df.drop(columns=['id'])

            # 使用事务处理删除和插入
            with self.engine.begin() as conn:  # 使用 begin 开启事务
                city_date_pairs = df[['city_code', 'date']].drop_duplicates()
                total_deleted = 0

                for _, row in city_date_pairs.iterrows():
                    city_code = row['city_code']
                    date = row['date']  # 直接使用 datetime.date 对象

                    delete_stmt = text("""
                        DELETE FROM cleaned_weather 
                        WHERE city_code = :city_code AND date = :date
                    """)
                    result = conn.execute(delete_stmt, {"city_code": city_code, "date": date})
                    total_deleted += result.rowcount

                # 在同一个事务中插入新记录
                df.to_sql('cleaned_weather',
                          conn,
                          if_exists='append',  # 如果表不存在，to_sql 会自动创建
                          index=False,
                          dtype={
                              'city_code': String(12),
                              'city_name': String(50),
                              'date': Date,
                              'temp_max': Float,
                              'temp_min': Float,
                              'weather': String(50),
                              'wind_dir': String(20),
                              'year': Integer,
                              'month': Integer,
                              'created_at': DateTime
                          })

                print(f"删除了 {total_deleted} 条旧记录")
                print(f"[成功] 清洗完成！更新记录：{len(df)}条")

        except SQLAlchemyError as e:
            print(f"[数据库错误] {str(e)}")
            # 发生异常时，事务会自动回滚，无需手动回滚
        except Exception as e:
            print(f"[系统错误] {str(e)}")
        finally:
            self.engine.dispose()

