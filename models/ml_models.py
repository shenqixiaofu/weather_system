# models/ml_models.py

from sqlalchemy import func
from models.weather_models import db

class ModelTrainingLog(db.Model):
    __tablename__ = 'model_training_logs'

    id = db.Column(db.Integer, primary_key=True)
    city_name = db.Column(db.String(50), unique=True, nullable=False, index=True)  # 城市名，唯一且索引
    trained_at = db.Column(db.DateTime, nullable=False, server_default=func.now(), onupdate=func.now()) #训练时间，自动更新
    model_version = db.Column(db.String(50))  # 模型版本
    metrics = db.Column(db.JSON)  # 评估指标 (JSON格式)

    def __repr__(self):
        return f"<ModelTrainingLog(city_name='{self.city_name}', trained_at='{self.trained_at}')>"