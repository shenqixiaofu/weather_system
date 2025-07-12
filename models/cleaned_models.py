# models/cleaned_models.py

from datetime import datetime
from models.weather_models import db

class CleanedHistoricalWeather(db.Model):
    __tablename__ = 'cleaned_weather'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    city_code = db.Column(db.String(12))
    city_name = db.Column(db.String(50))  # 城市名
    date = db.Column(db.Date)             # 日期
    temp_max = db.Column(db.Float)        # 最高温
    temp_min = db.Column(db.Float)        # 最低温
    weather = db.Column(db.String(50))    # 天气状况
    wind_dir = db.Column(db.String(20))
    year = db.Column(db.Integer)
    month = db.Column(db.Integer)
    created_at = db.Column(db.DateTime, default=datetime.now)

    def __repr__(self):
        return f'<City {self.city_name} {self.date}>'
