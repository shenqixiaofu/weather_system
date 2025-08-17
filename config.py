# config.py

class Config:
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://root:fumo666@localhost/weather_system_db'
    # root为你的mysql用户名，fumo666为你的mysql密码，weather_system_db为你的数据库名

    SQLALCHEMY_TRACK_MODIFICATIONS = False
    HEFENG_API_KEY = '1145141919810baka'
    # 和风天气API密钥，可自行申请，链接：https://console.qweather.com/home?lang=zh

    SQLALCHEMY_ECHO = True  # 开启SQL日志
    SECRET_KEY = 'fumo'  # 随机生成，如：os.urandom(24)