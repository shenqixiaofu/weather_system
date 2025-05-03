# models/systemsetting_models.py

from models.weather_models import db
from werkzeug.security import generate_password_hash, check_password_hash


class SystemSetting(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    system_name = db.Column(db.String(64), default='天气数据管理系统')  # 系统名称
    records_per_page = db.Column(db.Integer, default=10)  # 每页显示记录数
    system_version = db.Column(db.String(10), default='1.1.5')  # 系统版本号,新增
    system_logo = db.Column(db.String(255))  # 系统 Logo 文件名
    enable_email_notifications = db.Column(db.Boolean, default=False)  # 是否启用邮件
    smtp_server = db.Column(db.String(128))  # 邮件服务器
    smtp_port = db.Column(db.Integer)  # 邮件端口
    sender_email = db.Column(db.String(128))  # 发送者邮箱
    smtp_password_hash = db.Column(db.String(128))  # 存储加密后的 SMTP 密码/授权码
    email_encryption = db.Column(db.String(20), default='none')  # 邮件加密方式

    auto_backup_enabled = db.Column(db.Boolean, default=False)  # 是否启用自动备份
    auto_backup_interval = db.Column(db.Integer, default=86400)  # 自动备份间隔（秒）

    # 用于设置和验证 SMTP 密码的属性
    @property
    def smtp_password(self):
        raise AttributeError('password is not a readable attribute')

    @smtp_password.setter
    def smtp_password(self, password):
        if password:  # 只有在提供了新密码时才更新
            self.smtp_password_hash = generate_password_hash(password)
        else:  # 如果密码为空，则清空密码哈希值
            self.smtp_password_hash = None

    def verify_password(self, password):
        if self.smtp_password_hash:
            return check_password_hash(self.smtp_password_hash, password)
        else:
            return False

