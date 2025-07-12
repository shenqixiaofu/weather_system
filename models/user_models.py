# models/user_models.py

from models.weather_models import db
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from sqlalchemy.orm import relationship


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)

    # 个人资料信息
    email = db.Column(db.String(100), unique=True)
    phone = db.Column(db.String(20))
    bio = db.Column(db.String(200))
    location = db.Column(db.String(50))
    occupation = db.Column(db.String(50))
    avatar_file = db.Column(db.String(255), default='default-avatar.png')

    # 偏好设置
    default_city = db.Column(db.String(50))
    theme = db.Column(db.String(20), default='light')

    # 通知设置
    email_weather_alerts = db.Column(db.Boolean, default=True)
    email_weekly_report = db.Column(db.Boolean, default=True)
    email_system_updates = db.Column(db.Boolean, default=False)
    app_weather_alerts = db.Column(db.Boolean, default=True)
    app_data_updates = db.Column(db.Boolean, default=True)

    # 管理员权限
    is_admin = db.Column(db.Boolean, default=False)

    # 安全设置
    two_factor_enabled = db.Column(db.Boolean, default=False)

    # 时间戳
    register_date = db.Column(db.DateTime, default=datetime.now)
    last_login = db.Column(db.DateTime)
    profile_updated_at = db.Column(db.DateTime)
    password_updated_at = db.Column(db.DateTime)

    # 关系映射
    favorites = relationship('FavoriteLocation', backref='user', lazy=True, cascade='all, delete-orphan')
    activities = relationship('UserActivity', backref='user', lazy=True, cascade='all, delete-orphan')
    search_history = relationship('SearchHistory', backref='user', lazy=True, cascade='all, delete-orphan')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
        self.password_updated_at = datetime.now()

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def update_last_login(self):
        self.last_login = datetime.now()
        db.session.commit()


# 用户收藏的位置
class FavoriteLocation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='CASCADE'), nullable=False)
    name = db.Column(db.String(50), nullable=False)
    added_on = db.Column(db.DateTime, default=datetime.now)


# 用户活动记录
class UserActivity(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='CASCADE'), nullable=False)
    activity_type = db.Column(db.String(50), nullable=False)  # search, view, favorite, etc.
    description = db.Column(db.String(200))
    icon = db.Column(db.String(50))  # FontAwesome icon class
    timestamp = db.Column(db.DateTime, default=datetime.now)
    related_data = db.Column(db.String(100))  # city name, data type, etc.


# 搜索历史
class SearchHistory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='CASCADE'), nullable=False)
    search_query = db.Column(db.String(100), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.now)