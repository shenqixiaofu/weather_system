import requests
import concurrent.futures
import time
import statistics

# 在文件顶部添加新的import
import psutil

# 在文件顶部添加threading模块导入
import threading

def stress_test(url, total_requests=100, concurrency=20):
    """
    压力测试核心函数
    :param url: 测试目标URL
    :param total_requests: 总请求数
    :param concurrency: 并发数
    """
    # 测试结果统计
    results = {
        'total_time': 0.0,
        'requests': {
            'success': 0,
            'fail': 0
        },
        'response_times': [],
        'status_codes': {},  # 添加缺失的逗号
        'cpu_peak': 0,
        'memory_peak': 0
    }

    # 请求头设置
    headers = {
        'User-Agent': 'StressTestBot/1.0',
        'Accept-Encoding': 'gzip'
    }

    def send_request():
        start = time.time()
        try:
            response = requests.get(url, headers=headers, timeout=10)
            status_code = response.status_code
            results['status_codes'][status_code] = results['status_codes'].get(status_code, 0) + 1
            results['requests']['success'] += 1
        except Exception as e:
            results['requests']['fail'] += 1
            status_code = str(e)
        end = time.time()
        return end - start

    # 使用线程池模拟并发
    start_test = time.time()
    with concurrent.futures.ThreadPoolExecutor(max_workers=concurrency) as executor:
        futures = [executor.submit(send_request) for _ in range(total_requests)]
        for future in concurrent.futures.as_completed(futures):
            results['response_times'].append(future.result())

    results['total_time'] = time.time() - start_test

    # 计算统计指标
    if results['response_times']:
        results['response_time'] = {
            'avg': statistics.mean(results['response_times']),
            'max': max(results['response_times']),
            'min': min(results['response_times']),
            'p95': statistics.quantiles(results['response_times'], n=20)[-1]  # 95th percentile
        }
    
    # 打印测试报告
    print(f"\n压力测试报告 ({url})")
    print(f"总请求数: {total_requests}")
    print(f"并发数: {concurrency}")
    print(f"总耗时: {results['total_time']:.2f} 秒")
    print(f"成功请求: {results['requests']['success']}")
    print(f"失败请求: {results['requests']['fail']}")
    print(f"平均响应时间: {results['response_time']['avg']:.3f} 秒")
    print(f"最大响应时间: {results['response_time']['max']:.3f} 秒")
    print(f"95% 请求响应时间: {results['response_time']['p95']:.3f} 秒")
    print("状态码分布:")
    for code, count in results['status_codes'].items():
        print(f"  {code}: {count} 次")

    # 结束监控
    # 将监控函数定义移至stress_test函数之前
    def monitor_resources():
        """监控系统资源使用"""
        global max_cpu, max_mem, monitoring
        while monitoring:
            cpu = psutil.cpu_percent()
            mem = psutil.virtual_memory().used / (1024 * 1024)  # 转换为MB
            if cpu > max_cpu:
                max_cpu = cpu
            if mem > max_mem:
                max_mem = mem
            time.sleep(0.5)
    
    # 在函数开头声明全局变量
    global max_cpu, max_mem, monitoring
    max_cpu = 0
    max_mem = 0
    monitoring = True
    
    # 添加监控线程初始化
    # 将监控线程启动移到压力测试开始前
    monitor_thread = threading.Thread(target=monitor_resources)
    monitor_thread.start()
    
    # 压力测试逻辑（原代码）
    with concurrent.futures.ThreadPoolExecutor(max_workers=concurrency) as executor:
        futures = [executor.submit(send_request) for _ in range(total_requests)]
        for future in concurrent.futures.as_completed(futures):
            results['response_times'].append(future.result())

    # 测试结束后停止监控
    monitoring = False
    monitor_thread.join()
    
    # 记录监控结果（保持原位置）
    results['cpu_peak'] = round(max_cpu, 1)
    results['memory_peak'] = round(max_mem, 1)
    
    # 修改输出为表格格式
    success_rate = (results['requests']['success'] / total_requests) * 100
    print(f"""
| 并发线程数 | 总请求数 | 成功率 | 平均响应时间(s) | 95%请求响应时间(s) | 系统资源占用峰值 |
|------------|----------|--------|----------------|--------------------|------------------|
| {concurrency} | {total_requests} | {success_rate:.1f}% | {results['response_time']['avg']:.3f} | {results['response_time']['p95']:.3f} | CPU {results['cpu_peak']}%, 内存{results['memory_peak']}MB |""")
if __name__ == "__main__":
    # 测试配置（修改为你的实际API地址）
    test_url = "http://localhost:5000/cleaned_historical_weather/%E5%8C%97%E4%BA%AC"
    stress_test(test_url, total_requests=1000, concurrency=200)