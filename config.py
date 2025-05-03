# config.py

class Config:
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://root:fumo666@localhost/weather_system_db'  # 修正键名并添加驱动
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    HEFENG_API_KEY = '59e29f64914f4ee88924671cfde4a4cc'
    SQLALCHEMY_ECHO = True  # 开启SQL日志
    SECRET_KEY = 'fumo'  # 随机生成，如：os.urandom(24)