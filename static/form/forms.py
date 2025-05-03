# static/form/forms.py

from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, IntegerField, BooleanField, SelectField, FileField
from wtforms.validators import DataRequired, Length, Email, Optional, NumberRange
from wtforms.validators import Email, DataRequired  # 导入 Email 验证器


class SystemSettingsForm(FlaskForm):
    system_name = StringField('系统名称', validators=[DataRequired(), Length(1, 64)])
    records_per_page = IntegerField('每页显示记录数', validators=[DataRequired(), NumberRange(1, 100)])
    system_logo = FileField('系统 Logo')  # 文件上传字段
    submit = SubmitField('保存设置')


class EmailSettingsForm(FlaskForm):
    enable_email_notifications = BooleanField('启用邮件通知')
    smtp_server = StringField('SMTP 服务器', validators=[Optional(), Length(1, 128)])
    smtp_port = IntegerField('SMTP 端口', validators=[Optional(), NumberRange(1, 65535)])
    sender_email = StringField('Sender Email', validators=[Email()])  # 使用 Email 验证器
    smtp_password = PasswordField('发件人密码/授权码', validators=[Optional(), Length(1, 128)])  # 密码/授权码
    email_encryption = SelectField('加密方式', choices=[('none', '无'), ('ssl', 'SSL/TLS')], validators=[Optional()])
    submit = SubmitField('保存设置')


class DatabaseBackupForm(FlaskForm):
    backup_description = StringField('备份描述', validators=[Optional()])
    submit = SubmitField('立即备份')


class AutoBackupForm(FlaskForm):  # 自动备份
    auto_backup_enabled = BooleanField('启用自动备份')
    auto_backup_interval = IntegerField('备份间隔 (秒)', validators=[DataRequired(), NumberRange(min=60)],
                                        default=86400)  # 默认一天
    submit = SubmitField('保存设置')
