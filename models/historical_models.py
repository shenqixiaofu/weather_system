# models/historical_models.py

from datetime import datetime
from models.weather_models import db

class HistoricalWeather(db.Model):
    __tablename__ = 'historical_weather'  # 更新表版本
    id = db.Column(db.Integer, primary_key=True)
    city_code = db.Column(db.String(12), nullable=False, index=True)
    city_name = db.Column(db.String(50), nullable=False, index=True)
    date = db.Column(db.Date, nullable=False, index=True)
    temp_max = db.Column(db.Float)
    temp_min = db.Column(db.Float)
    weather = db.Column(db.String(50))
    wind_dir = db.Column(db.String(20))     #风向
    created_at = db.Column(db.DateTime, default=datetime.now)

# 新建一个表来存放新爬到的数据
class NewHistoricalWeather(db.Model):
    __tablename__ = 'historical_weather_v1'  # 更新表版本
    id = db.Column(db.Integer, primary_key=True)
    city_code = db.Column(db.String(12), nullable=False, index=True)
    city_name = db.Column(db.String(50), nullable=False, index=True)
    date = db.Column(db.Date, nullable=False, index=True)
    temp_max = db.Column(db.Float)
    temp_min = db.Column(db.Float)
    weather = db.Column(db.String(50))
    wind_dir = db.Column(db.String(20))     #风向
    created_at = db.Column(db.DateTime, default=datetime.now)