# utils/weather_api.py

import requests
from datetime import datetime
from config import Config

def get_location_id(city_name):
    search_url = "https://geoapi.qweather.com/v2/city/lookup"
    params = {
        "key": Config.HEFENG_API_KEY,
        "location": city_name,
        "lang": "zh",
        "range": "cn"
    }

    try:
        response = requests.get(search_url, params=params)
        response.raise_for_status()
        data = response.json()

        if data['code'] == '200' and data.get('location'):
            location = data['location'][0]
            return location['id'], location['name']  # 返回ID和中文名
        return None, None
    except Exception as e:
        print(f"位置查询异常: {str(e)}")
        return None, None

"""获取未来24小时预报"""
def get_hourly_forecast(city):
    location_id = get_location_id(city)
    if not location_id:
        return None

    base_url = "https://devapi.qweather.com/v7/weather/24h"
    params = {
        "key": Config.HEFENG_API_KEY,
        "location": location_id,
        "lang": "zh"
    }

    try:
        response = requests.get(base_url, params=params)
        response.raise_for_status()
        data = response.json()
        print("24小时预报响应:", data)

        if data['code'] == '200' and len(data['hourly']) > 0:
            hourly_data = []

            for hour in data['hourly'][:24]:  # 取前24小时
                # 安全地处理可能为空的字段
                pop = hour.get('pop')
                pop = float(pop) if pop is not None else None

                cloud = hour.get('cloud')
                cloud = float(cloud) if cloud is not None else None

                dew = hour.get('dew')
                dew = float(dew) if dew is not None else None

                hourly_item = {
                    'fx_time': datetime.strptime(hour['fxTime'], '%Y-%m-%dT%H:%M+08:00'),
                    'temp': float(hour['temp']),
                    'icon': hour['icon'],
                    'text': hour['text'],
                    'wind360': float(hour['wind360']),
                    'wind_dir': hour['windDir'],
                    'wind_scale': hour['windScale'],
                    'wind_speed': float(hour['windSpeed']),
                    'humidity': float(hour['humidity']),
                    'precip': float(hour['precip']),
                    'pop': pop,
                    'pressure': float(hour['pressure']),
                    'cloud': cloud,
                    'dew': dew
                }

                hourly_data.append(hourly_item)

            return hourly_data

        return None

    except Exception as e:
        print(f"24小时预报请求失败: {str(e)}")
        return None


# 获取实时天气信息
def get_current_weather_data(city):
    location_id, city_name = get_location_id(city)
    if not location_id:
        return None

    base_url = "https://devapi.qweather.com/v7/weather/now"
    params = {
        "key": Config.HEFENG_API_KEY,
        "location": location_id,
        "lang": "zh"
    }

    try:
        response = requests.get(base_url, params=params)
        response.raise_for_status()
        data = response.json()
        print("实时天气API响应:", data)  # 调试日志

        if data['code'] == '200' and 'now' in data:
            # 提取实时天气数据
            now = data['now']
            return {
                'city': city_name,
                'update_time': datetime.fromisoformat(data['updateTime'].replace('+08:00', '')),
                'obs_time': datetime.fromisoformat(now['obsTime'].replace('+08:00', '')),
                'temp': float(now['temp']),
                'feels_like': float(now['feelsLike']),
                'humidity': float(now['humidity']),
                'wind_speed': float(now['windSpeed']),
                'wind_dir': now['windDir'],
                'wind_scale': now['windScale'],
                'precip': float(now['precip']),
                'pressure': float(now['pressure']),
                'vis': float(now['vis']),
                'cloud': float(now['cloud']) if now.get('cloud') else None,
                'dew': float(now['dew']) if now.get('dew') else None,
                'text': now['text'],
                'icon': now['icon']
            }
        print(f"实时天气API错误: {data['code']} - {data.get('message')}")
        return None
    except Exception as e:
        print(f"API请求失败: {str(e)}")
        return None

"""获取7天天气预报"""
def fetch_weather_forecast(city):

    location_id = get_location_id(city)
    if not location_id:
        return None

    base_url = "https://devapi.qweather.com/v7/weather/7d"
    params = {
        "key": Config.HEFENG_API_KEY,
        "location": location_id,
        "lang": "zh"
    }

    try:
        response = requests.get(base_url, params=params)
        response.raise_for_status()

        print(f"【调试】API请求URL：{response.url}")  # 显示完整请求地址
        print(f"【调试】API响应状态码：{response.status_code}")  # 添加

        data = response.json()
        #print("天气预报响应:", data)
        print(f"【调试】原始API响应：{data}")  # 输出完整响应

        if data['code'] == '200' and len(data['daily']) >= 7:

            print(f"【调试】有效预报数据条数：{len(data.get('daily', []))}")

            forecast_days = data['daily'][:7]  # 取前3天
            return [
                {
                    'fx_date': datetime.strptime(day['fxDate'], '%Y-%m-%d').date(),
                    'temp_max': float(day['tempMax']),
                    'temp_min': float(day['tempMin']),
                    'icon_day': day['iconDay'],
                    'text_day': day['textDay'],
                    'wind_scale': day['windScaleDay'],
                    'humidity': float(day['humidity']),
                    'precip': float(day['precip'])
                }
                for day in forecast_days
            ]
        return None
    except Exception as e:
        print(f"预报API请求失败: {str(e)}")
        return None



"""逆地理编码API封装"""
def reverse_geocode_api(lat, lng):
    try:
        url = "https://geoapi.qweather.com/v2/city/lookup"
        params = {
            "key": Config.HEFENG_API_KEY,
            "location": f"{lng},{lat}",
            "lang": "zh",
            "number": 1
        }

        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()

        if data['code'] == '200' and data.get('location'):
            return {
                'status': 'success',
                'city': data['location'][0]['adm2'],
                'id': data['location'][0]['id']
            }

        return {
            'status': 'error',
            'message': data.get('message', '未知错误')
        }

    except requests.exceptions.RequestException as e:
        return {
            'status': 'error',
            'message': f"API请求失败: {str(e)}"
        }
    except Exception as e:
        return {
            'status': 'error',
            'message': f"系统错误: {str(e)}"
        }

