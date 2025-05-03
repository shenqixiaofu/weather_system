# models/weather_models.py

from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class WeatherData(db.Model):
    #实时天气
    id = db.Column(db.Integer, primary_key=True)
    city = db.Column(db.String(50), nullable=False)
    update_time = db.Column(db.DateTime)
    obs_time = db.Column(db.DateTime)
    temp = db.Column(db.Float)
    feels_like = db.Column(db.Float)
    humidity = db.Column(db.Float)
    wind_speed = db.Column(db.Float)
    wind_dir = db.Column(db.String(20))
    wind_scale = db.Column(db.String(10))
    precip = db.Column(db.Float)
    pressure = db.Column(db.Float)
    vis = db.Column(db.Float)
    cloud = db.Column(db.Float)
    dew = db.Column(db.Float)
    text = db.Column(db.String(50))
    icon = db.Column(db.String(10))

class HourlyForecast(db.Model):
    """未来24小时预报数据表"""
    id = db.Column(db.Integer, primary_key=True)
    city = db.Column(db.String(50), nullable=False)
    fx_time = db.Column(db.DateTime, nullable=False)       # 预报时间
    temp = db.Column(db.Float)                             # 温度，默认单位：摄氏度
    icon = db.Column(db.String(10))                        # 天气状况的图标代码
    text = db.Column(db.String(50))                        # 天气状况的文字描述
    wind360 = db.Column(db.Float)                          # 风向360角度
    wind_dir = db.Column(db.String(20))                    # 风向
    wind_scale = db.Column(db.String(10))                  # 风力等级
    wind_speed = db.Column(db.Float)                       # 风速，公里/小时
    humidity = db.Column(db.Float)                         # 相对湿度，百分比数值
    precip = db.Column(db.Float)                           # 当前小时累计降水量，毫米
    pop = db.Column(db.Float, nullable=True)               # 降水概率，百分比数值，可能为空
    pressure = db.Column(db.Float)                         # 大气压强，百帕
    cloud = db.Column(db.Float, nullable=True)             # 云量，百分比数值，可能为空
    dew = db.Column(db.Float, nullable=True)               # 露点温度，可能为空
    update_time = db.Column(db.DateTime, default=datetime.now)  # 数据更新时间


# 预报数据模型(通过api获取)
class WeatherForecast(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    city = db.Column(db.String(50), nullable=False)
    fx_date = db.Column(db.Date, nullable=False)  # 预报日期
    temp_max = db.Column(db.Float)  # 最高温度
    temp_min = db.Column(db.Float)  # 最低温度
    icon_day = db.Column(db.String(10))
    text_day = db.Column(db.String(50)) # 天气情况，包括阴晴雨雪等天气状态的描述
    wind_scale = db.Column(db.String(10))
    humidity = db.Column(db.Float)
    precip = db.Column(db.Float)
    update_time = db.Column(db.DateTime, default=datetime.now)



class RegionTemperature(db.Model):
    __tablename__ = 'region_temperatures'
    __table_args__ = (
        db.Index('idx_region_update', 'name', 'update_time'),  # 添加组合索引
    )
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), index=True)
    level = db.Column(db.String(10), default='province')  # 添加层级字段
    temp_avg = db.Column(db.Float, default=0)
    temp_max = db.Column(db.Float, default=0)
    temp_min = db.Column(db.Float, default=0)
    update_time = db.Column(db.DateTime, default=datetime.utcnow)


