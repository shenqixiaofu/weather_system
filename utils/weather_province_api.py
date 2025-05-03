# utils/weather_province_api.py

import requests
from config import Config

# 中国34个省级行政区标准名称
PROVINCE_NAMES = [
    '北京市', '天津市', '河北省', '山西省', '内蒙古自治区',
    '辽宁省', '吉林省', '黑龙江省', '上海市', '江苏省',
    '浙江省', '安徽省', '福建省', '江西省', '山东省',
    '河南省', '湖北省', '湖南省', '广东省', '广西壮族自治区',
    '海南省', '重庆市', '四川省', '贵州省', '云南省',
    '西藏自治区', '陕西省', '甘肃省', '青海省', '宁夏回族自治区',
    '新疆维吾尔自治区', '台湾省', '香港特别行政区', '澳门特别行政区', '南海诸岛'
]


def get_location_id(api_key, province_name):
    """获取省级行政中心LocationID"""
    url = "https://geoapi.qweather.com/v2/city/lookup"
    params = {
        'location': province_name,
        'key': Config.HEFENG_API_KEY,
        'range': 'cn'
    }
    try:
        res = requests.get(url, params=params, timeout=10).json()
        if res['code'] == '200' and len(res['location']) > 0:
            # 优先匹配省级节点（部分省份如广东需特殊处理）
            for loc in res['location']:
                if loc['adm2'] == province_name:  # 匹配到省级节点
                    return loc['id']
            return res['location'][0]['id']  # 默认返回第一个
        return None
    except Exception as e:
        print(f"获取{province_name} LocationID失败: {str(e)}")
        return None


def fetch_all_provinces_weather():
    """获取全国所有省份天气数据"""
    weather_data = []

    for province in PROVINCE_NAMES:
        location_id = get_location_id(Config.HEFENG_API_KEY, province)
        if not location_id:
            print(f"未找到{province}的LocationID")
            continue

        # 获取3天天气预报（取当日数据）
        url = "https://devapi.qweather.com/v7/weather/3d"
        params = {
            'location': location_id,
            'key': Config.HEFENG_API_KEY
        }

        try:
            response = requests.get(url, params=params, timeout=15)
            response.raise_for_status()  # 检查HTTP错误
            res = response.json()

            if res['code'] == '200' and len(res['daily']) > 0:
                # 取当日数据（数组第一个元素）
                today = res['daily'][0]

                # 处理温度数据
                temp_max = int(today['tempMax'])
                temp_min = int(today['tempMin'])
                temp_avg = round((temp_max + temp_min) / 2, 1)  # 保留1位小数

                weather_data.append({
                    'name': province,
                    'temp_avg': temp_avg,
                    'temp_max': temp_max,
                    'temp_min': temp_min
                })

                print(f"成功获取{province}天气数据")
            else:
                print(f"获取{province}天气失败：{res.get('message', '未知错误')}")

        except requests.exceptions.Timeout:
            print(f"请求{province}天气超时")
        except requests.exceptions.RequestException as e:
            print(f"网络请求异常：{str(e)}")
        except (KeyError, ValueError) as e:
            print(f"解析{province}天气数据失败：{str(e)}")
        except Exception as e:
            print(f"处理{province}天气时发生意外错误：{str(e)}")

    return weather_data

