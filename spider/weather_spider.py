import os
import requests
from bs4 import BeautifulSoup
import random
import json
from datetime import datetime, date, timedelta
import hashlib
import time
import execjs
from urllib.parse import quote
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from models.historical_models import HistoricalWeather, db, NewHistoricalWeather
from .data_cleaner import DataCleaner  # 导入 DataCleaner

# 获取当前脚本的目录
current_dir = os.path.dirname(os.path.abspath(__file__))
# 构造文件的绝对路径
city_json_path = os.path.join(current_dir, 'city.json')
china_json_path = os.path.join(current_dir, 'china.json')
# 加载城市映射数据
with open(city_json_path, 'r', encoding='utf-8') as f:
    CITY_PINYIN = json.load(f)
with open(china_json_path, 'r', encoding='utf-8') as f:
    CITY_CODE = json.load(f)
USER_AGENTS = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:127.0) Gecko/20100101 Firefox/127.0',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 14_5) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.4 Safari/605.1.15',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36 Edg/125.0.0.0',
    'Mozilla/5.0 (Linux; Android 14; Pixel 8 Pro) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Mobile Safari/537.36',
    'Mozilla/5.0 (iPhone 15 Pro Max; CPU iPhone OS 17_5 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.4 Mobile/15E148 Safari/604.1',
    'Mozilla/5.0 (Linux; Android 14; SM-S928B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Mobile Safari/537.36',
    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Windows NT 11.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 14_5; rv:127.0) Gecko/20100101 Firefox/127.0'
]
# 动态代理池获取函数
def fetch_free_proxies():
    url = "https://www.proxy-list.download/api/v1/get?type=http"
    try:
        response = requests.get(url, timeout=15)
        if response.status_code == 200:
            proxies = response.text.splitlines()
            print(f"成功获取到 {len(proxies)} 个代理")
            return proxies
    except Exception as e:
        print(f"获取代理失败: {e}")
    return []
# 代理缓存
PROXY_POOL = []
PROXY_UPDATE_TIME = None
PROXY_UPDATE_INTERVAL = timedelta(minutes=30)  # 代理更新间隔：30 分钟
# 从代理池中随机选择一个代理
def get_random_proxy():
    """从代理池中获取随机代理，并定期更新代理池"""
    global PROXY_POOL, PROXY_UPDATE_TIME

    # 检查代理池是否需要更新
    if not PROXY_POOL or PROXY_UPDATE_TIME is None or datetime.now() - PROXY_UPDATE_TIME > PROXY_UPDATE_INTERVAL:
        print("更新代理池...")
        PROXY_POOL = fetch_free_proxies()
        PROXY_UPDATE_TIME = datetime.now()
        if not PROXY_POOL:
            print("代理池为空，无法使用代理")
            return None

    if PROXY_POOL:
        return {'http': random.choice(PROXY_POOL)}
    else:
        print("代理池为空，无法使用代理")
        return None
def get_dynamic_cookies(city_pinyin):
    """生成动态cookie"""
    timestamp = int(time.time())
    return {
        'cityPy': city_pinyin,
        'cityPy_expire': str(timestamp + 7200),  # 2小时有效期
        'Hm_lvt_' + hashlib.md5(city_pinyin.encode()).hexdigest()[:8]: str(timestamp),
    }
def get_headers():
    return {
        'User-Agent': random.choice(USER_AGENTS),
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2',
        'Cache-Control': 'no-cache',
        'Sec-Fetch-Dest': 'document',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'same-origin',
        'Pragma': 'no-cache',
        'Sec-CH-UA': '"Chromium";v="116", "Not)A;Brand";v="24"',
        'Viewport-Width': str(random.randint(1200, 1920)),
        'Device-Memory': '8',
        'RTT': str(random.randint(50, 300)),
        'Connection': 'keep-alive',
        'Referer': 'https://www.tianqi.com/',
    }
# 全局配置 Session 和重试策略
session = requests.Session()
retries = Retry(
    total=3,
    backoff_factor=0.3,
    status_forcelist=[500, 502, 503, 504, 429]
)
session.mount('https://', HTTPAdapter(max_retries=retries))
def get_city_info():
    """生成城市信息映射表"""
    city_mapping = {}
    for ch_name, pinyin in CITY_PINYIN.items():
        code = CITY_CODE.get(ch_name)
        if code:
            city_mapping[ch_name] = {
                'code': code,
                'pinyin': pinyin.lower()  # 转换为小写匹配URL
            }
    return city_mapping

CITY_INFO = get_city_info()

def fetch_month_data_first(city_name, year, month):
    """抓取一个月前10天的天气数据"""
    city_data = CITY_INFO.get(city_name)
    if not city_data:
        print(f"未找到城市配置: {city_name}")
        return []
    pinyin_encoded = quote(city_data['pinyin'])
    url = f"https://lishi.tianqi.com/{pinyin_encoded}/{year}{month:02d}.html"
    data_list = []
    proxy_retries = 3  # 代理重试次数
    for attempt in range(proxy_retries):
        proxy = get_random_proxy() if True else None # 无代理时设为None
        try:
            # 添加随机延迟
            time.sleep(random.uniform(5, 15))
            response = session.get(
                url,
                headers=get_headers(),
                cookies=get_dynamic_cookies(city_data['pinyin']),
                proxies=proxy,
                timeout=15
            )
            response.encoding = 'utf-8'
            if response.status_code != 200:
                print(f"请求被拒绝: {url} 状态码 {response.status_code}")
                continue # 失败后直接进行下一次尝试
            if "error.png" in response.text:
                print(f"可能触发反爬机制，当前代理：{proxy}，尝试更换代理")
                continue
            soup = BeautifulSoup(response.text, 'lxml')
            # 修正选择器为实际的每日数据容器
            daily_container = soup.find('ul', class_='thrui')
            if not daily_container:
                print(f"未找到每日数据容器: {url}")
                return []
            # 解析每日数据
            for day in daily_container.find_all('li'):
                cols = day.find_all('div')
                if len(cols) < 5:  # 根据实际列数调整
                    continue
                try:
                    # 解析日期（去除星期信息）
                    date_str = cols[0].text.strip().split()[0]
                    # 解析温度数据
                    high_temp = float(cols[1].text.replace('℃', ''))
                    low_temp = float(cols[2].text.replace('℃', ''))
                    # 解析天气和风向风力
                    weather = cols[3].text.strip()
                    wind_info = cols[4].text.strip().split()
                    record = {
                        'city_code': city_data['code'],
                        'city_name': city_name,
                        'date': datetime.strptime(date_str, '%Y-%m-%d'),
                        'temp_max': high_temp,
                        'temp_min': low_temp,
                        'weather': weather,
                        'wind_dir': wind_info[0] if len(wind_info) > 0 else '未知',
                    }
                    data_list.append(record)
                except Exception as e:
                    print(f"解析失败: {str(e)}")
                    continue
            print(f"抓取到 {len(data_list)} 条数据: {city_name} {year}-{month:02d}")
            return data_list  # 成功抓取后直接返回
        except requests.exceptions.RequestException as e:
            print(f"请求失败: {str(e)}, 尝试次数 {attempt + 1}/{proxy_retries}")
            continue
    print(f"经过 {proxy_retries} 次尝试，未能成功抓取数据: {city_name} {year}-{month:02d}")
    return []  # 所有尝试失败后返回空列表

def fetch_month_data_remaining(city_name, year, month):
    """抓取一个月除前10天后剩余的天气数据"""
    current_dir = os.path.dirname(os.path.abspath(__file__))
    fetch_js_path = os.path.join(current_dir, 'fetch_reverse_crawling.js')
    city_data = CITY_INFO.get(city_name)
    if not city_data:
        print(f"未找到城市配置: {city_name}")
        return []
    city_pinyin = city_data['pinyin']
    url = f"https://lishi.tianqi.com/monthdata/{city_pinyin}/{year}{month:02d}.html"
    date = f"{year}{month:02d}"
    headers = {
        'User-Agent': random.choice(USER_AGENTS),
        'Host': 'lishi.tianqi.com',
        'X-Requested-With': 'XMLHttpRequest',
        'Referer': f"https://lishi.tianqi.com/monthdata/{city_pinyin}/{year}{month:02d}.html"
    }
    data_list = []
    proxy_retries = 3  # 代理重试次数
    for attempt in range(proxy_retries):
        proxy = get_random_proxy() if True else None
        try:
            time.sleep(random.uniform(5, 15))
            with open(fetch_js_path, 'r', encoding='utf-8') as js_file:
                js_code = js_file.read()
            response = session.post(
                url,
                headers=headers,
                data={'crypte': execjs.compile(js_code).call('encrypt', date, city_pinyin)},
                cookies=get_dynamic_cookies(city_pinyin),
                proxies=proxy,
                timeout=15
            )
            response.encoding = 'utf-8'
            if response.status_code != 200:
                print(f"请求被拒绝: {url} 状态码 {response.status_code}")
                continue
            if "error.png" in response.text:
                print(f"可能触发反爬机制，当前代理：{proxy}，尝试更换代理")
                continue
            # 检查响应内容是否为 JSON
            if response.text.startswith('<html>'):
                # 提取包裹在 <p> 标签中的 JSON 数据
                json_str = response.text.split('<p>')[1].split('</p>')[0]
                weather_data = json.loads(json_str)
            else:
                weather_data = response.json()
            for item in weather_data:
                try:
                    date_str = item['date_str']
                    high_temp = float(item['htemp'])
                    low_temp = float(item['ltemp'])
                    weather = item['weather']
                    wind_dir = item['WD']
                    record = {
                        'city_code': city_data['code'],
                        'city_name': city_name,
                        'date': datetime.strptime(date_str, '%Y-%m-%d'),
                        'temp_max': high_temp,
                        'temp_min': low_temp,
                        'weather': weather,
                        'wind_dir': wind_dir,
                    }
                    data_list.append(record)
                except Exception as e:
                    print(f"解析失败: {str(e)}")
                    continue
            print(f"抓取到 {len(data_list)} 条数据: {city_name} {year}-{month:02d}")
            return data_list  # 成功抓取后直接返回

        except requests.exceptions.RequestException as e:
            print(f"请求失败: {str(e)}, 尝试次数 {attempt + 1}/{proxy_retries}")
            continue
    print(f"经过 {proxy_retries} 次尝试，未能成功抓取数据: {city_name} {year}-{month:02d}")
    return []  # 所有尝试失败后返回空列表

def save_history_data(city_name):
    """抓取指定时间范围数据（2025年1月1日到今天）"""
    all_data = []
    start_date = date(2025, 1, 1)
    today = date.today()
    current_date = start_date
    while current_date <= today:
        year = current_date.year
        month = current_date.month
        print(f"正在抓取 {city_name} {year}-{month:02d}")
        first_part_data = fetch_month_data_first(city_name, year, month)
        remaining_part_data = fetch_month_data_remaining(city_name, year, month)
        monthly_data = first_part_data + remaining_part_data
        monthly_data.sort(key=lambda x: x['date'])
        all_data.extend(monthly_data)
        # 增加到下一个月
        if month == 12:
            current_date = date(year + 1, 1, 1)
        else:
            current_date = date(year, month + 1, 1)
    print(f"总共抓取到 {len(all_data)} 条数据")
    for data in all_data:
        new_record = NewHistoricalWeather(**data)
        db.session.merge(new_record)
    try:
        db.session.commit()
        print(f"{city_name} 成功写入 {len(all_data)} 条数据")
    except Exception as e:
        db.session.rollback()
        print(f"写入失败: {str(e)}")

def batch_crawl(city_name=None): # 允许city_name为空
    """
    爬取单个城市从 2025 年 1 月 1 日到今天的天气数据。
    如果 city_name 为 None, 则爬取所有城市
    """
    if city_name: # 如果提供了city_name, 则爬取单个城市
        print(f"[{datetime.now()}] 正在处理城市: {city_name}")
        save_history_data(city_name)
        # 数据清洗
        cleaner = DataCleaner()
        cleaner.execute_clean()
        delay = random.randint(5, 10)
        print(f"等待 {delay} 秒...")
        time.sleep(delay)
    else: # 如果city_name为None， 则爬取所有城市
        for city_name_chn, value in CITY_INFO.items():
            print(f"[{datetime.now()}] 正在处理城市: {city_name_chn}")
            save_history_data(city_name_chn)
            # 数据清洗
            cleaner = DataCleaner()
            cleaner.execute_clean()
            delay = random.randint(10, 20)
            print(f"等待 {delay} 秒...")
            time.sleep(delay)