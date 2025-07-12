// static/js/index.js

(function () {
    const theme = document.documentElement.getAttribute('data-theme') || 'light';
    if (theme === 'dark') {
        document.body.classList.add('dark-mode');
    }
})();

function showAlert(message, type = 'success') {
    const alertsContainer = document.getElementById('alertsContainer');
    if (!alertsContainer) {
        console.error("Alert container not found!");
        return;
    }
    const alert = document.createElement('div');
    alert.className = `alert alert-${type} alert-dismissible fade show`;
    alert.role = 'alert';
    alert.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    alertsContainer.appendChild(alert);
    setTimeout(() => {
        alert.classList.remove('show');
        setTimeout(() => {
            if (alertsContainer.contains(alert)) {
                alertsContainer.removeChild(alert);
            }
        }, 150);
    }, 5000);
}

// 图表实例
let index = {
    tempChart: null,
    rainfallChart: null,
    weatherPieChart: null,
    weatherRadarChart: null,
    forecastChart: null,
    wordcloudChart: null
};

// 当前温度周期
let currentTempPeriod = 'day';

// API请求处理
async function apiRequest(url) {
    try {
        const response = await $.ajax({
            url: url,
            dataType: 'json',
            timeout: 10000
        });
        console.log(`API响应 (${url}):`, response);
        if (!response || typeof response !== 'object') {
            throw new Error('API返回格式不正确');
        }
        return response;
    } catch (error) {
        console.error(`API请求失败 (${url}):`, error);
        let errorMessage = "请求失败: ";
        if (error.status === 404) {
            errorMessage += '找不到请求的资源,请检查城市名称是否正确';
        } else if (error.status === 0 && error.statusText === 'timeout') {
            errorMessage += '请求超时,请检查网络连接';
        } else if (error.responseJSON && error.responseJSON.message) {
            errorMessage += error.responseJSON.message;
        } else {
            errorMessage += error.statusText || error.message || '未知错误';
        }
        throw new Error(errorMessage);
    }
}

// 初始化图表
function initEmptyCharts() {
    // 初始化温度曲线图 - 空数据
    index.tempChart = echarts.init(document.getElementById('tempChart'));
    index.tempChart.setOption({
        tooltip: {trigger: 'axis'},
        grid: {left: '3%', right: '4%', bottom: '3%', containLabel: true},
        xAxis: {
            type: 'category',
            data: [],
            axisLabel: {rotate: 45}
        },
        yAxis: {type: 'value', name: '温度 (°C)'},
        series: [{
            name: '温度',
            type: 'line',
            smooth: true,
            data: [],
            lineStyle: {width: 3},
            itemStyle: {color: '#FF6B6B'},
            areaStyle: {
                color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
                    {offset: 0, color: 'rgba(255, 107, 107, 0.5)'},
                    {offset: 1, color: 'rgba(255, 107, 107, 0.1)'}
                ])
            },
        }]
    });

    // 初始化降水量图 - 空数据
    index.rainfallChart = echarts.init(document.getElementById('rainfallChart'));
    index.rainfallChart.setOption({
        tooltip: {trigger: 'axis'},
        grid: {left: '3%', right: '4%', bottom: '3%', containLabel: true},
        xAxis: {
            type: 'category',
            data: []
        },
        yAxis: {type: 'value', name: '降水量 (mm)', padding: [0, 0, 0, 20]},
        series: [{
            name: '降水量',
            type: 'bar',
            data: [],
            itemStyle: {
                color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
                    {offset: 0, color: '#4ECDC4'},
                    {offset: 1, color: '#556270'}
                ])
            },
            barWidth: '40%'
        }]
    });

    // 初始化一周天气预报图 - 空数据
    index.forecastChart = echarts.init(document.getElementById('forecastChart'));
    index.forecastChart.setOption({
        tooltip: {trigger: 'axis'},
        legend: {data: ['最高温度', '最低温度', '降水概率']},
        grid: {left: '3%', right: '4%', bottom: '3%', containLabel: true},
        xAxis: {
            type: 'category',
            boundaryGap: true,
            data: []
        },
        yAxis: [
            {
                type: 'value',
                name: '温度 (°C)',
                position: 'left'
            },
            {
                type: 'value',
                name: '降水概率 (%)',
                min: 0,
                max: 100,
                position: 'right'
            }
        ],
        series: [
            {
                name: '最高温度',
                type: 'line',
                smooth: true,
                data: [],
                itemStyle: {color: '#FF6B6B'}
            },
            {
                name: '最低温度',
                type: 'line',
                smooth: true,
                data: [],
                itemStyle: {color: '#7B68EE'}
            },
            {
                name: '降水概率',
                type: 'bar',
                yAxisIndex: 1,
                data: [],
                itemStyle: {
                    color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
                        {offset: 0, color: 'rgba(78, 205, 196, 0.8)'},
                        {offset: 1, color: 'rgba(78, 205, 196, 0.3)'}
                    ])
                }
            }
        ]
    });

    // 初始化气象因素分布图 - 空数据
    index.weatherPieChart = echarts.init(document.getElementById('weatherPieChart'));
    index.weatherPieChart.setOption({
        tooltip: {trigger: 'item', formatter: '{a} {b}: {c}天 ({d}%)'},
        legend: {
            orient: 'vertical',
            right: 10,
            top: 'center',
            data: []
        },
        series: [{
            name: '天气状况',
            type: 'pie',
            radius: ['40%', '70%'],
            avoidLabelOverlap: false,
            itemStyle: {
                borderRadius: 10,
                borderColor: '#fff',
                borderWidth: 2
            },
            label: {show: false},
            emphasis: {
                label: {show: true, fontSize: '16', fontWeight: 'bold'}
            },
            labelLine: {show: false},
            data: []
        }]
    });

    // 初始化气象指标雷达图 - 空数据
    index.weatherRadarChart = echarts.init(document.getElementById('weatherRadarChart'));
    index.weatherRadarChart.setOption({
        tooltip: {},
        radar: {
            shape: 'circle',
            indicator: [
                {name: '温度', max: 100},
                {name: '湿度', max: 100},
                {name: '风速', max: 100},
                {name: '能见度', max: 100},
                {name: '舒适度', max: 100},
            ]
        },
        series: [{
            name: '气象指标评分',
            type: 'radar',
            data: [{
                value: [],
                name: '今日评分',
                areaStyle: {
                    color: new echarts.graphic.RadialGradient(0.5, 0.5, 1, [
                        {offset: 0, color: 'rgba(86, 98, 112, 0.8)'},
                        {offset: 1, color: 'rgba(86, 98, 112, 0.3)'}
                    ])
                },
                lineStyle: {width: 2}
            }]
        }]
    });

    // 初始化词云图
    const wordcloudContainer = document.getElementById('wordcloudChart');
    wordcloudContainer.style.height = '400px';  // 确保容器有高度
    console.log('初始化词云图容器尺寸:', wordcloudContainer.offsetWidth, wordcloudContainer.offsetHeight);

    index.wordcloudChart = echarts.init(wordcloudContainer);
    console.log('词云图实例:', index.wordcloudChart);

    // 设置基础配置
    const wordcloudOption = {
        series: [{
            type: 'wordCloud',
            shape: 'circle',
            left: 'center',
            top: 'center',
            width: '100%',
            height: '100%',
            right: null,
            bottom: null,
            sizeRange: [20, 60],  // 固定大小范围
            rotationRange: [-90, 90],
            rotationStep: 45,
            gridSize: 8,
            drawOutOfBound: false,
            textStyle: {
                fontFamily: 'sans-serif',
                fontWeight: 'bold',
                color: function () {
                    return 'rgb(' + [
                        Math.round(Math.random() * 160),
                        Math.round(Math.random() * 160),
                        Math.round(Math.random() * 160)
                    ].join(',') + ')';
                }
            },
            emphasis: {
                focus: 'self',
                textStyle: {
                    shadowBlur: 10,
                    shadowColor: '#333'
                }
            },
            data: [] // 数据将在后续加载
        }]
    };
    index.wordcloudChart.setOption(wordcloudOption);
    console.log('词云图初始配置完成');

    // 确保所有图表容器有高度,或者用js设置也可以.
    document.querySelectorAll('.chart-container').forEach(container => {
        container.style.height = '400px'; // 或者其他合适的高度
    });
}

// 更新温度曲线图表 (同时处理日、周、月)
async function updateTempChart(city, period = 'day') {
    try {
        let endpoint;
        let times, tempMax, tempMin;

        switch (period) {
            case 'week':
                endpoint = `/weekly_data/${city}`;
                break;
            case 'month':
                endpoint = `/monthly_temp/${city}`;
                break;
            default: // 默认是 'day'
                endpoint = `/hourly_data/${city}`;
                break;
        }

        const response = await apiRequest(endpoint);
        console.log("温度API响应:", response);

        if (response) {
            switch (period) {
                case 'day':
                    times = response.times || [];
                    tempMax = (response.temps || []).map(temp => parseFloat(temp));
                    tempMin = []; // 日数据通常只有一条温度曲线
                    break;
                case 'week':
                    times = response.dates || [];
                    tempMax = (response.temp_max || []).map(temp => parseFloat(temp));
                    tempMin = (response.temp_min || []).map(temp => parseFloat(temp));
                    break;
                case 'month':
                    if (response.success && response.data) {
                        times = response.data.dates || [];
                        tempMax = (response.data.temp_max || []).map(temp => parseFloat(temp));
                        tempMin = (response.data.temp_min || []).map(temp => parseFloat(temp));
                    } else {
                        times = [];
                        tempMax = [];
                        tempMin = [];
                    }
                    break;
                default:
                    times = [];
                    tempMax = [];
                    tempMin = [];
            }

            // 基础配置 (适用于所有周期)
            const baseOption = {
                title: {
                    text: `${city} 温度变化 (${period === 'day' ? '小时' : period === 'week' ? '周' : '月'})`,
                    left: 'center',
                    textStyle: {
                        color: '#333',
                        fontSize: 18
                    }
                },
                tooltip: {
                    trigger: 'axis',
                    formatter: function (params) { // 自定义 tooltip
                        let date = params[0].name;
                        let result = `<b>${date}</b><br>`;
                        params.forEach(param => {
                            let value = param.value.toFixed(1);
                            let seriesName = param.seriesName;
                            result += `${param.marker} <span style="color:${param.color}; font-weight:bold;">${seriesName}: ${value}°C</span><br>`;
                        });
                        return result;
                    },
                    backgroundColor: 'rgba(255, 255, 255, 0.95)',
                    borderColor: '#ccc',
                    borderWidth: 1,
                    textStyle: {
                        color: '#333'
                    },
                    axisPointer: {
                        type: 'line',
                        lineStyle: {
                            color: '#999',
                            type: 'dashed'
                        }
                    }
                },
                grid: {
                    left: '5%',
                    right: '8%',
                    bottom: '8%',
                    containLabel: true
                },
                xAxis: {
                    type: 'category',
                    boundaryGap: false,
                    data: times,
                    axisLine: {
                        lineStyle: {
                            color: '#ccc'
                        }
                    },
                    axisLabel: {
                        color: '#666',
                        rotate: times.length > 15 ? 45 : 0, // 当x轴数据较多, 则旋转
                        fontSize: 12
                    }
                },
                yAxis: {
                    type: 'value',
                    name: '温度 (°C)',
                    nameTextStyle: {
                        color: '#666',
                        fontSize: 14
                    },
                    axisLine: {
                        lineStyle: {
                            color: '#ccc'
                        }
                    },
                    splitLine: {
                        lineStyle: {
                            type: 'dashed',
                            color: '#eee'
                        }
                    },
                    axisLabel: {
                        formatter: '{value}',
                        color: '#666',
                        fontSize: 12
                    }
                }
            };

            // 根据周期设置 series
            if (period === 'day') {
                baseOption.series = [{
                    name: '温度',
                    type: 'line',
                    smooth: true,
                    data: tempMax,
                    lineStyle: {
                        width: 3,
                        color: '#FF6B6B' // 更深的红色
                    },
                    itemStyle: {
                        color: '#FF6B6B'
                    },
                    areaStyle: { // 添加面积图
                        color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
                            {offset: 0, color: 'rgba(255, 107, 107, 0.8)'}, // 更深、更不透明
                            {offset: 1, color: 'rgba(255, 107, 107, 0.2)'} // 更浅、更透明
                        ])
                    },
                    symbol: 'circle', // 数据点样式
                    symbolSize: 8 // 数据点大小
                }];
                baseOption.legend = {show: false};

            } else { // 'week' 和 'month'
                baseOption.series = [
                    {
                        name: '最高温度',
                        type: 'line',
                        smooth: true,
                        data: tempMax,
                        lineStyle: {
                            width: 3,
                            color: '#e65100' // 橙红色
                        },
                        itemStyle: {
                            color: '#e65100'
                        },
                        areaStyle: { // 添加面积图
                            color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
                                {offset: 0, color: 'rgba(230, 81, 0, 0.8)'},
                                {offset: 1, color: 'rgba(230, 81, 0, 0.2)'}
                            ])
                        },
                        symbol: 'circle',
                        symbolSize: 8
                    },
                    {
                        name: '最低温度',
                        type: 'line',
                        smooth: true,
                        data: tempMin,
                        lineStyle: {
                            width: 3,
                            color: '#1e88e5' // 蓝色
                        },
                        itemStyle: {
                            color: '#1e88e5'
                        },
                        areaStyle: { // 添加面积图
                            color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
                                {offset: 0, color: 'rgba(30, 136, 229, 0.8)'},
                                {offset: 1, color: 'rgba(30, 136, 229, 0.2)'}
                            ])
                        },
                        symbol: 'circle',
                        symbolSize: 8
                    }
                ];
                baseOption.legend = {
                    data: ['最高温度', '最低温度'],
                    show: true,
                    top: 30,
                    textStyle: {
                        color: '#555',
                        fontSize: 14
                    }
                };


            }

            // 设置图表或显示 "暂无数据"
            if (times.length > 0 && (tempMax.length > 0 || tempMin.length > 0)) {
                index.tempChart.setOption(baseOption, true);
            } else {
                index.tempChart.setOption({
                    title: {text: '暂无数据', left: 'center', top: 'middle'}
                }, true);
            }

        } else {
            index.tempChart.setOption({
                title: {text: '暂无数据', left: 'center', top: 'middle'}
            }, true);
        }

        return true;

    } catch (error) {
        console.error("更新温度图表失败:", error);
        showAlert(`更新温度图表失败: ${error.message}`, 'danger');
        index.tempChart.setOption({
            title: {text: '暂无数据', left: 'center', top: 'middle'}
        }, true);
        return false;
    }
}

// 更新雷达图
async function updateRadarChart(city) {
    try {
        const response = await apiRequest(`/radar_data/${city}`);
        console.log("雷达图API响应:", response);
        if (response && response.status === 'success' && response.data && response.indicators) {
            const indicators = response.indicators.map(name => ({name: name, max: 100}));
            if (!Array.isArray(response.data) || response.data.length !== indicators.length) {
                console.error("雷达图数据格式不正确或数据缺失:", response);
                showAlert("雷达图数据格式不正确或数据缺失", "warning");
                index.weatherRadarChart.setOption({
                    title: {text: '暂无数据', left: 'center', top: 'middle'}
                }, true);
                return;
            }

            const numericData = response.data.map(value => {
                const num = Number(value);
                return isNaN(num) ? 0 : num;
            });
            console.log("雷达图 indicators:", indicators);
            console.log("雷达图 numericData:", numericData);

            index.weatherRadarChart.setOption({
                tooltip: {},
                radar: {
                    shape: 'circle',
                    indicator: indicators
                },
                series: [{
                    name: '气象指标评分',
                    type: 'radar',
                    data: [{
                        value: numericData,
                        name: '今日评分',
                        areaStyle: {
                            color: new echarts.graphic.RadialGradient(0.5, 0.5, 1, [
                                {offset: 0, color: 'rgba(86, 98, 112, 0.8)'},
                                {offset: 1, color: 'rgba(86, 98, 112, 0.3)'}
                            ])
                        },
                        lineStyle: {width: 2}
                    }]
                }]
            }, true);
        } else {
            index.weatherRadarChart.setOption({title: {text: '暂无数据', left: 'center', top: 'middle'}}, true);
        }
    } catch (error) {
        console.error("更新雷达图失败:", error);
        showAlert(`更新雷达图失败: ${error.message}`, 'danger');
        index.weatherRadarChart.setOption({title: {text: '暂无数据', left: 'center', top: 'middle'}}, true);
    }
}

// 更新所有图表
async function updateAllCharts(city) {
    try {

        // 并发请求所有数据
        const [tempData, radarData, forecastData, hourlyData, historyData] = await Promise.all([
            updateTempChart(city, currentTempPeriod),
            updateRadarChart(city),
            apiRequest(`/weekly_data/${city}`),
            apiRequest(`/hourly_data/${city}`),
            apiRequest(`/cleaned_historical_weather/${city}`)
        ]);
        console.log("历史天气数据:", historyData);

        // 更新降水量图表
        if (hourlyData && hourlyData.status === 'success' && hourlyData.precip && hourlyData.times) {
            index.rainfallChart.setOption({
                xAxis: {data: hourlyData.times},
                series: [{data: hourlyData.precip.map(val => parseFloat(val))}]
            });
        } else if (hourlyData && hourlyData.times && hourlyData.precip) {
            index.rainfallChart.setOption({
                xAxis: {data: hourlyData.times},
                series: [{data: hourlyData.precip}]
            });
        } else {
            index.rainfallChart.setOption({
                title: {
                    text: '暂无数据',
                    left: 'center',
                    top: 'middle'
                }
            });
        }

        // 更新气象分布饼图
        if (historyData && historyData.status === 'success' && historyData.data && historyData.data.length > 0) {
            const weatherTypes = {};
            historyData.data.forEach(day => {
                if (day.text) {
                    let weatherKey = day.text;
                    if (!weatherKey || weatherKey.trim() === '') {
                        weatherKey = '未知';
                    }
                    weatherTypes[weatherKey] = (weatherTypes[weatherKey] || 0) + 1;
                } else {
                    console.warn("当前日期缺少 text 字段或 text 值为空:", day);
                }
            });
            console.log("统计后的 weatherTypes:", weatherTypes);
            const pieData = Object.entries(weatherTypes).map(([name, value]) => ({name, value}));
            console.log("最终的 pieData:", pieData);

            if (pieData.length > 0) {
                index.weatherPieChart.setOption({
                    tooltip: {
                        trigger: 'item',
                        formatter: '{a} {b}: {c}天 ({d}%)'
                    },
                    legend: {
                        orient: 'horizontal',
                        bottom: 20,
                        left: 'center',
                        data: pieData.map(item => item.name)
                    },
                    series: [{
                        name: '天气状况',
                        type: 'pie',
                        radius: ['30%', '60%'],
                        center: ['50%', '45%'],
                        avoidLabelOverlap: false,
                        itemStyle: {
                            borderRadius: 10,
                            borderColor: '#fff',
                            borderWidth: 2
                        },
                        emphasis: {
                            label: {show: true, fontSize: '16', fontWeight: 'bold'}
                        },
                        data: pieData
                    }]
                }, true);

            } else {
                index.weatherPieChart.setOption({title: {text: '暂无数据', left: 'center', top: 'middle'}}, true);
            }
        } else {
            index.weatherPieChart.setOption({title: {text: '暂无数据', left: 'center', top: 'middle'}}, true);
        }

        // 更新预报图
        if (forecastData) {
            const dates = forecastData.dates || [];
            const highTemps = forecastData.temp_max || [];
            const lowTemps = forecastData.temp_min || [];
            let rainProb = [];
            if (forecastData.precip && forecastData.precip.length > 0) {
                rainProb = forecastData.precip.map(p => precipToRainProbability(p));
            }
            index.forecastChart.setOption({
                xAxis: {data: dates.map(d => typeof d === 'string' ? d : String(d))},
                boundaryGap: true,
                series: [
                    {data: highTemps.map(t => typeof t === 'number' ? t : parseFloat(t))},
                    {data: lowTemps.map(t => typeof t === 'number' ? t : parseFloat(t))},
                    {data: rainProb}
                ]
            });
        } else {
            index.forecastChart.setOption({
                title: {
                    text: '暂无数据',
                    left: 'center',
                    top: 'middle'
                }
            });
        }

        // 更新词云图
        const currentCity = document.getElementById('currentCity').textContent;
        if (currentCity) {
            console.log('开始更新词云图，当前城市:', currentCity);
            const wordcloudData = await apiRequest(`/weather_wordcloud/${currentCity}`);
            console.log("词云数据:", wordcloudData);

            if (wordcloudData && wordcloudData.status === 'success' && wordcloudData.data && wordcloudData.data.length > 0) {
                console.log('准备词云数据:', wordcloudData.data);
                console.log('总天数:', wordcloudData.total_days);

                // 准备数据
                const data = wordcloudData.data.map(item => ({
                    name: item.name,
                    value: item.value,
                    textStyle: {
                        color: '#' + Math.floor(Math.random() * 0xFFFFFF).toString(16).padStart(6, '0')
                    }
                }));

                console.log('处理后的词云数据:', data);

                // 使用新的配置
                const option = {
                    title: {
                        text: `${currentCity}历史天气分布 (共${wordcloudData.total_days}天)`,
                        left: 'center',
                        top: 0,
                        textStyle: {
                            fontSize: 14
                        }
                    },
                    tooltip: {
                        show: true,
                        formatter: function (params) {
                            const percentage = ((params.value / 10) / wordcloudData.total_days * 100).toFixed(1);
                            return `${params.name}: ${params.value / 10}天 (${percentage}%)`;
                        }
                    },
                    series: [{
                        type: 'wordCloud',
                        shape: 'circle',
                        left: 'center',
                        top: 'center',
                        width: '100%',
                        height: '100%',
                        sizeRange: [10, 50],
                        rotationRange: [-45, 45],
                        rotationStep: 15,
                        gridSize: 8,
                        drawOutOfBound: false,
                        layoutAnimation: true,
                        textStyle: {
                            fontFamily: 'sans-serif',
                            fontWeight: 'bold'
                        },
                        emphasis: {
                            focus: 'self',
                            textStyle: {
                                shadowBlur: 10,
                                shadowColor: '#333'
                            }
                        },
                        data: data
                    }]
                };

                try {
                    console.log('开始设置词云图配置');
                    index.wordcloudChart.clear();
                    index.wordcloudChart.setOption(option, true);
                    console.log('词云图配置设置完成');

                    // 确保图表容器可见
                    const container = document.getElementById('wordcloudChart');
                    if (container) {
                        container.style.height = '500px';  // 增加容器高度
                        container.style.visibility = 'visible';
                        console.log('词云图容器尺寸:', container.offsetWidth, container.offsetHeight);
                    }

                    // 延迟执行resize
                    setTimeout(() => {
                        console.log('执行resize');
                        index.wordcloudChart.resize();
                    }, 100);
                } catch (e) {
                    console.error('设置词云图配置时出错:', e);
                }
            } else {
                console.log('无词云数据，显示暂无数据提示');
                index.wordcloudChart.setOption({
                    title: {
                        text: '暂无数据',
                        left: 'center',
                        top: 'middle'
                    },
                    series: [{
                        type: 'wordCloud',
                        data: []
                    }]
                });
            }
        }

        return true;  // 所有图表更新成功

    } catch (error) {
        console.error("更新图表失败:", error);
        showAlert(`更新图表失败: ${error.message}`, 'danger');
        Object.values(index).forEach(chart => {
            if (chart) { //防止空指针
                chart.setOption({title: {text: '暂无数据', left: 'center', top: 'middle'}}, true);
            }

        });
        return false; // 有图表更新失败
    }
}

// 计算降水概率 (与之前版本相同)
function precipToRainProbability(precipAmount) {
    const amount = parseFloat(precipAmount);
    if (amount <= 0) return 0;
    if (amount < 1) return 20 + (amount * 30);
    if (amount < 5) return 50 + ((amount - 1) * 7.5);
    if (amount < 10) return 80 + ((amount - 5) * 3);
    if (amount < 25) return 95 + ((amount - 10) * 0.2);
    return 99;
}

// ====== 本地缓存相关函数 ======
function saveWeatherCache(city, data) {
    localStorage.setItem('weatherCache_' + city, JSON.stringify({
        data: data,
        time: Date.now()
    }));
}

function loadWeatherCache(city, maxAgeMinutes = 60) {
    const cache = localStorage.getItem('weatherCache_' + city);
    if (!cache) return null;
    try {
        const obj = JSON.parse(cache);
        if (Date.now() - obj.time < maxAgeMinutes * 60 * 1000) {
            return obj.data;
        }
    } catch (e) {
    }
    return null;
}

function renderWeatherData(city, data, isCache = false) {
    document.getElementById('currentCity').textContent = city;
    document.getElementById('cityDisplay').style.display = 'block';
    document.getElementById('currentTemp').textContent = `${data.temp || '--'}°C`;
    document.getElementById('currentHumidity').textContent = `${data.humidity || '--'}%`;
    document.getElementById('currentWind').textContent = `${data.windSpeed || '--'} km/h`;
    document.getElementById('currentWindDirection').textContent = data.windDirection || '--';
    document.getElementById('currentWeather').textContent = data.text || '--';
    document.getElementById('overviewCards').style.display = 'flex';
    document.getElementById('chartCards').style.display = 'flex';
    if (isCache) {
        showAlert('已加载本地缓存天气数据，正在自动刷新...', 'info');
    }
}

// 更新当前天气信息卡片
async function updateCurrentWeather(city) {
    try {
        const response = await apiRequest(`/weather_data/${city}`);
        console.log("API响应:", response);
        if (response && response.temp) {
            const latestData = {
                temp: response.temp,
                humidity: response.humidity,
                windSpeed: response.wind_speed,
                windDirection: response.wind_dir,
                text: response.text ? response.text : '--'
            };
            console.log("处理后的数据:", latestData);

            document.getElementById('currentTemp').textContent = `${latestData.temp || '--'}°C`;
            document.getElementById('currentHumidity').textContent = `${latestData.humidity || '--'}%`;
            document.getElementById('currentWind').textContent = `${latestData.windSpeed || '--'} km/h`;
            document.getElementById('currentWindDirection').textContent = latestData.windDirection || '--';
            document.getElementById('currentWeather').textContent = latestData.text || '--';
            return latestData; // 新增：返回数据对象
        } else {
            document.getElementById('currentTemp').textContent = '--°C';
            document.getElementById('currentHumidity').textContent = '--%';
            document.getElementById('currentWind').textContent = '-- km/h';
            document.getElementById('currentWindDirection').textContent = '--';
            document.getElementById('currentWeather').textContent = '暂无数据';
            return null;
        }
    } catch (error) {
        console.error("更新当前天气信息失败:", error);
        showAlert(`更新当前天气信息失败: ${error.message}`, 'warning');
        document.getElementById('currentTemp').textContent = '--°C';
        document.getElementById('currentHumidity').textContent = '--%';
        document.getElementById('currentWind').textContent = '-- km/h';
        document.getElementById('currentWindDirection').textContent = '--';
        document.getElementById('currentWeather').textContent = '暂无数据';
        return null;
    }
}

// 获取天气数据
async function fetchWeather(city) {
    let cityName = city;
    if (!cityName) {
        cityName = document.getElementById('cityInput').value;
    }
    if (!cityName) {
        showAlert('请输入城市名称', 'warning');
        return;
    }

    // 1. 先尝试本地缓存
    const cacheData = loadWeatherCache(cityName);
    if (cacheData) {
        renderWeatherData(cityName, cacheData, true); // true表示用缓存
    }

    // 2. 再异步请求最新数据
    try {
        document.getElementById('loadingCity').textContent = cityName;
        document.getElementById('loading').style.display = 'block';
        document.getElementById('noDataMessage').style.display = 'none';

        const response = await apiRequest(`/get_weather/${cityName}`);

        if (response && response.status === 'success') {
            const cityCN = response.city_cn || cityName;
            document.getElementById('currentCity').textContent = cityCN;
            document.getElementById('cityDisplay').style.display = 'block';

            // 更新天气数据和图表
            const weatherData = await updateCurrentWeather(cityCN);
            await updateAllCharts(cityCN);

            document.getElementById('overviewCards').style.display = 'flex';
            document.getElementById('chartCards').style.display = 'flex';

            // 3. 保存到本地缓存
            if (weatherData) {
                saveWeatherCache(cityCN, weatherData);
            }

            // 记录搜索行为（仅登录用户会被记录，未登录会返回403但不影响前端）
            fetch('/record_search_activity', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({city: cityCN})
            });

            // 数据加载和图表更新完成后,统一 resize 所有图表
            Object.values(index).forEach(chart => {
                if (chart) chart.resize();
            });

            showAlert(`成功获取${cityCN}的天气数据`, 'success');
        } else {
            throw new Error(response.message || '未能获取天气数据');
        }
    } catch (error) {
        console.error("获取天气数据失败:", error);
        showAlert(`获取天气数据失败: ${error.message}`, 'danger');
        document.getElementById('noDataMessage').style.display = 'block';
        document.getElementById('overviewCards').style.display = 'none';
        document.getElementById('chartCards').style.display = 'none';
        document.getElementById('cityDisplay').style.display = 'none';
    } finally {
        document.getElementById('loading').style.display = 'none';
    }
}

// 定位
function checkGeoLocation() {
    if (!navigator.geolocation) {
        showAlert('您的浏览器不支持地理定位功能,请手动输入城市', 'warning');
        document.getElementById('cityInput').style.display = 'block';
        return;
    }
    const geoModal = new bootstrap.Modal(document.getElementById('geoModal'));
    geoModal.show();

    document.getElementById('allowGeo').addEventListener('click', () => {
        geoModal.hide();
        getLocation();
    });

    document.getElementById('denyGeo').addEventListener('click', () => {
        geoModal.hide();
        showAlert('您已拒绝地理定位,请手动输入城市', 'info');
        document.getElementById('cityInput').style.display = 'block';
        document.getElementById('cityInput').focus();
    });
}

async function getLocation() {
    try {
        const position = await new Promise((resolve, reject) => {
            navigator.geolocation.getCurrentPosition(resolve, reject, {
                enableHighAccuracy: true,
                timeout: 5000,
                maximumAge: 0
            });
        });
        const {latitude, longitude} = position.coords;
        const city = await reverseGeocode(latitude, longitude);
        if (city) {
            document.getElementById('cityInput').value = city;
            document.getElementById('cityInput').style.display = 'block';
            fetchWeather(city);
            // 记录已定位状态和城市
            localStorage.setItem('hasLocated', '1');
            localStorage.setItem('locatedCity', city);
        }
    } catch (error) {
        console.error('定位失败:', error);
        let errorMessage = "自动定位失败: ";
        if (error.code === 1) {
            errorMessage += "用户拒绝了位置请求";
        } else if (error.code === 2) {
            errorMessage += "位置信息不可用";
        } else if (error.code === 3) {
            errorMessage += "请求超时";
        } else {
            errorMessage += "未知错误";
        }
        showAlert(errorMessage, 'danger');
        document.getElementById('cityDisplay').style.display = 'none';
        document.getElementById('cityInput').style.display = 'block';
        document.getElementById('cityInput').focus();
    }
}

async function reverseGeocode(lat, lng) {
    try {
        document.getElementById('loadingCity').textContent = "正在获取地理位置...";
        const response = await apiRequest(`/reverse_geocode/${lat}/${lng}`);
        if (response && response.status === 'success' && response.city) {
            return response.city;
        }
        throw new Error(response.message || '无法获取位置信息');
    } catch (error) {
        console.error("位置查询失败:", error);
        showAlert(`位置查询失败: ${error.message}`, 'danger');
        return null;
    }
}

// 改进的响应式调整
function debouncedResize() {
    clearTimeout(window.resizeTimer); // 清除之前的定时器
    window.resizeTimer = setTimeout(() => {
        // 仅当图表容器可见时才 resize
        if (document.getElementById('chartCards').offsetParent !== null) {
            Object.values(index).forEach(chart => {
                if (chart) chart.resize();
            });
        }
    }, 250); // 250毫秒延迟,避免频繁触发
}

window.addEventListener('resize', debouncedResize);


// 更新时间
function updateTime() {
    const timeElement = document.getElementById('currentTime');
    if (timeElement) {
        timeElement.textContent = new Date().toLocaleTimeString();
    }
}

document.addEventListener('DOMContentLoaded', () => {
    document.getElementById('noDataMessage').style.display = 'block';
    document.getElementById('cityDisplay').style.display = 'none';
    document.getElementById('overviewCards').style.display = 'none';
    document.getElementById('chartCards').style.display = 'none';

    initEmptyCharts();
    updateTime();
    setInterval(updateTime, 1000);

    document.querySelectorAll('#tempPeriodSelector .btn').forEach(btn => {
        btn.addEventListener('click', async (e) => {
            document.querySelectorAll('#tempPeriodSelector .btn').forEach(b => b.classList.remove('active'));
            e.target.classList.add('active');
            const period = e.target.dataset.period;
            currentTempPeriod = period;
            const city = document.getElementById('currentCity').textContent;

            if (city && document.getElementById('cityDisplay').style.display !== 'none') {
                index.tempChart.showLoading({text: '加载数据中...', color: '#3f51b5'});
                await updateTempChart(city, period);
                index.tempChart.hideLoading();
                index.tempChart.resize();
            }
        });
    });

    // 点击按钮查询城市
    document.getElementById('fetchBtn').addEventListener('click', () => {
        const cityName = document.getElementById('cityInput').value;
        if (cityName) {
            fetchWeather(cityName);
            localStorage.setItem('lastSearchedCity', cityName);
        } else {
            alert('请输入城市名称');
        }
    });

    // 回车查询城市
    document.getElementById('cityInput').addEventListener('keypress', e => {
        if (e.key === 'Enter') {
            const cityName = document.getElementById('cityInput').value;
            if (cityName) {
                fetchWeather(cityName);
                localStorage.setItem('lastSearchedCity', cityName);
            } else {
                alert('请输入城市名称');
            }
        }
    });

    // 检查用户登录状态并加载相应城市
    fetch('/check_login')
        .then(response => response.json())
        .then(data => {
            const defaultCity = document.getElementById('defaultCity').value;
            const lastSearchedCity = localStorage.getItem('lastSearchedCity');
            const locatedCity = localStorage.getItem('locatedCity');

            if (data.isLoggedIn) {
                // 用户已登录：优先使用默认城市
                if (defaultCity && defaultCity !== "None") {
                    fetchWeather(defaultCity);
                } else if (lastSearchedCity) {
                    fetchWeather(lastSearchedCity);
                } else if (locatedCity) {
                    fetchWeather(locatedCity);
                } else if (!localStorage.getItem('hasLocated')) {
                    checkGeoLocation();
                } else {
                    document.getElementById('cityInput').style.display = 'block';
                    document.getElementById('cityInput').focus();
                }
            } else {
                // 用户未登录：清除缓存并使用定位
                localStorage.removeItem('lastSearchedCity');
                if (!localStorage.getItem('hasLocated')) {
                    checkGeoLocation();
                } else if (locatedCity) {
                    fetchWeather(locatedCity);
                } else {
                    document.getElementById('cityInput').style.display = 'block';
                    document.getElementById('cityInput').focus();
                }
            }
        })
        .catch(error => {
            console.error('检查登录状态失败:', error);
            document.getElementById('cityInput').style.display = 'block';
            document.getElementById('cityInput').focus();
        });
});
