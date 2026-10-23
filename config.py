# config.py
#
# 所有敏感配置都从环境变量读取，代码里不再写死密码与密钥。
# 启动前先设好环境变量，例如：
#   export DB_PASSWORD=你的mysql密码
#   export HEFENG_API_KEY=你的和风天气密钥
# 需要哪些变量见 .env.example。

import os

# 数据库连接：优先用 DATABASE_URL 整串覆盖，否则按下面四项拼
DB_USER = os.environ.get('DB_USER', 'root')
DB_PASSWORD = os.environ.get('DB_PASSWORD', '')
DB_HOST = os.environ.get('DB_HOST', 'localhost')
DB_NAME = os.environ.get('DB_NAME', 'weather_system_db')


class Config:
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        'DATABASE_URL',
        f'mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}/{DB_NAME}',
    )
    # 也可以用 DATABASE_URL 一次性给整串：mysql+pymysql://用户:密码@主机/库名

    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # 和风天气 API 密钥，申请地址：https://console.qweather.com
    HEFENG_API_KEY = os.environ.get('HEFENG_API_KEY', '')

    # 设为 1 才会把每条 SQL 打到控制台，默认关闭
    SQLALCHEMY_ECHO = os.environ.get('SQLALCHEMY_ECHO', '0') == '1'

    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-secret-change-me')

    # 备份 / 恢复走 mysqldump 命令行，密码得单独传，与 DB_PASSWORD 同源
    MYSQL_PASSWORD = DB_PASSWORD
    # 这三项必须和上面的连接串同源，否则备份会 dump 到另一个库
    MYSQL_USER = DB_USER
    MYSQL_DB = DB_NAME
    MYSQL_HOST = DB_HOST
