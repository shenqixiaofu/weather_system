# app.py

import json
import math
import os
import secrets
import shutil
import time
from collections import Counter
import re
import numpy as np
import pandas as pd
import logging
import subprocess
from functools import wraps
from PIL import Image
from apscheduler.schedulers.background import BackgroundScheduler
from flask import jsonify, send_from_directory, session, Response, stream_with_context, make_response
from logging.handlers import RotatingFileHandler
from flask import send_file
from flask_login import current_user
from sqlalchemy import case, func, or_
from werkzeug.utils import secure_filename
from models.systemsetting_models import SystemSetting
from models.cleaned_models import CleanedHistoricalWeather
from models.user_models import User, UserActivity, FavoriteLocation, SearchHistory
from models.feedback_models import Feedback
from models.weather_models import db, WeatherData, WeatherForecast, HourlyForecast, RegionTemperature
from models.historical_models import HistoricalWeather
from config import Config
from models.systemsetting_models import SystemSetting
from spider.province_data import province_data
from spider.weather_spider import batch_crawl, CITY_INFO
from static.form.forms import SystemSettingsForm, EmailSettingsForm, DatabaseBackupForm, AutoBackupForm
from utils import weather_province_api
from utils.weather_api import fetch_weather_forecast, get_hourly_forecast, get_location_id, get_current_weather_data
from datetime import datetime, timedelta
from flask_migrate import Migrate
from flask import Flask, render_template, redirect, url_for, flash, request
from flask_login import LoginManager, login_user, logout_user, login_required
from utils.weather_api import reverse_geocode_api
from utils.weather_province_api import fetch_all_provinces_weather
from utils.weather_predictor import WeatherPredictor
from apscheduler.triggers.interval import IntervalTrigger
from flask import Flask, request, current_app
from flask_babel import Babel
import uuid
import sys
import platform
import psutil


app = Flask(__name__, static_folder='static')
app.config.from_object(Config)
db.init_app(app)
migrate = Migrate(app, db)
app.config['SECRET_KEY'] = 'fumo'
babel = Babel(app)

# 初始化登录管理
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# 配置日志系统
log_folder = 'logs'
if not os.path.exists(log_folder):
    os.makedirs(log_folder)
log_file = os.path.join(log_folder, 'app.log')
handler = RotatingFileHandler(log_file, maxBytes=10240, backupCount=5, delay=True)
handler.setFormatter(logging.Formatter(
    '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
))
handler.setLevel(logging.INFO)
app.logger.addHandler(handler)
app.logger.setLevel(logging.INFO)
app.logger.info('天气系统启动')

# 添加日志记录装饰器
def log_operation(operation_type):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            try:
                result = f(*args, **kwargs)
                app.logger.info(f'[{operation_type}] 操作成功: {f.__name__}')
                return result
            except Exception as e:
                app.logger.error(f'[{operation_type}] 操作失败: {f.__name__}, 错误: {str(e)}')
                raise
        return decorated_function
    return decorator

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


# 在登录路由中添加CSRF保护
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # 获取并清理输入
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        remember = 'remember' in request.form

        if not username or not password:
            app.logger.warning(f'登录失败: 用户名或密码为空')
            flash('用户名和密码不能为空', 'error')
            return render_template('login.html')

        user = User.query.filter_by(username=username).first()

        if user and user.check_password(password):
            login_user(user, remember=remember)
            app.logger.info(f'用户登录成功: {username}')
            next_page = request.args.get('next')
            flash('登录成功', 'success')
            return redirect(next_page or url_for('index'))
        else:
            app.logger.warning(f'登录失败: 用户名或密码错误 - {username}')
            flash('用户名或密码错误', 'error')
            return render_template('login.html', username=username)

    # GET请求显示页面
    return render_template('login.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        if User.query.filter_by(username=username).first():
            app.logger.warning(f'注册失败: 用户名已存在 - {username}')
            flash(f'用户名 "{username}" 已被注册，请使用其他用户名', 'error')
            return redirect(url_for('register'))
        if request.form['password'] != request.form['confirm_password']:
            app.logger.warning(f'注册失败: 密码不匹配 - {username}')
            flash('两次输入的密码不匹配')
            return redirect(url_for('register'))

        try:
            new_user = User(
                username=username,
                    register_date=datetime.now()
            )
            new_user.set_password(password)

            db.session.add(new_user)
            db.session.commit()
            app.logger.info(f'新用户注册成功: {username}')

            login_user(new_user)
            return redirect(url_for('index'))
        except Exception as e:
            app.logger.error(f'注册失败: {str(e)}')
            db.session.rollback()
            flash('注册失败，请稍后重试')
            return redirect(url_for('register'))
    return render_template('register.html')


@app.route('/logout')
@login_required
def logout():
    # 获取响应对象
    response = make_response(redirect(url_for('index')))
    
    # 清除用户相关的cookie
    response.delete_cookie('lastSearchedCity')
    response.delete_cookie('locatedCity')
    response.delete_cookie('hasLocated')
    
    # 先保存用户名
    username = current_user.username
    
    # 执行登出操作
    logout_user()
    app.logger.info(f'用户退出登录: {username}')
    flash('您已成功退出登录', 'success')
    
    return response


"""@app.cli.command("rebuild-db")
def rebuild_database_command():
    with app.app_context():
        db.drop_all()
        db.create_all()
        print("数据库已重建。")"""


# 强制重建数据库（仅开发时使用）
# with app.app_context():
#     db.drop_all()
#     db.create_all()

# 添加favicon路由
@app.route('/favicon.ico')
def favicon():
    settings = SystemSetting.query.first()
    response = None
    if settings and settings.system_logo:
        response = send_from_directory('static/images/logos', settings.system_logo)
    else:
        response = send_from_directory('static/images/favicons', 'favicon.ico')
    
    # 添加缓存控制头
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    return response


@app.route('/')
def index():
    user_theme = request.cookies.get('user_theme', 'light')
    default_city_data = None
    default_city_name = None

    if current_user.is_authenticated and current_user.default_city:
        default_city_name = current_user.default_city
        try:
            # 获取城市ID和中文名 (复用 get_location_id 函数)
            location_id, city_cn = get_location_id(default_city_name)
            if location_id and city_cn:
                # 获取实时天气数据 (复用逻辑, 但不直接调用函数)
                current_weather = get_current_weather_data(default_city_name)  # 获取实时数据

                # 获取24小时预报 (复用逻辑, 但不直接调用函数)
                hourly_data = get_hourly_forecast(default_city_name)

                # 获取预报数据 (复用逻辑, 但不直接调用函数)
                forecast_data = fetch_weather_forecast(default_city_name)

                # 将数据组合成一个字典，方便传递
                default_city_data = {
                    'current_weather': current_weather,
                    'hourly_data': hourly_data,
                    'forecast_data': forecast_data,
                    'city_cn': city_cn  # 确保 city_cn 也被传递
                }

        except Exception as e:
            db.session.rollback()
            #  处理错误，例如可以记录日志，但不要中断页面渲染
            print(f"Error fetching default city data: {e}")

    return render_template('index.html', user_theme=user_theme,
                           default_city=default_city_name,
                           default_city_data=default_city_data)


@app.route('/get_weather/<city>')
def fetch_weather(city):
    with app.app_context():
        if city == "None":
            return jsonify({'status': 'error', 'message': '城市名称无效'}), 400  # 使用 400 Bad Request
        try:
            # 获取城市ID和中文名
            location_id, city_cn = get_location_id(city)
            if not location_id or not city_cn:
                return jsonify({'status': 'error', 'message': '城市不存在'})

            # 检查并获取/更新实时天气数据
            current_weather = get_current_weather_data(city)  # 直接调用，包含缓存逻辑

            # 检查并获取/更新24小时预报
            hourly_data = get_hourly_forecast(city)

            # 检查并获取/更新预报数据
            forecast_data = fetch_weather_forecast(city)

            # 保存数据
            if hourly_data:
                HourlyForecast.query.filter_by(city=city_cn).delete()
                for hour in hourly_data:
                    record = HourlyForecast(city=city_cn, **hour)
                    db.session.add(record)
            if forecast_data:
                WeatherForecast.query.filter_by(city=city_cn).delete()
                for day_data in forecast_data:
                    forecast = WeatherForecast(city=city_cn, **day_data)
                    db.session.add(forecast)
            if current_weather:
                WeatherData.query.filter_by(city=city_cn).delete()
                weather_record = WeatherData(**current_weather)
                db.session.add(weather_record)
            db.session.commit()

            return jsonify({'status': 'success', 'city_cn': city_cn})

        except Exception as e:
            db.session.rollback()
            return jsonify({'status': 'error', 'message': str(e)})


@app.route('/check_login')
def check_login():
    """检查用户登录状态的 API"""
    return jsonify({'isLoggedIn': current_user.is_authenticated})


@app.route('/hourly_data/<city>')
def get_hourly_weather(city):
    """获取存储的24小时数据, 优先从数据库读取"""
    try:
        # 记录请求信息
        print(f"接收到城市 {city} 的小时天气数据请求")

        # 尝试从数据库获取
        records = HourlyForecast.query.filter_by(city=city).order_by(HourlyForecast.fx_time).limit(24).all()

        if records:
            # 检查数据是否是最新的（1小时内）
            most_recent_update = records[0].update_time if records else None
            if most_recent_update and (datetime.now() - most_recent_update) < timedelta(hours=1):
                print(f"从数据库获取城市 {city} 的小时天气数据")
                # 构建响应数据... (与之前版本相同)
                response_data = {
                    'times': [r.fx_time.strftime('%H:%M') for r in records],
                    'temps': [float(r.temp) for r in records],
                    'humidity': [float(r.humidity) for r in records],
                    'wind_speed': [float(r.wind_speed) for r in records],
                    'wind_dir': [r.wind_dir for r in records],
                    'text': [r.text for r in records],
                    'icon': [r.icon for r in records],
                    'precip': [float(r.precip) for r in records]
                }
                if all(r.pop is not None for r in records):
                    response_data['pop'] = [float(r.pop) if r.pop is not None else 0 for r in records]
                if all(r.pressure is not None for r in records):
                    response_data['pressure'] = [float(r.pressure) if r.pressure is not None else 0 for r in records]
                if all(r.cloud is not None for r in records):
                    response_data['cloud'] = [float(r.cloud) if r.cloud is not None else 0 for r in records]

                if records and hasattr(records[0], 'update_time'):  # 检查列表是否为空
                    response_data['updated_at'] = records[0].update_time.strftime('%Y-%m-%d %H:%M:%S')
                print("成功构建响应数据")
                return jsonify(response_data)

        # 数据库中没有数据，或者数据过期, 调用API获取
        print(f"未找到城市 {city} 的最新小时数据，正在从API获取")
        hourly_data = get_hourly_forecast(city)  # 这个函数会处理API获取和数据库更新

        if hourly_data:
            # 重新从数据库读取（因为 get_hourly_forecast 已经更新了数据库）
            records = HourlyForecast.query.filter_by(city=city).order_by(HourlyForecast.fx_time).limit(24).all()

            # 构建响应数据... (与之前版本相同)
            response_data = {
                'times': [r.fx_time.strftime('%H:%M') for r in records],
                'temps': [float(r.temp) for r in records],
                'humidity': [float(r.humidity) for r in records],
                'wind_speed': [float(r.wind_speed) for r in records],
                'wind_dir': [r.wind_dir for r in records],
                'text': [r.text for r in records],
                'icon': [r.icon for r in records],
                'precip': [float(r.precip) for r in records]
            }
            if all(r.pop is not None for r in records):
                response_data['pop'] = [float(r.pop) if r.pop is not None else 0 for r in records]
            if all(r.pressure is not None for r in records):
                response_data['pressure'] = [float(r.pressure) if r.pressure is not None else 0 for r in records]
            if all(r.cloud is not None for r in records):
                response_data['cloud'] = [float(r.cloud) if r.cloud is not None else 0 for r in records]
            if records and hasattr(records[0], 'update_time'):  # 检查列表是否为空
                response_data['updated_at'] = records[0].update_time.strftime('%Y-%m-%d %H:%M:%S')
            print("成功构建响应数据")
            return jsonify(response_data)

        else:
            return jsonify({"error": "未找到该城市的小时预报数据"}), 404

    except Exception as e:
        import traceback
        error_msg = f"获取小时数据时出错: {str(e)}\n{traceback.format_exc()}"
        print(error_msg)
        return jsonify({"error": error_msg}), 500


# 一周天气预报 - 增加了缓存逻辑
@app.route('/weekly_data/<city>')
def get_weather_forecast(city):
    with app.app_context():
        # 尝试从数据库获取
        forecasts = WeatherForecast.query.filter_by(city=city).order_by(WeatherForecast.fx_date).limit(7).all()

        if forecasts:
            # 检查数据是否是最新的（1小时内）
            most_recent_update = forecasts[0].update_time
            if (datetime.now() - most_recent_update) < timedelta(hours=1):
                # 从数据库返回数据
                # 记录用户查询周预报的活动
                if current_user.is_authenticated:
                    record_activity(
                        activity_type="view",
                        description=f"查看了{city}的周预报",
                        icon="fa-calendar",
                        related_data=f"未来7天预报(来自缓存)"
                    )
                return jsonify({
                    'dates': [f.fx_date.strftime('%m/%d') for f in forecasts],
                    'temp_max': [f.temp_max for f in forecasts],
                    'temp_min': [f.temp_min for f in forecasts],
                    'icons': [f.icon_day for f in forecasts],
                    'texts': [f.text_day for f in forecasts],
                    'wind_scale': [f.wind_scale for f in forecasts],
                    'humidity': [f.humidity for f in forecasts],
                    'precip': [f.precip for f in forecasts]
                })

        # 如果数据库中没有数据，或者数据已过期,则调用API获取并更新数据库
        forecast_data = fetch_weather_forecast(city)  # 这个函数会处理API获取和数据库更新
        if forecast_data:
            # 重新从数据库读取
            forecasts = WeatherForecast.query.filter_by(city=city).order_by(WeatherForecast.fx_date).limit(7).all()

            # 记录用户查询周预报的活动
            if current_user.is_authenticated:
                record_activity(
                    activity_type="view",
                    description=f"查看了{city}的周预报",
                    icon="fa-calendar",
                    related_data=f"未来7天预报"
                )
            return jsonify({
                'dates': [f.fx_date.strftime('%m/%d') for f in forecasts],
                'temp_max': [f.temp_max for f in forecasts],
                'temp_min': [f.temp_min for f in forecasts],
                'icons': [f.icon_day for f in forecasts],
                'texts': [f.text_day for f in forecasts],
                'wind_scale': [f.wind_scale for f in forecasts],
                'humidity': [f.humidity for f in forecasts],
                'precip': [f.precip for f in forecasts]
            })
        else:
            return jsonify({'status': 'error', 'message': '无法获取天气预报数据'}), 500


# 实时天气 - 增加了缓存逻辑
@app.route('/weather_data/<city>')
def get_weather_records(city):
    with app.app_context():
        # 尝试从数据库获取
        record = WeatherData.query.filter_by(city=city).order_by(WeatherData.obs_time.desc()).first()

        if record:
            # 检查数据是否是最新的（1小时内）
            if (datetime.now() - record.update_time) < timedelta(hours=1):
                # 从数据库返回数据
                if current_user.is_authenticated:
                    record_activity(
                        activity_type="view",
                        description=f"查询了{city}的天气",
                        icon="fa-cloud",
                        related_data=f"获取最新天气数据（来自缓存）"
                    )
                return jsonify({
                    'temp': [record.temp],
                    'humidity': [record.humidity],
                    'wind_speed': [record.wind_speed],
                    'feels_like': [record.feels_like],
                    'wind_dir': [record.wind_dir],
                    'wind_scale': [record.wind_scale],
                    'precip': [record.precip],
                    'pressure': [record.pressure],
                    'vis': [record.vis],
                    'cloud': [record.cloud if hasattr(record, 'cloud') else None],
                    'dew': [record.dew if hasattr(record, 'dew') else None],
                    'text': [record.text if hasattr(record, 'text') else '--'],
                    'icon': [record.icon if hasattr(record, 'icon') else None]
                })

        # 如果数据库中没有数据，或者数据已过期，则调用API获取并更新数据库
        current_weather = get_current_weather_data(city)  # 这个函数处理了API获取和数据库更新
        if current_weather:
            # 重新从数据库读取
            record = WeatherData.query.filter_by(city=city).order_by(WeatherData.obs_time.desc()).first()
            # 记录用户查询天气的活动
            if current_user.is_authenticated:
                record_activity(
                    activity_type="view",
                    description=f"查询了{city}的天气",
                    icon="fa-cloud",
                    related_data=f"获取最新天气数据"
                )
            return jsonify({
                'temp': [record.temp],
                'humidity': [record.humidity],
                'wind_speed': [record.wind_speed],
                'feels_like': [record.feels_like],
                'wind_dir': [record.wind_dir],
                'wind_scale': [record.wind_scale],
                'precip': [record.precip],
                'pressure': [record.pressure],
                'vis': [record.vis],
                'cloud': [record.cloud if hasattr(record, 'cloud') else None],
                'dew': [record.dew if hasattr(record, 'dew') else None],
                'text': [record.text if hasattr(record, 'text') else '--'],
                'icon': [record.icon if hasattr(record, 'icon') else None]
            })
        else:
            # 如果没有记录，返回空数据
            return jsonify({
                'temp': [],
                'humidity': [],
                'wind_speed': [],
                'text': []
            })


# 月温度曲线图表
@app.route('/monthly_temp/<city>')
def get_monthly_temp(city):
    with app.app_context():
        today = datetime.now()
        thirty_days_ago = today - timedelta(days=30)
        
        print(f"查询城市: {city}")
        print(f"查询时间范围: {thirty_days_ago} 到 {today}")

        # 首先尝试查询过去30天的数据，按日期排序
        recent_data = CleanedHistoricalWeather.query.filter(
            CleanedHistoricalWeather.city_name.ilike(f'%{city}%'),
            CleanedHistoricalWeather.date >= thirty_days_ago,
            CleanedHistoricalWeather.date <= today
        ).order_by(CleanedHistoricalWeather.date).all()

        print(f"查询到过去30天的数据条数: {len(recent_data)}")
        if recent_data:
            print(f"数据日期范围: {recent_data[0].date} 到 {recent_data[-1].date}")

        # 如果找到的数据少于30条，则获取更早的数据来补充
        if len(recent_data) < 30:
            print(f"数据不足30条，需要补充 {30 - len(recent_data)} 条更早的数据")
            # 获取更早的数据
            earlier_data = CleanedHistoricalWeather.query.filter(
                CleanedHistoricalWeather.city_name.ilike(f'%{city}%'),
                CleanedHistoricalWeather.date < thirty_days_ago
            ).order_by(CleanedHistoricalWeather.date.desc()).limit(30 - len(recent_data)).all()
            earlier_data.reverse()  # 将数据按日期升序排列
            
            # 合并数据
            historical_data = earlier_data + recent_data
            print(f"补充后总数据条数: {len(historical_data)}")
            if historical_data:
                print(f"最终数据日期范围: {historical_data[0].date} 到 {historical_data[-1].date}")
        else:
            historical_data = recent_data

        if not historical_data:
            print("未找到任何数据")
            return jsonify({
                'success': False,
                'message': 'No data available'
            }), 404

        # 提取日期、最高温和最低温
        dates = []
        temp_max = []
        temp_min = []

        for record in historical_data:
            dates.append(record.date.strftime('%Y-%m-%d'))  # 格式化日期
            temp_max.append(record.temp_max)
            temp_min.append(record.temp_min)

        print(f"最终返回的数据条数: {len(dates)}")
        print(f"日期列表: {dates}")

        # 返回json数据
        return jsonify({
            'success': True,
            'data': {
                'dates': dates,
                'temp_max': temp_max,
                'temp_min': temp_min
            }
        })

@app.route('/weather_distribution/<city>')
def get_weather_distribution(city):
    try:
        # 获取该城市最近的30条天气记录
        records = WeatherData.query.filter_by(city=city)\
            .order_by(WeatherData.obs_time.desc())\
            .limit(30)\
            .all()
            
        if not records:
            return jsonify({
                'success': False,
                'message': '未找到该城市的天气数据'
            }), 404
            
        # 统计天气状况分布
        weather_counts = {}
        for record in records:
            weather = record.text
            weather_counts[weather] = weather_counts.get(weather, 0) + 1
            
        # 转换为前端所需的格式
        distribution_data = [
            {'name': weather, 'value': count}
            for weather, count in weather_counts.items()
        ]
        
        return jsonify({
            'success': True,
            'data': distribution_data
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'获取天气分布数据失败: {str(e)}'
        }), 500


# 将能见度 (米) 分段线性映射到 0-100 的评分
def visibility_to_score(visibility):
    if visibility <= 100:  # 强浓雾
        score = 5
    elif visibility <= 500:  # 浓雾
        score = 10 + (visibility - 100) / (500 - 100) * 10  # 10-20
    elif visibility <= 1000:  # 大雾
        score = 20 + (visibility - 500) / (1000 - 500) * 10  # 20-30
    elif visibility <= 2000:  # 轻雾
        score = 30 + (visibility - 1000) / (2000 - 1000) * 20  # 30-50
    elif visibility <= 5000:  # 中度雾霾
        score = 50 + (visibility - 2000) / (5000 - 2000) * 20  # 50 - 70
    elif visibility <= 10000:  # 轻度雾霾
        score = 70 + (visibility - 5000) / (10000 - 5000) * 20  # 70-90
    else:  # 良好以上
        score = 90 + (visibility - 10000) / (30000 - 10000) * 10  # 90-100, 假设最大30km
        score = min(100, score)
    return int(score)


# 气象指标雷达图
@app.route('/radar_data/<city>')
def get_radar_data(city):
    with app.app_context():
        def calculate_comfort(temp, humidity, wind_speed):
            # 1. 计算体感温度 (使用更接近中国气象局常用的公式)
            #    - 风寒指数 (适用于低温)
            if temp <= 10:
                apparent_temp = 13.12 + 0.6215 * temp - 11.37 * (wind_speed ** 0.16) + 0.3965 * temp * (
                        wind_speed ** 0.16)
            #    - 炎热指数 (适用于高温高湿)
            elif temp >= 26 and humidity >= 40:
                apparent_temp = -8.784695 + 1.61139411 * temp + 2.338549 * humidity - 0.14611605 * temp * humidity \
                                - 0.012308094 * temp ** 2 - 0.016424828 * humidity ** 2 + 0.002211732 * temp ** 2 * humidity \
                                + 0.00072546 * temp * humidity ** 2 - 0.000003582 * temp ** 2 * humidity ** 2
            #    - 其他情况，使用简化的 Steadman 公式
            else:
                apparent_temp = 1.04 * temp + 0.2 * (
                        6.105 * math.exp(17.27 * temp / (237.7 + temp)) * humidity / 100) - 0.65 * wind_speed - 2.7

            # 2. 根据体感温度, 动态确定舒适度等级和评分 (不再依赖季节)
            #    - 使用分段函数, 使评分更平滑.
            if apparent_temp < 12:
                score = 10 + (apparent_temp - 5) * 2  # 极冷区间
            elif apparent_temp < 18:
                score = 30 + (apparent_temp - 12) * 3  # 寒冷 -> 凉爽
            elif apparent_temp < 26:
                score = 50 + (apparent_temp - 18) * 5  # 凉爽 -> 舒适
            elif apparent_temp < 30:
                score = 90 + (apparent_temp - 26) * 2.5  # 舒适 -> 闷热
            else:
                score = 100 - (apparent_temp - 30) * 3  # 闷热以上

            return int(max(10, min(100, score)))  # 限制在 0-100 之间

        def estimate_visibility(humidity, cloud, wind_speed):
            # 1. 湿度的影响: 湿度越高，能见度越低 (非线性关系)
            humidity_effect = 8000 * (1 - (humidity / 100)) ** 2
            # 2. 云量的影响: 云量越高，能见度越低
            cloud_effect = 5000 * (1 - (cloud / 100))
            # 3. 风速的影响: 风速越大，能见度越高
            wind_effect = 500 * (wind_speed / (wind_speed + 2))
            visibility = humidity_effect + cloud_effect + wind_effect
            return int(max(100, min(12000, visibility)))

        def get_radar_data_from_record(record):
            temp = record.temp if record.temp is not None else 20
            humidity = record.humidity if record.humidity is not None else 50
            wind_speed = record.wind_speed if record.wind_speed is not None else 5
            cloud = record.cloud if record.cloud is not None else 20

            visibility = estimate_visibility(humidity, cloud, wind_speed)
            vis_score = visibility_to_score(visibility)  # 转换为评分
            comfort = calculate_comfort(temp, humidity, wind_speed)
            radar_data = [temp, humidity, wind_speed, vis_score, comfort]  # 使用评分
            indicator_names = ['温度', '湿度', '风速', '能见度', '舒适度']
            return radar_data, indicator_names

        def fetch_data_from_db(city):
            # 优先从 WeatherData 获取
            record = WeatherData.query.filter_by(city=city).order_by(WeatherData.obs_time.desc()).first()
            if record and (datetime.now() - record.update_time) < timedelta(hours=1):
                return record
            # 如果 WeatherData 没有数据或数据过旧,尝试从 HourlyForecast 获取
            record = HourlyForecast.query.filter_by(city=city).order_by(HourlyForecast.fx_time.desc()).first()
            return record

        # 从数据库获取数据
        record = fetch_data_from_db(city)
        if record:
            radar_data, indicator_names = get_radar_data_from_record(record)
            result = {'status': 'success', 'data': radar_data, 'indicators': indicator_names}
            return jsonify(result)

        # 如果都没有数据,返回错误信息
        return jsonify({'status': 'error', 'message': 'No data available'}), 404


@app.route('/cleaned_historical_weather/<city>')
def get_cleaned_historical_weather(city):
    with app.app_context():
        thirty_days_ago = datetime.now().date() - timedelta(days=30)
        # 先查最近30天
        recent_data = CleanedHistoricalWeather.query.filter(
            CleanedHistoricalWeather.city_name == city,
            CleanedHistoricalWeather.date >= thirty_days_ago
        ).order_by(CleanedHistoricalWeather.date.desc()).all()

        # 不足30条再补历史
        if len(recent_data) < 30:
            extra_needed = 30 - len(recent_data)
            extra_data = CleanedHistoricalWeather.query.filter(
                CleanedHistoricalWeather.city_name == city,
                CleanedHistoricalWeather.date < thirty_days_ago
            ).order_by(CleanedHistoricalWeather.date.desc()).limit(extra_needed).all()
            historical_data = recent_data + extra_data
        else:
            historical_data = recent_data

        # 按日期升序排列
        historical_data = sorted(historical_data, key=lambda r: r.date)

        result = []
        for record in historical_data:
            result.append({
                'date': record.date.strftime('%Y-%m-%d'),
                'temp_max': record.temp_max,
                'temp_min': record.temp_min,
                'text': record.weather,
                'wind_dir': record.wind_dir
            })
        return jsonify({'status': 'success', 'data': result})


# 记录搜索历史的辅助函数
def record_search(query):
    if current_user.is_authenticated:
        search = SearchHistory(
            user_id=current_user.id,
            search_query=query
        )
        db.session.add(search)
        db.session.commit()


# 记录搜索次数
@app.route('/record_search_activity', methods=['POST'])
def record_search_activity():
    if current_user.is_authenticated:
        try:
            data = request.json
            city = data.get('city', '')

            # 使用现有的record_activity函数记录搜索活动
            record_activity(
                activity_type="search",
                description="搜索城市天气",
                icon="fa-search",
                related_data=f"城市: {city}"
            )

            # 记录搜索历史
            record_search(city)
            return jsonify({'status': 'success'})
        except Exception as e:
            return jsonify({'status': 'error', 'message': str(e)}), 500
    else:
        return jsonify({'status': 'error', 'message': '用户未登录'}), 403


# 定位获取坐标
@app.route('/reverse_geocode/<lat>/<lng>')
def reverse_geocode(lat, lng):
    try:
        # 参数验证
        if not is_float(lat) or not is_float(lng):
            return jsonify({'status': 'error', 'message': '无效的坐标参数'})

        # 调用封装好的API方法
        result = reverse_geocode_api(float(lat), float(lng))

        # 统一返回格式
        if result['status'] == 'success':
            return jsonify({
                'status': 'success',
                'city': result['city']
            })

        return jsonify(result)

    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f"服务器错误: {str(e)}"
        })


def is_float(value):
    try:
        float(value)
        return True
    except ValueError:
        return False


# 添加地图页面路由
@app.route('/china_map')
def china_map():
    return render_template('ChinaMap.html')


@app.route('/get_provinces_temp')
def get_provinces_temp():
    # 先尝试从数据库获取
    cached_data = RegionTemperature.query.filter(
        RegionTemperature.level == 'province',
        RegionTemperature.update_time >= datetime.now() - timedelta(hours=12)  # 缓存12小时
    ).all()

    # 验证数据完整性
    if len(cached_data) >= len(weather_province_api.PROVINCE_NAMES):
        formatted_data = [{
            "name": p.name,
            "value": p.temp_avg,
            "temp_max": p.temp_max,
            "temp_min": p.temp_min
        } for p in cached_data]
        return jsonify(formatted_data)

    # 记录用户查看地图的活动
    if current_user.is_authenticated:
        record_activity(
            activity_type="view",
            description="查看了中国气温分布图",
            icon="fa-map",
            related_data="全国温度分布概览"
        )

    # 缓存不完整或过期时重新采集
    return fetch_and_cache_provinces_data()


def fetch_and_cache_provinces_data():
    """调用API获取并更新缓存"""
    provinces = weather_province_api.fetch_all_provinces_weather()

    # 转换数据结构
    formatted_data = []
    for p in provinces:
        record = RegionTemperature.query.filter_by(name=p["name"]).first()
        if not record:
            record = RegionTemperature(name=p["name"], level='province')

        record.temp_avg = p["temp_avg"]
        record.temp_max = p["temp_max"]
        record.temp_min = p["temp_min"]
        record.update_time = datetime.now()
        db.session.add(record)

        formatted_data.append({
            "name": p["name"],
            "value": p["temp_avg"],
            "temp_max": p["temp_max"],
            "temp_min": p["temp_min"]
        })

    try:
        db.session.commit()
        return jsonify(formatted_data)
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# 更新省份温度数据
def update_provinces_temperature():
    with app.app_context():
        try:
            provinces = fetch_all_provinces_weather()
            for p in provinces:
                record = RegionTemperature.query.filter_by(name=p['name']).first()
                if not record:
                    record = RegionTemperature(
                        name=p['name'],
                        level='province',
                        temp_avg=p['temp_avg'],
                        temp_max=p['temp_max'],
                        temp_min=p['temp_min']
                    )
                else:
                    record.temp_avg = p['temp_avg']
                    record.temp_max = p['temp_max']
                    record.temp_min = p['temp_min']
                    record.update_time = datetime.now()
                db.session.add(record)
            db.session.commit()
            print(f"成功更新 {len(provinces)} 个省份温度数据")
        except Exception as e:
            db.session.rollback()
            print(f"更新失败: {str(e)}")


# 添加反馈页面路由
@app.route('/feedback')
def feedback():
    return render_template('feedback.html')


@app.route('/submit_feedback', methods=['POST'])
def submit_feedback():
    try:
        data = request.get_json()

        # 正确处理user_id值
        user_id = None
        if current_user.is_authenticated:
            user_id = current_user.id
        elif data.get('user_id') and data.get('user_id').isdigit():
            user_id = int(data.get('user_id'))

        feedback = Feedback(
            user_id=user_id,  # 可能为None
            feedback_type=data['type'],
            content=data['content'],
            contact=data.get('contact')
        )

        db.session.add(feedback)
        db.session.commit()

        # 记录用户提交反馈的活动（只有已登录用户）
        if current_user.is_authenticated:
            record_activity(
                activity_type="feedback",
                description="提交了反馈",
                icon="fa-comment",
                related_data=f"反馈类型: {data['type']}"
            )

        return jsonify({'status': 'success', 'message': '反馈提交成功！感谢您的支持'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'status': 'error', 'message': str(e)}), 500


scheduler = BackgroundScheduler()
scheduler.add_job(
    func=update_provinces_temperature,
    trigger=IntervalTrigger(hours=12),
    id='update_provinces_job'
)

scheduler.start()

# 定义允许的文件扩展名
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

# 配置上传文件夹
app.config['UPLOAD_FOLDER'] = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static/images/avatars')
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)


def allowed_file(filename):
    """
    检查文件是否具有允许的扩展名
    """
    return '.' in filename and \
        filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


# 个人主页路由
@app.route('/profile')
@login_required
def profile():
    # 获取页数和活动类型过滤参数
    page = request.args.get('page', 1, type=int)
    activity_type = request.args.get('activity_type', None)
    show_all = request.args.get('show_all_activities', False, type=bool)

    # 获取用户统计信息
    days_since_joined = 0
    if current_user.register_date:
        days_since_joined = (datetime.now() - current_user.register_date).days
    else:
        current_user.register_date = datetime.now()
        db.session.commit()

    user_stats = {
        'views_count': UserActivity.query.filter_by(user_id=current_user.id).count(),
        'favorites_count': FavoriteLocation.query.filter_by(user_id=current_user.id).count(),
        'searches_count': UserActivity.query.filter_by(user_id=current_user.id, activity_type='search').count(),
        'days_since_joined': days_since_joined
    }

    # 查询用户活动，添加过滤和分页
    activities_query = UserActivity.query.filter_by(user_id=current_user.id)

    # 应用活动类型过滤
    if activity_type:
        activities_query = activities_query.filter_by(activity_type=activity_type)

    # 排序
    activities_query = activities_query.order_by(UserActivity.timestamp.desc())

    # 分页
    per_page = 50 if show_all else 5
    activities_pagination = activities_query.paginate(page=page, per_page=per_page, error_out=False)
    activities = activities_pagination.items

    # 获取收藏的位置
    favorite_locations = FavoriteLocation.query.filter_by(user_id=current_user.id).all()

    return render_template(
        'profile.html',
        user_stats=user_stats,
        user_activities=activities,
        has_more_activities=activities_pagination.has_next,
        current_page=page,
        activity_type=activity_type,
        favorite_locations=favorite_locations,
        user_theme=current_user.theme
    )


# 最近活动卡片
@app.route('/profile/load_more_activities')
@login_required
def load_more_activities():
    page = request.args.get('page', 1, type=int)
    activity_type = request.args.get('activity_type', None)

    # 构建查询
    activities_query = UserActivity.query.filter_by(user_id=current_user.id)
    if activity_type:
        activities_query = activities_query.filter_by(activity_type=activity_type)

    # 排序
    activities_query = activities_query.order_by(UserActivity.timestamp.desc())

    # 分页
    per_page = 5  # 每次加载5条，与profile中的per_page保持一致
    activities_pagination = activities_query.paginate(page=page, per_page=per_page, error_out=False)
    user_activities = activities_pagination.items

    # 将活动渲染为HTML片段
    html = render_template(
        'partials/activity_list.html',
        user_activities=user_activities
    )

    return jsonify({
        'html': html,
        'has_more': activities_pagination.has_next,
        'next_page': page + 1 if activities_pagination.has_next else page
    })


# 删除活动记录
@app.route('/activity/delete/<int:activity_id>', methods=['GET', 'POST'])
@login_required
def delete_activity(activity_id):
    activity = UserActivity.query.get_or_404(activity_id)

    # 检查是否是当前用户的活动
    if activity.user_id != current_user.id:
        flash('你没有权限删除这条活动记录', 'danger')
        return redirect(url_for('profile'))

    # 删除活动
    db.session.delete(activity)
    db.session.commit()

    flash('活动记录已删除', 'success')
    return redirect(url_for('profile'))


@app.route('/activity/clear', methods=['POST'])
@login_required
def clear_activities():
    activity_type = request.form.get('activity_type')

    if activity_type and activity_type != 'all':
        # 删除特定类型的活动
        UserActivity.query.filter_by(user_id=current_user.id, activity_type=activity_type).delete()
    else:
        # 删除所有活动
        UserActivity.query.filter_by(user_id=current_user.id).delete()

    db.session.commit()
    flash('活动记录已清空', 'success')
    return redirect(url_for('profile'))


# 记录用户活动的辅助函数
def record_activity(activity_type, description, icon, related_data=None):
    """
    记录用户活动并管理活动记录数量

    参数:
        activity_type: 活动类型 (view, search, favorite等)
        description: 活动描述
        icon: 前端显示的图标类 (fontawesome类名)
        related_data: 关联数据 (可选)
        url: 相关链接 (可选)
    """
    if current_user.is_authenticated:
        try:
            # 记录新活动
            activity = UserActivity(
                user_id=current_user.id,
                activity_type=activity_type,
                description=description,
                icon=icon,
                related_data=related_data,
                timestamp=datetime.now()
            )
            db.session.add(activity)

            # 管理活动记录数量，防止过多记录
            # 获取用户活动记录总数
            activity_count = UserActivity.query.filter_by(user_id=current_user.id).count()

            # 如果超过最大限制(如1000条)，删除最旧的记录
            max_activities = 1000  # 增加最大限制到1000条
            if activity_count > max_activities:
                oldest_activities = UserActivity.query.filter_by(user_id=current_user.id) \
                    .order_by(UserActivity.timestamp) \
                    .limit(activity_count - max_activities).all()

                for old_activity in oldest_activities:
                    db.session.delete(old_activity)

            db.session.commit()
            return True
        except Exception as e:
            db.session.rollback()
            print(f"记录用户活动失败: {str(e)}")
            # 可以添加日志记录
            return False
    return False


# 示例用法 - 记录不同类型的活动
def record_view_activity(item_name, item_id):
    """记录查看数据的活动"""
    record_activity(
        activity_type="view",
        description=f"查看了{item_name}",
        icon="fa-eye",
        related_data=f"ID: {item_id}",
        url=url_for('view_item', item_id=item_id)
    )


def record_favorite_activity(item_name, item_id):
    """记录收藏活动"""
    record_activity(
        activity_type="favorite",
        description=f"收藏了{item_name}",
        icon="fa-heart",
        related_data=f"ID: {item_id}",
        url=url_for('view_item', item_id=item_id)
    )


# 添加收藏位置的路由
@app.route('/favorite/add/<city_name>', methods=['POST'])
@login_required
def add_favorite(city_name):
    # 检查是否已收藏
    existing = FavoriteLocation.query.filter_by(
        user_id=current_user.id,
        name=city_name
    ).first()

    if not existing:
        favorite = FavoriteLocation(
            user_id=current_user.id,
            name=city_name
        )
        db.session.add(favorite)
        db.session.commit()

        # 记录活动
        record_activity(
            activity_type='favorite',
            description=f'收藏了城市 {city_name}',
            icon='fa-star',
            related_data=city_name
        )

        flash(f'已将 {city_name} 添加到收藏', 'success')
    else:
        flash(f'{city_name} 已在收藏列表中', 'info')

    return redirect(url_for('profile'))


# 获取收藏列表的路由
@app.route('/favorites/list', methods=['GET'])
@login_required
def list_favorites():
    try:
        favorites = FavoriteLocation.query.filter_by(user_id=current_user.id).all()
        favorites_list = [
            {
                'id': favorite.id,
                'name': favorite.name,
                'added_on': favorite.added_on.strftime('%Y-%m-%d %H:%M:%S')
            }
            for favorite in favorites
        ]
        return jsonify({
            'success': True,
            'favorites': favorites_list
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'获取收藏列表失败'
        }), 500


# 删除收藏位置的路由(个人主页)
@app.route('/favorite/remove/<city_name>', methods=['POST'])
@login_required
def remove_favorite(city_name):
    FavoriteLocation.query.filter_by(
        user_id=current_user.id,
        name=city_name
    ).delete()

    # 记录活动
    record_activity(
        activity_type='unfavorite',
        description=f'取消收藏城市 {city_name}',
        icon='fa-star-half',
        related_data=city_name
    )

    db.session.commit()
    flash(f'已将 {city_name} 从收藏中移除', 'success')
    return redirect(url_for('profile'))


# 从json中加载程序
@app.route('/api/cities')
def get_cities():
    with open('spider/old_province_city.json', 'r', encoding='utf-8') as f:
        cities_data = json.load(f)
    return jsonify(cities_data)


# 设置语言选择器函数（暂未实现）
def get_locale():
    # 优先使用用户个人设置的语言
    if current_user.is_authenticated and current_user.language:
        return current_user.language
    # 其次从请求头获取
    return request.accept_languages.best_match(['zh_CN', 'en_US'])


app.config['BABEL_TRANSLATION_DIRECTORIES'] = 'translations'
babel.init_app(app, locale_selector=get_locale)


# 个人主页个性化设置 + 设置页面偏好设置
@app.route('/profile/update_preference', methods=['POST'])
@login_required
def update_preference():
    try:
        data = request.get_json()

        # 详细的输入验证
        if not data:
            return jsonify({'success': False, 'message': '无效的请求数据'}), 400

        preference = data.get('preference')
        value = data.get('value')

        if preference is None or value is None:
            return jsonify({'success': False, 'message': '缺少必要的参数'}), 400

        # 动态确定 JSON 文件路径
        base_dir = os.path.dirname(os.path.abspath(__file__))
        json_path = os.path.join(base_dir, 'spider', 'old_province_city.json')

        # 额外的响应对象
        resp = jsonify({'success': True, 'message': '偏好设置已更新'})

        # 主题特殊处理
        if preference == 'theme':
            resp.set_cookie('user_theme', value, max_age=30 * 24 * 60 * 60)

        preference_mapping = {
            'theme': 'theme',
            'email_weather_alerts': 'email_weather_alerts',
            'temp_unit': 'temp_unit',
            'defaultCity': 'default_city',
            'tempUnit': 'temp_unit',
            'language': 'language'
        }

        # 检查偏好设置是否合法
        if preference not in preference_mapping:
            return jsonify({'success': False, 'message': '未知的偏好设置类型'}), 400

        # 城市验证
        if preference == 'defaultCity':
            # 添加更详细的日志记录
            app.logger.info(f"正在验证城市: {value}")

            # 检查 JSON 文件
            if not os.path.exists(json_path):
                app.logger.error(f"城市数据文件不存在: {json_path}")
                return jsonify({'success': False, 'message': '城市数据文件不存在'}), 500

            try:
                with open(json_path, 'r', encoding='utf-8') as f:
                    cities_data = json.load(f)

                # 扁平化城市列表
                all_cities = [city for province in cities_data.values() for city in province]

                # 详细的城市验证日志
                app.logger.info(f"可用城市列表: {all_cities}")

                if value not in all_cities:
                    app.logger.warning(f"无效的城市: {value}")
                    return jsonify({'success': False, 'message': '无效的城市'}), 400

            except json.JSONDecodeError:
                app.logger.error("城市数据文件解析错误")
                return jsonify({'success': False, 'message': '城市数据文件解析错误'}), 500
            except Exception as e:
                app.logger.error(f"读取城市数据失败: {str(e)}")
                return jsonify({'success': False, 'message': f'读取城市数据失败: {str(e)}'}), 500

        # 更新用户偏好
        db_field = preference_mapping[preference]
        setattr(current_user, db_field, value)
        current_user.profile_updated_at = datetime.now()

        db.session.commit()

        return resp

    except Exception as e:
        db.session.rollback()
        app.logger.error(f"更新用户偏好设置失败: {str(e)}", exc_info=True)
        return jsonify({'success': False, 'message': f'更新失败: {str(e)}'}), 500


def validate_phone(phone):
    """验证手机号格式"""
    if not phone:  # 允许为空
        return True
    import re
    pattern = r'^1[3-9]\d{9}$'
    return bool(re.match(pattern, phone))

# 个人设置路由
@app.route('/profile/settings', methods=['GET', 'POST'])
@login_required
def profile_settings():
    if request.method == 'POST':
        try:
            # 获取表单数据
            username = request.form.get('username', '').strip()
            email = request.form.get('email', '').strip()
            phone = request.form.get('phone', '').strip()
            bio = request.form.get('bio', '').strip()
            location = request.form.get('location', '').strip()
            occupation = request.form.get('occupation', '').strip()
            
            # 验证手机号
            if phone and not validate_phone(phone):
                flash('请输入正确的手机号码格式', 'danger')
                return redirect(url_for('profile_settings'))
            
            # 更新用户信息
            current_user.username = username
            current_user.email = email
            current_user.phone = phone
            current_user.bio = bio
            current_user.location = location
            current_user.occupation = occupation
            current_user.profile_updated_at = datetime.now()
            
            # 处理头像上传
            if 'avatar' in request.files:
                file = request.files['avatar']
                if file and allowed_file(file.filename):
                    filename = secure_filename(file.filename)
                    # 生成唯一文件名
                    ext = filename.rsplit('.', 1)[1].lower()
                    new_filename = f"{current_user.id}_{int(time.time())}.{ext}"
                    file.save(os.path.join(app.config['UPLOAD_FOLDER'], new_filename))
                    current_user.avatar_file = new_filename
            
            db.session.commit()
            flash('个人资料更新成功！', 'success')
            return redirect(url_for('profile_settings'))
            
        except Exception as e:
            db.session.rollback()
            app.logger.error(f"更新个人资料失败: {str(e)}")
            flash('更新失败，请稍后重试', 'danger')
            return redirect(url_for('profile_settings'))
    
    return render_template('profile_settings.html')


# 改密码
@app.route('/profile/change_password', methods=['POST'])
@login_required
def change_password():
    current_password = request.form.get('currentPassword')
    new_password = request.form.get('newPassword')
    confirm_password = request.form.get('confirmPassword')

    # 验证当前密码
    if not current_user.check_password(current_password):
        return jsonify({'status': 'error', 'message': '当前密码不正确'}), 400

    # 验证新密码一致性
    if new_password != confirm_password:
        return jsonify({'status': 'error', 'message': '两次输入的新密码不一致'}), 400

    # 设置新密码
    current_user.set_password(new_password)
    db.session.commit()
    flash('密码修改成功', 'success')
    return jsonify({'status': 'success', 'message': '密码修改成功'}), 200  # 添加返回语句


# 清除搜索历史
@app.route('/profile/clear_search_history', methods=['POST'])
@login_required
def clear_search_history():
    try:
        # 删除用户的搜索历史
        SearchHistory.query.filter_by(user_id=current_user.id).delete()
        # 同时删除用户活动表中的搜索记录
        UserActivity.query.filter_by(user_id=current_user.id, activity_type='search').delete()
        db.session.commit()

        # 返回 JSON 响应而不是重定向
        return jsonify({"success": True})
    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "message": str(e)}), 500


# 清除浏览历史
@app.route('/profile/clear_browsing_data', methods=['POST'])
@login_required
def clear_browsing_data():
    try:
        # 删除用户的搜索历史
        SearchHistory.query.filter_by(user_id=current_user.id).delete()

        # 删除用户的活动记录
        UserActivity.query.filter_by(user_id=current_user.id).delete()

        # 提交数据库更改
        db.session.commit()

        return jsonify({
            'success': True,
            'message': '浏览数据已成功清除'
        })
    except Exception as e:
        # 发生错误时回滚
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': f'清除数据时发生错误: {str(e)}'
        }), 500


# 更新双因素认证状态
@app.route('/profile/update-two-factor', methods=['POST'])
@login_required
def update_two_factor():
    try:
        data = request.get_json()
        is_enabled = data.get('enabled', False)
        current_user.two_factor_enabled = is_enabled
        db.session.commit()

        status = "启用" if is_enabled else "禁用"
        return jsonify({
            'success': True,
            'message': f'双因素认证已{status}'
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': '操作失败'
        }), 400


# 更新通知
@app.route('/profile/update-notification', methods=['POST'])
@login_required
def update_notification():
    try:
        # 获取请求的 JSON 数据
        data = request.get_json()
        setting = data.get('setting')
        enabled = data.get('enabled', False)

        # 映射前端设置名称到数据库字段
        notification_mapping = {
            'emailWeatherAlerts': 'email_weather_alerts',
            'emailWeeklyReport': 'email_weekly_report',
            'emailSystemUpdates': 'email_system_updates',
            'appWeatherAlerts': 'app_weather_alerts',
            'appDataUpdates': 'app_data_updates'
        }

        # 检查设置是否有效
        if setting not in notification_mapping:
            return jsonify({
                'success': False,
                'message': '无效的通知设置'
            }), 400

        # 获取对应的数据库字段名
        db_field = notification_mapping[setting]

        # 更新用户设置
        setattr(current_user, db_field, enabled)
        db.session.commit()

        return jsonify({
            'success': True,
            'message': '通知设置已更新'
        })

    except Exception as e:
        # 回滚数据库事务
        db.session.rollback()

        # 记录错误日志（如果有日志系统）
        current_app.logger.error(f"通知设置更新失败: {str(e)}")

        return jsonify({
            'success': False,
            'message': '设置保存失败，请稍后再试'
        }), 500


# 删除收藏位置的路由(个人设置)
@app.route('/favorite/remove_setting/<city_name>', methods=['POST'])
@login_required
def remove_favorite_settings(city_name):
    try:
        favorite = FavoriteLocation.query.filter_by(
            user_id=current_user.id,
            name=city_name
        ).first()

        if favorite:
            db.session.delete(favorite)
            db.session.commit()

            # 记录活动
            record_activity(
                activity_type='unfavorite',
                description=f'取消收藏城市 {city_name}',
                icon='fa-star-half',
                related_data=city_name
            )

            return jsonify({
                'success': True,
                'message': f'已将 {city_name} 从收藏中移除'
            })
        else:
            return jsonify({
                'success': False,
                'message': f'未找到城市 {city_name} 的收藏记录'
            }), 404
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': f'移除收藏失败: {str(e)}'
        }), 500


@app.route('/data_view')
def data_view():
    with app.app_context():
        cities = [c[0] for c in db.session.query(CleanedHistoricalWeather.city_name).distinct().all()]
        return render_template('data_view.html', cities=cities)


@app.route('/api/weather')
def get_weather_data():
    city = request.args.get('city')
    province = request.args.get('province')  # 获取 province 参数
    start = request.args.get('start')
    end = request.args.get('end')
    page = int(request.args.get('page', 1))
    size = int(request.args.get('size', 10))

    query = CleanedHistoricalWeather.query

    # 城市和省份筛选条件
    if city:  # 1. 如果选择了城市，优先按城市筛选
        city = city.strip()
        query = query.filter(CleanedHistoricalWeather.city_name.ilike(f"%{city}%"))
    elif province:  # 2. 如果只选择了省份，筛选该省份下的所有城市
        province = province.strip()
        query = query.filter(or_(
            CleanedHistoricalWeather.city_name.like(f"{province}%"),  # 匹配直辖市/自治区
            CleanedHistoricalWeather.city_name.in_(province_data.get(province, []))  # 匹配省份下城市
        ))

    # 时间范围筛选条件 (与之前相同)
    if start and end:
        query = query.filter(CleanedHistoricalWeather.date.between(start, end))
    elif start:
        query = query.filter(CleanedHistoricalWeather.date >= start)
    elif end:
        query = query.filter(CleanedHistoricalWeather.date <= end)

    total = query.count()
    data = query.order_by(CleanedHistoricalWeather.date.desc()) \
        .offset((page - 1) * size) \
        .limit(size) \
        .all()

    return jsonify({
        'data': [{
            'city_name': item.city_name,
            'date': item.date.strftime('%Y-%m-%d'),
            'temp_max': item.temp_max,
            'temp_min': item.temp_min,
            'weather': item.weather
        } for item in data],
        'total': total
    })


@app.route('/prediction_view')
def prediction_view():
    """显示预测视图页面"""
    with app.app_context():
        # 获取可以预测的城市列表
        cities = [c[0] for c in db.session.query(CleanedHistoricalWeather.city_name).distinct().all()]
        return render_template('prediction_view.html', cities=cities)


# 初始化预测器实例
predictor = WeatherPredictor(days_to_predict=7)

# 模态框中预测天气图表
@app.route('/predict_weather/<city>')
def predict_weather(city):
    try:
        predictions, metrics = predictor.run_full_pipeline(city, retrain=False)
        # 格式化预测结果
        def safe_convert(value):
            if isinstance(value, (pd.Timestamp, datetime)):
                return value.strftime('%Y-%m-%d')
            return float(value) if isinstance(value, (np.generic, float, np.float64)) else value
        formatted_results = {
            'dates': [safe_convert(d) for d in predictions['date'].tolist()],
            'temp_max': [safe_convert(t) for t in predictions['temp_max'].tolist()],
            'temp_min': [safe_convert(t) for t in predictions['temp_min'].tolist()]
        }
        return jsonify({
            'status': 'success',
            'predictions': formatted_results,
            'accuracy': metrics
        })
    except Exception as e:
        current_app.logger.error(f"预测失败: {str(e)}", exc_info=True)
        return jsonify({'status': 'error', 'message': str(e)}), 500


# 后端相关业务处理
@app.route('/upgrade_to_admin', methods=['POST'])  # 只处理 POST 请求
@login_required
def upgrade_to_admin():
    invite_code = request.form.get('invite_code')
    if invite_code == 'fumo666':
        current_user.is_admin = True
        db.session.commit()
        return jsonify({'success': True, 'message': '恭喜您，已成功升级为管理员！'})
    else:
        return jsonify({'success': False, 'message': '不玩富摩也配当管理吗？'})


# 添加管理员认证装饰器
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin:
            flash('您需要以管理员身份登录才能访问此页面。', 'danger')
            # 重定向到管理员登录页面，并传递 next 参数
            return redirect(url_for('admin_login', next=request.url))
        return f(*args, **kwargs)

    return decorated_function


# 管理员登录页面
@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if current_user.is_authenticated:
        if current_user.is_admin:
            return redirect(url_for('admin_dashboard'))
        else:  # 已登录的非管理员, 重定向到普通用户首页
            return redirect(url_for("index"))

    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = User.query.filter_by(username=username).first()

        if user and user.check_password(password) and user.is_admin:
            login_user(user)  # 使用 Flask-Login 登录管理员
            next_page = request.args.get('next')
            flash('管理员登录成功', 'success')
            return redirect(next_page or url_for('admin_dashboard'))
        else:
            flash('用户名、密码错误或非管理员', 'danger')

    return render_template('admin/login.html')  # 使用管理员登录模板


# 管理员退出
@app.route('/admin/logout')
@login_required
def admin_logout():
    logout_user()  # 使用 Flask-Login 注销用户
    flash('已退出管理员账号', 'success')
    return redirect(url_for('admin_login'))


# 管理员仪表板
@app.route('/admin')
@app.route('/admin/dashboard')
@admin_required
def admin_dashboard():
    # 打印调试信息
    print(f"Current session in dashboard: {session}")

    # 获取统计数据
    weather_data_count = db.session.query(CleanedHistoricalWeather).count()
    city_count = db.session.query(CleanedHistoricalWeather.city_name).distinct().count()
    region_count = db.session.query(RegionTemperature).count()
    # 获取模型数量
    model_path = predictor.model_path
    model_count = len([f for f in os.listdir(model_path) if f.endswith('.joblib')]) if os.path.exists(
        model_path) else 0
    # 获取爬虫最近更新的天气数据
    recent_weather = CleanedHistoricalWeather.query.order_by(CleanedHistoricalWeather.date.desc()).limit(5).all()
    # 用户最近查看的预报数据
    recent_forecast = WeatherForecast.query.order_by(WeatherForecast.fx_date.desc()).limit(5).all()

    return render_template('admin/dashboard.html',
                           weather_data_count=weather_data_count,
                           city_count=city_count,
                           region_count=region_count,
                           model_count=model_count,
                           recent_weather=recent_weather,
                           recent_forecast=recent_forecast)


# 天气数据管理
# 更新天气数据管理路由
@app.route('/admin/weather-data')
@admin_required
def admin_weather_data():
    # 从请求参数获取过滤条件
    city = request.args.get('city', '')
    start_date = request.args.get('start_date', '')
    end_date = request.args.get('end_date', '')
    page = request.args.get('page', 1, type=int)
    per_page = 20  # 每页显示的记录数

    # 构建查询
    query = CleanedHistoricalWeather.query

    if city:
        query = query.filter(CleanedHistoricalWeather.city_name.ilike(f'%{city}%'))
    if start_date:
        query = query.filter(CleanedHistoricalWeather.date >= start_date)
    if end_date:
        query = query.filter(CleanedHistoricalWeather.date <= end_date)

    # 获取总记录数和分页数据
    total_count = query.count()
    total_pages = (total_count + per_page - 1) // per_page

    # 分页查询
    weather_data = query.order_by(CleanedHistoricalWeather.date.desc()) \
        .offset((page - 1) * per_page) \
        .limit(per_page) \
        .all()

    return render_template('admin/weather_data.html',
                           weather_data=weather_data,
                           page=page,
                           total_pages=total_pages)


# 添加天气数据
@app.route('/admin/add-weather-data', methods=['POST'])
@admin_required
def admin_add_weather_data():
    try:
        # 获取表单数据
        city_name = request.form.get('city_name')
        date_str = request.form.get('date')
        temp_max = request.form.get('temp_max', type=float)
        temp_min = request.form.get('temp_min', type=float)
        weather = request.form.get('weather')
        wind_dir = request.form.get('wind_dir')

        # 检查是否已存在相同城市和日期的记录
        date = datetime.strptime(date_str, '%Y-%m-%d').date()
        existing_record = CleanedHistoricalWeather.query.filter_by(
            city_name=city_name,
            date=date
        ).first()

        if existing_record:
            flash(f'该城市在{date_str}已有天气数据记录，请勿重复添加', 'warning')
            return redirect(url_for('admin_weather_data'))

        # 创建新记录
        new_data = CleanedHistoricalWeather(
            city_name=city_name,
            date=date,
            temp_max=temp_max,
            temp_min=temp_min,
            weather=weather,
            wind_dir=wind_dir,
            year=date.year,
            month=date.month
        )

        db.session.add(new_data)
        db.session.commit()

        flash('天气数据添加成功', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'天气数据添加失败: {str(e)}', 'danger')
    return redirect(url_for('admin_weather_data'))


# 编辑天气数据
@app.route('/admin/edit-weather-data/<int:id>', methods=['POST'])
@admin_required
def admin_edit_weather_data(id):
    try:
        # 查找记录
        data = CleanedHistoricalWeather.query.get_or_404(id)

        # 更新数据
        data.city_name = request.form.get('city_name')
        date_str = request.form.get('date')
        data.date = datetime.strptime(date_str, '%Y-%m-%d').date()
        data.temp_max = request.form.get('temp_max', type=float)
        data.temp_min = request.form.get('temp_min', type=float)
        data.weather = request.form.get('weather')
        data.wind_dir = request.form.get('wind_dir')
        data.year = data.date.year
        data.month = data.date.month

        db.session.commit()
        flash('天气数据更新成功', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'天气数据更新失败: {str(e)}', 'danger')

    return redirect(url_for('admin_weather_data'))


# 删除天气数据
@app.route('/admin/delete-weather-data/<int:id>')
@admin_required
def admin_delete_weather_data(id):
    try:
        # 查找记录
        data = CleanedHistoricalWeather.query.get_or_404(id)

        # 删除记录
        db.session.delete(data)
        db.session.commit()

        flash('天气数据删除成功', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'天气数据删除失败: {str(e)}', 'danger')

    return redirect(url_for('admin_weather_data'))


# 管理员界面 - 批量删除天气数据
@app.route('/admin/batch_delete_weather_data')
def admin_batch_delete_weather_data():
    ids = request.args.get('ids')
    if ids:
        ids_list = ids.split(',')
        try:
            ids_to_delete = [int(id) for id in ids_list]
            CleanedHistoricalWeather.query.filter(CleanedHistoricalWeather.id.in_(ids_to_delete)).delete(
                synchronize_session=False)
            db.session.commit()
            return jsonify({'success': True, 'message': '批量删除成功'})  # 返回 JSON 响应
        except Exception as e:
            db.session.rollback()
            import traceback
            traceback.print_exc()
            return jsonify({'success': False, 'message': '批量删除失败'})  # 返回 JSON 响应
        finally:
            db.session.close()
    else:
        return jsonify({'success': False, 'message': '未选择任何数据'})  # 返回 JSON 响应


# 预测模型管理
@app.route('/admin/prediction-models')
@admin_required
def admin_prediction_models():
    with app.app_context():
        # 获取查询参数
        page = request.args.get('page', 1, type=int)
        per_page = 10
        sort_order = request.args.get('sort_order', 'desc')
        search = request.args.get('search', '').strip()
        model_path = predictor.model_path
        # 获取所有存在的模型文件
        existing_models = []
        if os.path.exists(model_path):
            existing_models = [f for f in os.listdir(model_path) if f.endswith('.joblib')]
        # 构建基础查询，获取所有唯一的城市名称
        city_query = db.session.query(
            CleanedHistoricalWeather.city_name.distinct().label('city_name')
        )
        # 添加搜索条件
        if search:
            city_query = city_query.filter(
                CleanedHistoricalWeather.city_name.ilike(f'%{search}%')
            )
        # 获取所有符合条件的城市名称列表
        all_cities = [row.city_name for row in city_query.order_by(CleanedHistoricalWeather.city_name.asc()).all()]
        # 获取每个城市对应模型文件的修改时间
        model_timestamps = {}
        for city in all_cities:
            model_file = f"{city}_weather_model.joblib"
            if model_file in existing_models:
                file_path = os.path.join(model_path, model_file)
                try:
                    mtime = os.path.getmtime(file_path)
                    timestamp = datetime.fromtimestamp(mtime)
                    model_timestamps[city] = timestamp
                except OSError:
                    model_timestamps[city] = None
            else:
                model_timestamps[city] = None
        # 构建城市与其last_trained时间的关联列表
        cities_with_trained = []
        for city in all_cities:
            last_trained = model_timestamps.get(city)
            cities_with_trained.append({
                'city_name': city,
                'last_trained': last_trained
            })
        # 根据last_trained进行排序
        reverse = (sort_order == 'desc')

        # 排序逻辑：先按last_trained排序，last_trained为None的城市排在最后（无论升降序）
        # 使用元组进行多级排序：(is_none, timestamp)，None排在最后
        cities_with_trained.sort(
            key=lambda x: (
            not (x['last_trained'] is None) if reverse else (x['last_trained'] is None), x['last_trained']),
            reverse=reverse
        )

        # 手动分页
        total = len(cities_with_trained)
        total_pages = math.ceil(total / per_page) if per_page else 1
        # 确保当前页在有效范围内
        page = max(1, min(page, total_pages))
        start = (page - 1) * per_page
        end = start + per_page
        paginated_cities = cities_with_trained[start:end]
        cities = [city['city_name'] for city in paginated_cities]
        # 为模板准备model_timestamps显示格式
        model_timestamps_display = {}
        for city in cities:
            timestamp = model_timestamps.get(city)
            if timestamp:
                model_timestamps_display[city] = timestamp.strftime('%Y-%m-%d %H:%M:%S')
            else:
                model_timestamps_display[city] = '未知'
        return render_template('admin/prediction_models.html',
                               cities=cities,
                               existing_models=existing_models,
                               model_timestamps=model_timestamps_display,
                               page=page,
                               total_pages=total_pages,
                               sort_order=sort_order,
                               search=search)


# 城市管理
# 添加缓存相关的全局变量
city_data_cache = {}
city_cache_time = 0
CACHE_TIMEOUT = 60  # 1分钟缓存

def clear_city_data_cache():
    """清除城市数据缓存"""
    global city_data_cache, city_cache_time
    city_data_cache = {}
    city_cache_time = 0

# 获取城市数据的函数
def get_city_data(search_term=''):
    global city_data_cache, city_cache_time
    cache_key = f"cities_{search_term}"
    current_time = time.time()
    # 如果缓存有效，直接返回缓存
    if cache_key in city_data_cache and current_time - city_cache_time < CACHE_TIMEOUT:
        return city_data_cache[cache_key]

    # 查询城市列表、记录数和最新日期
    query = db.session.query(
        CleanedHistoricalWeather.city_name,
        db.func.count(CleanedHistoricalWeather.id).label('record_count'),
        db.func.max(CleanedHistoricalWeather.date).label('latest_date')
    )
    if search_term:
        query = query.filter(CleanedHistoricalWeather.city_name.ilike(f'%{search_term}%'))
    cities = query.group_by(CleanedHistoricalWeather.city_name).order_by(db.desc('latest_date')).all()

    # 获取每个城市的日期范围
    city_date_ranges = {}
    for city, _, latest in cities:
        # 最早日期
        earliest = db.session.query(db.func.min(CleanedHistoricalWeather.date)) \
            .filter(CleanedHistoricalWeather.city_name == city).scalar()
        city_date_ranges[city] = {
            'earliest': earliest.strftime('%Y-%m-%d') if earliest else '-',
            'latest': latest.strftime('%Y-%m-%d') if latest else '-'
        }

    # 更新缓存
    city_data_cache[cache_key] = {
        'cities': [(city, count) for city, count, _ in cities],  # 只保留城市名和记录数
        'city_date_ranges': city_date_ranges
    }
    city_cache_time = current_time
    return city_data_cache[cache_key]


# 城市列表API
@app.route('/admin/api/cities')
@admin_required
def admin_cities_api():
    try:
        search = request.args.get('search', '')
        page = request.args.get('page', 1, type=int)
        per_page = 20

        # 获取城市数据
        data = get_city_data(search)
        cities = data['cities']
        city_date_ranges = data['city_date_ranges']

        # 计算分页
        total_items = len(cities)              # 城市数量
        total_pages = (total_items + per_page - 1) // per_page  #总页数
        start_idx = (page - 1) * per_page               #当前页在所有列表中的起止下标
        end_idx = min(start_idx + per_page, total_items)

        # 获取当前页数据
        current_page_cities = cities[start_idx:end_idx]

        # 构建响应数据
        city_list = []
        for city, record_count in current_page_cities:
            city_list.append({
                'name': city,
                'record_count': record_count,
                'earliest_date': city_date_ranges.get(city, {}).get('earliest', '-'),
                'latest_date': city_date_ranges.get(city, {}).get('latest', '-')
            })

        return jsonify({
            'cities': city_list,
            'total_pages': total_pages,
            'current_page': page
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500


# 修改城市管理页面路由
@app.route('/admin/cities')
@admin_required
def admin_cities():
    # 只传递搜索参数，其他数据通过API异步加载
    search = request.args.get('search', '')
    return render_template('admin/cities.html', search=search)


# 添加城市
@app.route('/admin/add-city', methods=['POST'])
@admin_required
def admin_add_city():
    try:
        city_name = request.form.get('city_name')
        city_code = request.form.get('city_code', '')

        # 检查城市是否已存在
        existing_city = CleanedHistoricalWeather.query.filter_by(city_name=city_name).first()
        if existing_city:
            flash(f'城市 {city_name} 已存在', 'warning')
            return redirect(url_for('admin_cities'))

        # 创建一条示例记录（可以通过爬虫获取实际数据）
        today = datetime.now().date()
        new_city_record = CleanedHistoricalWeather(
            city_name=city_name,
            city_code=city_code if city_code else None,
            date=today,
            temp_max=25.0,  # 示例数据
            temp_min=15.0,  # 示例数据
            weather='晴',
            wind_dir='来财风',
            year=today.year,
            month=today.month
        )
        db.session.add(new_city_record)
        db.session.commit()

        # 清除城市数据缓存
        clear_city_data_cache()

        flash(f'城市 {city_name} 添加成功', 'success')

    except Exception as e:
        db.session.rollback()
        flash(f'添加城市失败: {str(e)}', 'danger')

    return redirect(url_for('admin_cities'))


# 添加一个全局变量来存储爬取任务状态
crawl_tasks = {}

@app.route('/admin/crawl-weather/<city>')
@admin_required
def admin_crawl_weather(city):
    # 生成任务ID
    task_id = str(uuid.uuid4())
    crawl_tasks[task_id] = {'status': 'running', 'city': city}
    
    try:
        # 检查是否被取消
        if crawl_tasks[task_id]['status'] == 'cancelled':
            return jsonify({'message': '任务已取消'}), 200
            
        # 执行爬取操作
        batch_crawl(city)
        clear_city_data_cache()  # 清除缓存
        flash(f'已爬取 {city} 的天气数据（2025年1月1日至今）。', 'success')
        
        crawl_tasks[task_id]['status'] = 'completed'
        return jsonify({'message': '数据爬取成功'})
    except Exception as e:
        crawl_tasks[task_id]['status'] = 'failed'
        return jsonify({'message': str(e)}), 500
    finally:
        # 清理任务状态
        if task_id in crawl_tasks:
            del crawl_tasks[task_id]

@app.route('/admin/crawl-all-cities')
@admin_required
def crawl_all_cities():
    # 设置取消标志为 running
    crawl_tasks['all'] = {'status': 'running', 'city': 'all'}
    try:
        batch_crawl()  # 阻塞直到所有城市都爬完
        crawl_tasks['all']['status'] = 'completed'
        return jsonify({'message': '所有城市数据爬取完成'})
    except Exception as e:
        crawl_tasks['all']['status'] = 'failed'
        return jsonify({'message': str(e)}), 500
    finally:
        if 'all' in crawl_tasks:
            del crawl_tasks['all']

@app.route('/admin/cancel-crawl/<task_id>')
@admin_required
def cancel_crawl(task_id):
    if task_id in crawl_tasks:
        crawl_tasks[task_id]['status'] = 'cancelled'
        return jsonify({'message': '任务已取消'})
    return jsonify({'message': '任务不存在'}), 404

# --- 用户管理路由 ---
@app.route('/admin/users')
@admin_required
def admin_users():
    app.logger.info("管理员访问用户列表")
    users = User.query.all()
    return render_template('admin/users.html', users=users)


@app.route('/admin/users/edit/<int:user_id>', methods=['GET', 'POST'])
@admin_required
def admin_edit_user(user_id):
    user = User.query.get_or_404(user_id)
    if request.method == 'POST':
        # --- 表单验证 ---
        username = request.form.get('username')
        email = request.form.get('email')
        phone = request.form.get('phone')
        bio = request.form.get('bio')
        location = request.form.get('location')
        occupation = request.form.get('occupation')
        if not username or not email:
            flash('用户名和邮箱不能为空。', 'danger')
            return render_template('admin/edit_user.html', user=user)
        existing_user = User.query.filter(User.username == username, User.id != user_id).first()
        if existing_user:
            flash('用户名已存在，请选择其他用户名。', 'danger')
            return render_template('admin/edit_user.html', user=user)
        existing_email = User.query.filter(User.email == email, User.id != user_id).first()
        if existing_email:
            flash('邮箱已存在，请选择其他邮箱。', 'danger')
            return render_template('admin/edit_user.html', user=user)
        # --- 更新用户信息 ---
        try:
            user.username = username
            user.email = email
            user.phone = phone
            user.bio = bio
            user.location = location
            user.occupation = occupation
            # 更新头像（如果提供了新头像）
            if 'avatar_file' in request.files:
                avatar_file = request.files['avatar_file']
                if avatar_file.filename != '':  # 确保有文件被选择
                    filename = secure_filename(avatar_file.filename)  # 使用 secure_filename
                    upload_folder = os.path.join(app.static_folder, 'images', 'avatars')  # 设置正确的上传路径
                    os.makedirs(upload_folder, exist_ok=True)  # 确保目录存在
                    avatar_file.save(os.path.join(upload_folder, filename))
                    user.avatar_file = filename  # 保存相对路径
            db.session.commit()
            app.logger.info(f"管理员编辑了用户 (用户名: {username})")
            flash('用户信息已更新。', 'success')
            return redirect(url_for('admin_users'))
        except Exception as e:
            db.session.rollback()
            app.logger.error(f"更新用户 (ID: {user_id}) 信息时出错: {e}")
            flash('更新用户信息时发生错误。', 'danger')
    return render_template('admin/edit_user.html', user=user)


@app.route('/admin/users/delete/<int:user_id>', methods=['POST'])
@admin_required
def admin_delete_user(user_id):
    user = User.query.get_or_404(user_id)
    try:
        db.session.delete(user)
        db.session.commit()
        app.logger.info(f"管理员删除了用户 (ID: {user_id})")
        flash('用户已删除。', 'success')
    except Exception as e:
        db.session.rollback()
        app.logger.error(f"删除用户 (ID: {user_id}) 时出错: {e}")
        flash('删除用户时发生错误。', 'danger')

    return redirect(url_for('admin_users'))


@app.route('/admin/users/create', methods=['GET', 'POST'])
@admin_required
def admin_create_user():
    if request.method == 'POST':
        # --- 表单验证 ---
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        phone = request.form.get('phone')
        bio = request.form.get('bio')
        location = request.form.get('location')
        occupation = request.form.get('occupation')

        if not username:
            flash('用户名不能为空', 'danger')
            return render_template("admin/create_user.html", username=username, email=email, phone=phone, bio=bio,
                                   location=location, occupation=occupation)
        if not email:
            flash('邮箱不能为空', 'danger')
            return render_template("admin/create_user.html", username=username, email=email, phone=phone, bio=bio,
                                   location=location, occupation=occupation)
        if not password:
            flash('密码不能为空', 'danger')
            return render_template("admin/create_user.html", username=username, email=email, phone=phone, bio=bio,
                                   location=location, occupation=occupation)

        if User.query.filter_by(username=username).first():
            flash('用户名已存在，请选择其他用户名', 'danger')
            return render_template("admin/create_user.html", username=username, email=email, phone=phone, bio=bio,
                                   location=location, occupation=occupation)
        if User.query.filter_by(email=email).first():
            flash('邮箱已存在', 'danger')
            return render_template("admin/create_user.html", username=username, email=email, phone=phone, bio=bio,
                                   location=location, occupation=occupation)

        # --- 创建新用户 ---
        try:
            new_user = User(username=username, email=email)
            new_user.set_password(password)  # 设置哈希密码
            new_user.phone = phone
            new_user.bio = bio
            new_user.location = location
            new_user.occupation = occupation
            # 头像处理
            if 'avatar_file' in request.files:
                avatar_file = request.files['avatar_file']
                if avatar_file and avatar_file.filename:
                    filename = secure_filename(f"avatar_{username}_{int(time.time())}.jpg")
                    upload_folder = app.config['UPLOAD_FOLDER']
                    os.makedirs(upload_folder, exist_ok=True)
                    file_path = os.path.join(upload_folder, filename)
                    avatar_file.save(file_path)
                    new_user.avatar_file = filename
            db.session.add(new_user)
            db.session.commit()
            app.logger.info(f"管理员创建了新用户 (用户名: {username})")
            flash('新用户创建成功。', 'success')
            return redirect(url_for('admin_users'))
        except Exception as e:
            db.session.rollback()
            app.logger.error(f"创建新用户时出错: {e}")
            flash('创建新用户时发生错误。', 'danger')
            return render_template("admin/create_user.html", username=username, email=email, phone=phone, bio=bio,
                                   location=location, occupation=occupation)
    return render_template("admin/create_user.html")


# 显示所有用户反馈
@app.route('/admin/feedback', methods=['GET'])
@admin_required
def admin_feedback():
    """显示所有用户反馈."""

    feedbacks = Feedback.query.order_by(Feedback.timestamp.desc()).all()
    user_dict = {}
    for feedback in feedbacks:
        if feedback.user_id:
            user = User.query.get(feedback.user_id)
            user_dict[feedback.id] = user
        else:
            user_dict[feedback.id] = None  # 匿名用户

    return render_template('admin/feedback.html', feedbacks=feedbacks, user_dict=user_dict)


# 删除反馈路由
@app.route('/admin/feedback/delete/<int:feedback_id>', methods=['POST'])
@login_required
def delete_feedback(feedback_id):
    """删除指定ID的反馈."""

    feedback = Feedback.query.get_or_404(feedback_id)
    db.session.delete(feedback)
    db.session.commit()
    flash("反馈已成功删除。", 'success')
    return redirect(url_for('admin_feedback'))


# 系统状态 (路由不变，但渲染合并后的模板)
@app.route('/admin/system-status')
@admin_required
def admin_system_status():
    try:
        # 获取系统状态信息
        status = {
            'db_records': {
                'weather_data': db.session.query(WeatherData).count(),
                'forecasts': db.session.query(WeatherForecast).count(),
                'hourly_forecasts': db.session.query(HourlyForecast).count(),
                'region_temperatures': db.session.query(RegionTemperature).count()
            },
            'trained_models': len([f for f in os.listdir('models') if f.endswith('.pkl')]),
            'system_info': {
                'python_version': sys.version,
                'platform': platform.platform(),
                'memory_usage': psutil.Process().memory_info().rss / 1024 / 1024,  # MB
                'cpu_usage': psutil.cpu_percent(interval=0.2),  # 采样0.2秒，获取真实值
                'disk_usage': psutil.disk_usage('/').percent
            }
        }
        
        # 获取最近的系统日志
        log_file = 'logs/app.log'
        system_logs = []
        if os.path.exists(log_file):
            try:
                with open(log_file, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
                    system_logs = lines[-50:] if len(lines) > 50 else lines
            except UnicodeDecodeError:
                try:
                    with open(log_file, 'r', encoding='gbk') as f:
                        lines = f.readlines()
                        system_logs = lines[-50:] if len(lines) > 50 else lines
                except:
                    system_logs = ["无法读取日志文件"]
        system_logs = ''.join(system_logs)
        
        return render_template('admin/system_status.html', 
                             status=status,
                             system_logs=system_logs)
    except Exception as e:
        flash(f'获取系统状态时出错: {str(e)}', 'error')
        return redirect(url_for('admin_dashboard'))

@app.route('/admin/system-settings', methods=['GET', 'POST'])
@admin_required
def admin_system():
    # 获取系统状态信息
    try:
        status = {
            'db_records': {
                'weather_data': db.session.query(WeatherData).count(),
                'forecasts': db.session.query(WeatherForecast).count(),
                'hourly_forecasts': db.session.query(HourlyForecast).count(),
                'region_temperatures': db.session.query(RegionTemperature).count()
            },
            'trained_models': len([f for f in os.listdir('models') if f.endswith('.pkl')]),
            'system_info': {
                'python_version': sys.version,
                'platform': platform.platform(),
                'memory_usage': psutil.Process().memory_info().rss / 1024 / 1024,  # MB
                'cpu_usage': psutil.cpu_percent(interval=0.2),  # 采样0.2秒，获取真实值
                'disk_usage': psutil.disk_usage('/').percent
            }
        }
        
        # 获取最近的系统日志
        log_file = 'logs/app.log'
        system_logs = []
        if os.path.exists(log_file):
            try:
                with open(log_file, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
                    system_logs = lines[-50:] if len(lines) > 50 else lines
            except UnicodeDecodeError:
                try:
                    with open(log_file, 'r', encoding='gbk') as f:
                        lines = f.readlines()
                        system_logs = lines[-50:] if len(lines) > 50 else lines
                except:
                    system_logs = ["无法读取日志文件"]
        system_logs = ''.join(system_logs)
    except Exception as e:
        status = {
            'db_records': {'weather_data': 0, 'forecasts': 0, 'hourly_forecasts': 0, 'region_temperatures': 0},
            'trained_models': 0,
            'system_info': {
                'python_version': '未知',
                'platform': '未知',
                'memory_usage': 0,
                'cpu_usage': 0,
                'disk_usage': 0
            }
        }
        system_logs = [f"获取系统状态时出错: {str(e)}"]

    # 获取系统设置
    settings = SystemSetting.query.first()
    if not settings:
        settings = SystemSetting()
        db.session.add(settings)
        db.session.commit()

    # 创建表单
    system_form = SystemSettingsForm(obj=settings)
    email_form = EmailSettingsForm(obj=settings)
    backup_form = DatabaseBackupForm()
    auto_backup_form = AutoBackupForm(obj=settings)

    # 获取备份文件列表
    backup_folder = current_app.config.get('BACKUP_FOLDER', 'backups')
    backup_path = os.path.join(current_app.root_path, backup_folder)
    backups = []
    if os.path.exists(backup_path):
        backups = [f for f in os.listdir(backup_path) if f.endswith('.sql')]
        backups.sort(key=lambda x: os.path.getmtime(os.path.join(backup_path, x)), reverse=True)

    if request.method == 'POST':
        form_type = request.form.get('form_type')
        
        if form_type == 'system_settings' and system_form.validate_on_submit():
            system_form.populate_obj(settings)
            # 处理logo上传
            if system_form.system_logo.data:
                file = system_form.system_logo.data
                from werkzeug.utils import secure_filename
                filename = secure_filename(file.filename)
                logo_folder = os.path.join(app.static_folder, 'images', 'logos')
                os.makedirs(logo_folder, exist_ok=True)
                save_path = os.path.join(logo_folder, filename)
                file.save(save_path)  # 以二进制方式安全保存
                settings.system_logo = filename
            db.session.commit()
            flash('系统设置已更新', 'success')
            return redirect(url_for('admin_system'))
            
        elif form_type == 'email_settings' and email_form.validate_on_submit():
            email_form.populate_obj(settings)
            db.session.commit()
            flash('邮件设置已更新', 'success')
            return redirect(url_for('admin_system'))
            
        elif form_type == 'auto_backup' and auto_backup_form.validate_on_submit():
            auto_backup_form.populate_obj(settings)
            db.session.commit()
            flash('自动备份设置已更新', 'success')
            return redirect(url_for('admin_system'))

    return render_template('admin/system_settings.html',
                         system_form=system_form,
                         email_form=email_form,
                         backup_form=backup_form,
                         auto_backup_form=auto_backup_form,
                         settings=settings,
                         backups=backups,
                         status=status,
                         system_logs=system_logs)

# 数据库备份路径
BACKUP_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'backups')
if not os.path.exists(BACKUP_FOLDER):
    os.makedirs(BACKUP_FOLDER)


# 添加数据库恢复功能
@app.route('/admin/restore_database/<filename>', methods=['GET', 'POST'])
@admin_required
def restore_database(filename):
    close_all_db_connections()
    try:
        app.logger.info(f"开始恢复数据库，文件名: {filename}")
        
        # 安全检查：确保文件名不包含路径注入
        if '../' in filename or '/' in filename:
            error_msg = '非法文件名'
            app.logger.error(error_msg)
            if request.method == 'POST':
                return jsonify({'type': 'error', 'message': error_msg})
            flash(error_msg, 'danger')
            return redirect(url_for('admin_system',_anchor="backup"))
        
        # 构建完整的备份文件路径
        backup_file = os.path.join(BACKUP_FOLDER, filename)
        app.logger.info(f"备份文件完整路径: {backup_file}")

        if not os.path.exists(backup_file):
            error_msg = f'备份文件不存在: {backup_file}'
            app.logger.error(error_msg)
            if request.method == 'POST':
                return jsonify({'type': 'error', 'message': error_msg})
            flash(error_msg, 'danger')
            return redirect(url_for('admin_system',_anchor="backup"))

        # 获取数据库连接信息
        db_user = app.config.get('MYSQL_USER', 'root')
        db_password = app.config.get('MYSQL_PASSWORD', 'fumo666')
        db_name = app.config.get('MYSQL_DB', 'weather_system_db')
        db_host = app.config.get('MYSQL_HOST', 'localhost')
        
        app.logger.info(f"数据库连接信息 - 主机: {db_host}, 数据库: {db_name}, 用户: {db_user}")

        # 构建mysql命令来恢复数据库
        cmd = [
            'mysql',
            f'--user={db_user}',
            f'--password={db_password}',
            f'--host={db_host}',
            db_name,
            f'<{backup_file}'
        ]
        
        app.logger.info(f"执行恢复命令: {' '.join(cmd)}")
        
        # 执行恢复命令
        result = subprocess.run(' '.join(cmd), shell=True, capture_output=True, text=True)
        
        if result.returncode == 0:
            success_msg = '数据库恢复成功!'
            app.logger.info(success_msg)
            if request.method == 'POST':
                return jsonify({'type': 'success', 'message': success_msg})
            flash(success_msg, 'success')
        else:
            error_message = result.stderr or '未知错误'
            error_msg = f'数据库恢复失败: {error_message}'
            app.logger.error(f"恢复失败 - 错误码: {result.returncode}, 错误信息: {error_message}")
            if request.method == 'POST':
                return jsonify({'type': 'error', 'message': error_msg})
            flash(error_msg, 'danger')
        
        return redirect(url_for('admin_system',_anchor="backup"))
    except Exception as e:
        error_msg = f'恢复过程中出错: {str(e)}'
        app.logger.error(f"恢复过程中发生异常: {str(e)}", exc_info=True)
        if request.method == 'POST':
            return jsonify({'type': 'error', 'message': error_msg})
        flash(error_msg, 'danger')
        return redirect(url_for('admin_system',_anchor="backup"))

# 列出所有备份文件
@app.route('/admin/list_backups')
@admin_required
def admin_list_backups():
    try:
        backup_folder = current_app.config.get('BACKUP_FOLDER', 'backups')
        backup_path = os.path.join(current_app.root_path, backup_folder)
        backups = []
        if os.path.exists(backup_path):
            backups = [f for f in os.listdir(backup_path) if f.endswith('.sql')]
            backups.sort(key=lambda x: os.path.getmtime(os.path.join(backup_path, x)), reverse=True)
        return jsonify(backups)
    except Exception as e:
        return jsonify({
            'type': 'error',
            'message': f'获取备份列表失败: {str(e)}'
        })

# 清除缓存
@app.route('/admin/clear-cache')
@admin_required
def admin_clear_cache():
    try:
        app.logger.info('开始清除系统缓存')
        seven_days_ago = datetime.now() - timedelta(days=7)

        deleted_temps = RegionTemperature.query.filter(RegionTemperature.update_time < seven_days_ago).delete()
        db.session.commit()
        app.logger.info(f'已清除 {deleted_temps} 条区域温度缓存数据')

        deleted_hourly = HourlyForecast.query.filter(HourlyForecast.update_time < seven_days_ago).delete()
        deleted_daily = WeatherForecast.query.filter(WeatherForecast.update_time < seven_days_ago.date()).delete()
        db.session.commit()
        app.logger.info(f'已清除 {deleted_hourly} 条小时预报和 {deleted_daily} 条天气预报缓存数据')

        flash(
            f'已成功清除过期缓存数据 ({deleted_temps}条区域温度数据, {deleted_hourly}条小时预报, {deleted_daily}条天气预报)',
            'success')
    except Exception as e:
        db.session.rollback()
        app.logger.error(f'清除缓存失败: {str(e)}')
        flash(f'清除缓存失败: {str(e)}', 'danger')
    return redirect(url_for('admin_system',_anchor="status"))

# 更新省份数据
@app.route('/admin/update-provinces')
@admin_required
def admin_update_provinces():
    try:
        # 调用更新省份温度的函数
        update_provinces_temperature()
        flash('省份温度数据已成功更新', 'success')
    except Exception as e:
        flash(f'更新省份数据失败: {str(e)}', 'danger')
    return redirect(url_for('admin_system',_anchor="status"))

# 重新训练模型
@app.route('/admin/retrain-model/<city>')
@admin_required
def admin_retrain_model(city):
    try:
        # 使用完整流程进行训练
        result = predictor.run_full_pipeline(city, retrain=True)
        if result is not None:
            flash(f'{city}的天气预测模型训练成功', 'success')
        else:
            flash(f'{city}的天气预测模型训练失败，可能数据不足', 'warning')
    except Exception as e:
        flash(f'训练模型失败: {str(e)}', 'danger')
    return redirect(url_for('admin_prediction_models'))

def get_db_connection_params(db_uri):
    db_type, rest = db_uri.split("://", 1)
    if db_type == "mysql+pymysql":
        user, password_host_db = rest.split(":", 1)
        password, host_db = password_host_db.split("@", 1)
        host, database = host_db.split("/", 1)
        try:
            port, host = host.split(":")
        except ValueError:
            port = "3306"
        return host, port, user, password, database
    else:
        return None

# 手动备份
@app.route('/admin/backup', methods=['POST'])
@admin_required
def backup_database():
    close_all_db_connections()
    try:
        backup_description = request.form.get('backup_description', '').strip()
        app.logger.info(f'开始数据库备份，描述: {backup_description}')
        
        db_user = app.config.get('MYSQL_USER', 'root')
        db_password = app.config.get('MYSQL_PASSWORD', 'fumo666')
        db_name = app.config.get('MYSQL_DB', 'weather_system_db')
        db_host = app.config.get('MYSQL_HOST', 'localhost')

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        if backup_description:
            backup_description = re.sub(r'[\\/:*?"<>|]', '_', backup_description)
            backup_description = backup_description.replace(' ', '_')
            filename = f"backup_weather_system_db_{timestamp}_{backup_description}.sql"
        else:
            filename = f"backup_weather_system_db_{timestamp}_{secrets.token_hex(4)}.sql"

        backup_file = os.path.join(BACKUP_FOLDER, filename)

        cmd = [
            'mysqldump',
            f'--user={db_user}',
            f'--password={db_password}',
            f'--host={db_host}',
            '--single-transaction',
            '--quick',
            '--lock-tables=false',
            db_name,
            f'> {backup_file}'
        ]

        result = subprocess.run(' '.join(cmd), shell=True, capture_output=True, text=True)

        if result.returncode == 0:
            app.logger.info(f'数据库备份成功: {filename}')
            return jsonify({
                'type': 'success',
                'message': f'数据库备份成功: {filename}'
            })
        else:
            error_message = result.stderr or '未知错误'
            app.logger.error(f'数据库备份失败: {error_message}')
            return jsonify({
                'type': 'error',
                'message': f'数据库备份失败: {error_message}'
            })
    except Exception as e:
        app.logger.error(f'备份过程中出错: {str(e)}', exc_info=True)
        return jsonify({
            'type': 'error',
            'message': f'备份过程中出错: {str(e)}'
        })

def close_all_db_connections():
    db.session.close()
    db.engine.dispose()


# 简化的自动备份函数
def perform_auto_backup():
    with current_app.app_context():
        settings = SystemSetting.query.first()
        if settings and settings.auto_backup_enabled:
            try:
                backup_folder = current_app.config.get('BACKUP_FOLDER', 'backups')
                backup_path = os.path.join(current_app.root_path, backup_folder)
                os.makedirs(backup_path, exist_ok=True)
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                backup_file = f"auto_backup_weather_system_db_{timestamp}_{secrets.token_hex(4)}.sql"  # 自动备份也加上随机后缀
                full_backup_path = os.path.join(backup_path, backup_file)

                db_uri = current_app.config['SQLALCHEMY_DATABASE_URI']
                db_params = get_db_connection_params(db_uri)
                if db_params:
                    host, port, user, password, database = db_params
                    command = [
                        "mysqldump",
                        "-h", host,
                        "-P", port,
                        "-u", user,
                        f"-p{password}",
                        database
                    ]
                    with open(full_backup_path, 'w', encoding='utf-8') as f:
                         result = subprocess.run(command, stdout=f, stderr=subprocess.PIPE, text=True) #直接写入

                    if result.returncode != 0:
                        print(f"自动备份失败: {result.stderr}")
                    else:
                        print(f"自动备份成功: {backup_file}")
                else:
                    print(f"自动备份失败: 仅支持 MySQL")

            except subprocess.SubprocessError as e:  # 捕获特定异常
                print(f"自动备份失败: {e}")
            except OSError as e:
                print(f"自动备份创建目录失败: {e}")

# 生成报告
@app.route('/admin/generate-report')
@admin_required
def admin_generate_report():
    try:
        # 获取当前时间
        current_time = datetime.now()
        
        # 获取统计数据
        weather_data_count = db.session.query(CleanedHistoricalWeather).count()
        city_count = db.session.query(CleanedHistoricalWeather.city_name).distinct().count()
        region_count = db.session.query(RegionTemperature).count()
        model_count = len([f for f in os.listdir(predictor.model_path) if f.endswith('.joblib')]) if os.path.exists(predictor.model_path) else 0
        
        # 获取最近的天气数据
        recent_weather = CleanedHistoricalWeather.query.order_by(CleanedHistoricalWeather.date.desc()).limit(10).all()
        
        # 获取最近的预报数据
        recent_forecast = WeatherForecast.query.order_by(WeatherForecast.fx_date.desc()).limit(10).all()
        
        # 获取系统状态
        status = {
            'db_records': {
                'weather_data': weather_data_count,
                'forecasts': WeatherForecast.query.count(),
                'hourly_forecasts': HourlyForecast.query.count(),
                'region_temperatures': region_count
            },
            'trained_models': model_count
        }
        
        # 生成报告文本内容
        report_content = f"""天气系统状态报告
生成时间: {current_time.strftime('%Y-%m-%d %H:%M:%S')}
{'='*50}

系统概况:
- 总天气数据记录: {weather_data_count}
- 覆盖城市数量: {city_count}
- 区域温度记录: {region_count}
- 训练模型数量: {model_count}

数据库记录统计:
- 天气数据: {status['db_records']['weather_data']}
- 天气预报: {status['db_records']['forecasts']}
- 小时预报: {status['db_records']['hourly_forecasts']}
- 区域温度: {status['db_records']['region_temperatures']}

最近天气记录:
{'='*50}"""

        # 添加最近的天气数据
        for weather in recent_weather:
            report_content += f"""
日期: {weather.date}
城市: {weather.city_name}
最高温度: {weather.temp_max}°C
最低温度: {weather.temp_min}°C
天气: {weather.weather}
风向: {weather.wind_dir}
{'- '*25}"""

        report_content += f"""
\n最近天气预报:
{'='*50}"""

        # 添加最近的预报数据
        for forecast in recent_forecast:
            report_content += f"""
预报日期: {forecast.fx_date}
城市: {forecast.city}
最高温度: {forecast.temp_max}°C
最低温度: {forecast.temp_min}°C
天气: {forecast.text_day}
风力等级: {forecast.wind_scale}
{'- '*25}"""
        
        # 生成文件名
        filename = f"weather_system_report_{current_time.strftime('%Y%m%d_%H%M%S')}.txt"
        
        # 创建响应
        response = make_response(report_content)
        response.headers['Content-Type'] = 'text/plain; charset=utf-8'
        response.headers['Content-Disposition'] = f'attachment; filename={filename}'
        
        return response
        
    except Exception as e:
        flash(f'生成报告时发生错误：{str(e)}', 'error')
        return redirect(url_for('admin_dashboard'))

# 词云图部分
WEATHER_KEYWORDS_MAP = {
    "晴": ["阳光明媚", "万里无云", "蓝天", "好天气", "温暖", "干燥", "晴朗"],
    "多云": ["云彩", "天空云量多", "有时有阳光", "阴晴不定", "云层"],
    "阴": ["阴天", "天色昏暗", "无阳光", "云层密布", "灰蒙蒙"],
    "小雨": ["毛毛雨", "细雨", "零星降水", "阵雨", "潮湿", "雨滴", "湿润", "雨具"],
    "中雨": ["雨水", "持续降雨", "雨量适中", "路面湿滑", "雨天"],
    "大雨": ["倾盆大雨", "暴雨", "雨势强劲", "积水", "雨幕", "洪水风险"],
    "雷阵雨": ["雷电", "闪电", "雷鸣", "阵性降水", "强对流", "夏季午后", "雷雨"],
    "雨夹雪": ["湿雪", "雨雪混合", "泥泞", "冻雨", "冰冷"],
    "小雪": ["雪花", "飘雪", "轻微降雪", "寒冷"],
    "中雪": ["雪景", "降雪", "积雪", "冬天"],
    "大雪": ["鹅毛大雪", "雪量大", "银装素裹", "雪白", "暴雪"],
    "雾": ["大雾", "能见度低", "迷雾", "白茫茫", "湿气重", "行车安全"],
    "霾": ["雾霾", "空气污染", "PM2.5", "灰霾", "能见度差", "戴口罩"],
    "沙尘暴": ["沙尘", "黄沙漫天", "风沙", "空气质量差", "土味"],
    "浮尘": ["扬沙", "轻微沙尘", "风"],
    "扬沙": ["风沙", "能见度下降"],
}


@app.route('/weather_wordcloud/<city>')
def get_weather_wordcloud(city):
    try:
        # 1. 获取该城市的所有历史天气数据
        weather_data = CleanedHistoricalWeather.query.filter(
            CleanedHistoricalWeather.city_name == city
        ).order_by(CleanedHistoricalWeather.date.desc()).all()

        if not weather_data:
             return jsonify({'status': 'success', 'data': [], 'total_days': 0, 'message': '未找到该城市的历史天气数据'})

        # 2. 使用 Counter 统计词频
        wordcloud_counter = Counter()
        processed_records = 0

        for record in weather_data:
            processed_records += 1

            if record.weather:
                # Handle descriptions like "晴转多云" or "小雨、阵雨"
                conditions = record.weather.replace('转', '、').split('、')
                for condition in conditions:
                    condition = condition.strip()
                    if condition:  # Ensure not empty

                        wordcloud_counter[condition] += 1

                        related_keywords = WEATHER_KEYWORDS_MAP.get(condition, [])
                        for keyword in related_keywords:
                            wordcloud_counter[keyword] += 1 

            if record.wind_dir:
                wind_direction = record.wind_dir.strip()
                if wind_direction: # Ensure not empty
                    wordcloud_counter[wind_direction] += 1

        
        min_frequency = 2 # 仅包含出现至少两次的单词
        filtered_word_freq = {word: freq for word, freq in wordcloud_counter.items() if freq >= min_frequency}

        # 转换为 ECharts Wordcloud 所需的列表格式
        wordcloud_data = [{'name': word, 'value': freq} for word, freq in filtered_word_freq.items()]

        # 按频率降序排序
        wordcloud_data.sort(key=lambda x: x['value'], reverse=True)

        # 限制发送给前端的单词数量
        max_words = 150 # 限制为前 150 个单词
        wordcloud_data = wordcloud_data[:max_words]

        print(f"为 {city} 生成词云，源数据 {len(weather_data)} 条, 处理后词语 {len(wordcloud_data)} 个")

        return jsonify({
            'status': 'success',
            'data': wordcloud_data,
            'total_days': len(weather_data) # 保留 total_days 如果前端使用它
        })

    except Exception as e:
        # 记录错误用于调试
        print(f"生成 {city} 词云时出错: {e}")
        import traceback
        traceback.print_exc() # 打印详细回溯
        return jsonify({
            'status': 'error',
            'message': f'生成天气词云时出错: {str(e)}'
        }), 500

@app.route('/compare')
def compare_page():
    return render_template('compare.html')

@app.route('/api/weather/compare', methods=['GET'])
def compare_weather_data():
    """对比多个城市或时间段的天气数据"""
    cities = request.args.getlist('city')  # 支持多个城市参数
    start = request.args.get('start')
    end = request.args.get('end')
    metrics = request.args.get('metrics', 'temp_max,temp_min')  # 默认对比最高最低温
    
    if not cities:
        return jsonify({'status': 'error', 'message': '至少需要选择一个城市'}), 400
    
    # 查询每个城市的数据
    results = {}
    for city in cities:
        query = CleanedHistoricalWeather.query.filter(
            CleanedHistoricalWeather.city_name.ilike(f"%{city}%")
        )
        
        if start and end:
            query = query.filter(CleanedHistoricalWeather.date.between(start, end))
        
        data = query.order_by(CleanedHistoricalWeather.date.asc()).all()
        
        results[city] = [{
            'date': item.date.strftime('%Y-%m-%d'),
            'temp_max': item.temp_max,
            'temp_min': item.temp_min,
            'weather': item.weather
        } for item in data]
    
    return jsonify({
        'status': 'success',
        'data': results,
        'metrics': metrics.split(',')
    })

@app.route('/weather_analysis/<city>')
def weather_analysis(city):
    """
    天气数据分析页面
    展示：
    1. 温度趋势分析
    2. 季节性模式
    3. 天气模式分析
    4. 异常天气事件
    """
    try:
        predictor = WeatherPredictor()  # 创建预测器实例
        analysis_report = predictor.generate_analysis_report(city)  # 生成分析报告
        return jsonify({
            'status': 'success',
            'data': analysis_report
        })
    except Exception as e:
        current_app.logger.error("分析失败: %s", str(e), exc_info=True) # 记录错误
        return jsonify({
            'status': 'error',
            'message': f'分析失败: {str(e)}'
        }), 500

@app.route('/analysis_view')
def analysis_view():
    return render_template('analysis_view.html')

# 删除账号API
@app.route('/profile/delete_account', methods=['POST'])
@login_required
def delete_account():
    try:
        data = request.get_json() # 获取请求数据
        password = data.get('password') # 获取密码
        if not password or not current_user.check_password(password): # 检查密码
            return jsonify({'success': False, 'message': '密码错误'}), 400
        user_id = current_user.id
        # 删除相关数据（如活动、收藏、历史等）
        UserActivity.query.filter_by(user_id=user_id).delete()
        FavoriteLocation.query.filter_by(user_id=user_id).delete()
        SearchHistory.query.filter_by(user_id=user_id).delete()
        Feedback.query.filter_by(user_id=user_id).delete()
        # 删除用户本身
        user = User.query.get(user_id)
        if user:
            db.session.delete(user) # 删除用户
        db.session.commit() # 提交事务
        logout_user() # 注销用户
        return jsonify({'success': True}) # 返回成功
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500

# 从数据库获取系统设置
@app.context_processor
def inject_now():
    settings = SystemSetting.query.first()
    return {
        'now': datetime.now,
        'system_name': settings.system_name if settings and settings.system_name else '天气数据管理系统'
    }


if __name__ == '__main__':
    app.run(debug=True)

