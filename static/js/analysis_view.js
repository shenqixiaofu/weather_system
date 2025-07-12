// static/js/analysis_view.js

const provinceData = {
    "北京": ["北京"],
    "上海": ["上海"],
    "天津": ["天津"],
    "重庆": ["重庆"],
    "黑龙江": ["哈尔滨", "齐齐哈尔", "牡丹江", "佳木斯", "绥化", "黑河", "大兴安岭", "伊春", "大庆", "七台河", "鸡西", "鹤岗", "双鸭山"],
    "吉林": ["长春", "吉林", "延边", "四平", "通化", "白城", "辽源", "松原", "白山"],
    "辽宁": ["沈阳", "大连", "鞍山", "抚顺", "本溪", "丹东", "锦州", "营口", "阜新", "辽阳", "铁岭", "朝阳", "盘锦", "葫芦岛"],
    "内蒙古": ["呼和浩特", "包头", "乌海", "乌兰察布", "通辽", "赤峰", "鄂尔多斯", "巴彦淖尔", "锡林郭勒", "呼伦贝尔", "兴安盟", "阿拉善盟"],
    "河北": ["石家庄", "保定", "张家口", "承德", "唐山", "廊坊", "沧州", "衡水", "邢台", "邯郸", "秦皇岛", "雄安新区"],
    "山西": ["太原", "大同", "阳泉", "晋中", "长治", "晋城", "临汾", "运城", "朔州", "忻州", "吕梁"],
    "陕西": ["西安", "咸阳", "延安", "榆林", "渭南", "商洛", "安康", "汉中", "宝鸡", "铜川", "杨凌"],
    "山东": ["济南", "青岛", "淄博", "德州", "烟台", "潍坊", "济宁", "泰安", "临沂", "菏泽", "滨州", "东营", "威海", "枣庄", "日照", "莱芜", "聊城"],
    "新疆": ["乌鲁木齐", "克拉玛依", "石河子", "昌吉", "吐鲁番", "巴州", "阿拉尔", "阿克苏", "喀什", "伊犁", "塔城", "哈密", "和田", "阿勒泰", "克州", "博州"],
    "西藏": ["拉萨", "日喀则", "山南", "林芝", "昌都", "那曲", "阿里"],
    "青海": ["西宁", "海东", "黄南", "海南", "果洛", "玉树", "海西", "海北"],
    "甘肃": ["兰州", "定西", "平凉", "庆阳", "武威", "金昌", "张掖", "酒泉", "天水", "陇南", "临夏", "甘南", "白银", "嘉峪关"],
    "宁夏": ["银川", "石嘴山", "吴忠", "固原", "中卫"],
    "河南": ["郑州", "安阳", "新乡", "许昌", "平顶山", "信阳", "南阳", "开封", "洛阳", "商丘", "焦作", "鹤壁", "濮阳", "周口", "漯河", "驻马店", "三门峡", "济源"],
    "江苏": ["南京", "无锡", "镇江", "苏州", "南通", "扬州", "盐城", "徐州", "淮安", "连云港", "常州", "泰州", "宿迁"],
    "湖北": ["武汉", "襄阳", "鄂州", "孝感", "黄冈", "黄石", "咸宁", "荆州", "宜昌", "恩施", "十堰", "神农架", "随州", "荆门", "天门", "仙桃", "潜江"],
    "浙江": ["杭州", "湖州", "嘉兴", "宁波", "绍兴", "台州", "温州", "丽水", "金华", "衢州", "舟山"],
    "安徽": ["合肥", "蚌埠", "芜湖", "淮南", "马鞍山", "安庆", "宿州", "阜阳", "亳州", "黄山", "滁州", "淮北", "铜陵", "宣城", "六安", "池州"],
    "福建": ["福州", "厦门", "宁德", "莆田", "泉州", "漳州", "龙岩", "三明", "南平", "钓鱼岛"],
    "江西": ["南昌", "九江", "上饶", "抚州", "宜春", "吉安", "赣州", "景德镇", "萍乡", "新余", "鹰潭"],
    "湖南": ["长沙", "湘潭", "株洲", "衡阳", "郴州", "常德", "益阳", "娄底", "邵阳", "岳阳", "张家界", "怀化", "永州", "湘西"],
    "贵州": ["贵阳", "遵义", "安顺", "黔南", "黔东南", "铜仁", "毕节", "六盘水", "黔西南"],
    "四川": ["成都", "攀枝花", "自贡", "绵阳", "南充", "达州", "遂宁", "广安", "巴中", "泸州", "宜宾", "内江", "资阳", "乐山", "眉山", "凉山", "雅安", "甘孜", "阿坝", "德阳", "广元"],
    "广东": ["广州", "韶关", "惠州", "梅州", "汕头", "深圳", "珠海", "佛山", "肇庆", "湛江", "江门", "河源", "清远", "云浮", "潮州", "东莞", "中山", "阳江", "揭阳", "茂名", "汕尾"],
    "云南": ["昆明", "大理", "红河", "曲靖", "保山", "文山", "玉溪", "楚雄", "普洱", "昭通", "临沧", "怒江", "迪庆", "丽江", "德宏", "西双版纳"],
    "广西": ["南宁", "崇左", "柳州", "来宾", "桂林", "梧州", "贺州", "贵港", "玉林", "百色", "钦州", "河池", "北海", "防城港"],
    "海南": ["海口", "三亚", "三沙"],
    "香港": ["香港"],
    "澳门": ["澳门"],
    "台湾": ["台北", "高雄", "台中"]
};

// 初始化省份下拉框
const provinceSelect = document.getElementById('provinceSelect');
Object.keys(provinceData).forEach(province => {
    const option = document.createElement('option');
    option.value = province;
    option.textContent = province;
    provinceSelect.appendChild(option);
});

// 省份选择变化事件
provinceSelect.addEventListener('change', function () {
    const citySelect = document.getElementById('citySelect');
    citySelect.innerHTML = '<option value="">请选择城市</option>';
    citySelect.disabled = !this.value;
    if (this.value) {
        provinceData[this.value].forEach(city => {
            const option = document.createElement('option');
            option.value = city;
            option.textContent = city;
            citySelect.appendChild(option);
        });
    }
});

// 显示加载动画
function showLoader() {
    document.getElementById('loader').style.display = 'block';
    document.getElementById('analysis-results').style.display = 'none';
}

// 隐藏加载动画
function hideLoader() {
    document.getElementById('loader').style.display = 'none';
}

// 加载分析数据
function loadAnalysis() {
    const city = document.getElementById('citySelect').value;
    if (!city) {
        alert('请选择一个城市');
        return;
    }
    // 加载动画
    showLoader();
    // 发送天气分析请求
    fetch(`/weather_analysis/${city}`)
        .then(response => response.json())
        .then(data => {
            hideLoader();
            if (data.status === 'success') {
                displayAnalysis(data.data);
            } else {
                alert(`分析失败: ${data.message}`);
            }
        })
        .catch(error => {
            hideLoader();
            console.error('分析请求失败:', error);
            alert('系统错误，请稍后再试');
        });
}

// 显示分析结果
function displayAnalysis(data) {
    document.getElementById('analysis-results').style.display = 'block';
    
    // 显示温度趋势
    displayTemperatureTrend(data.trends);
    
    // 显示季节性分析
    displaySeasonalPatterns(data.seasonal_patterns);
    
    // 显示异常天气事件
    displayAnomalies(data.trends.anomalies);
    
    // 显示天气模式分析
    displayWeatherPatterns(data.weather_patterns);
}

// 显示温度趋势
function displayTemperatureTrend(trends) {
    const trendChart = echarts.init(document.getElementById('temperatureTrendChart'));
    
    const option = {
        title: { text: '温度趋势分析', left: 'center' },
        tooltip: {
            trigger: 'axis',
            formatter: function(params) {
                let date = params[0].name;
                let result = `<b>${date}</b><br>`;
                params.forEach(param => {
                    result += `${param.marker} <span style=\"color:${param.color}; font-weight:bold;\">${param.seriesName}: ${param.value.toFixed(1)}°C</span><br>`;
                });
                return result;
            }
        },
        legend: { data: ['最高温度', '最低温度'], top: 30 },
        xAxis: { type: 'category', data: trends.trend_x },
        yAxis: { type: 'value', name: '温度 (°C)' },
        series: [
            {
                name: '最高温度',
                type: 'line',
                data: trends.trend_max_temp.map(v => v != null ? Number(v.toFixed(1)) : null),
                smooth: true,
                lineStyle: { width: 3, color: '#e65100' }
            },
            {
                name: '最低温度',
                type: 'line',
                data: trends.trend_min_temp.map(v => v != null ? Number(v.toFixed(1)) : null),
                smooth: true,
                lineStyle: { width: 3, color: '#1e88e5' }
            }
        ]
    };
    
    trendChart.setOption(option);
    
    // 更新趋势摘要
    const summary = document.getElementById('trendSummary');
    summary.innerHTML = `
        <div class=\"trend-summary-card\">
            <div class=\"summary-item\"><i class=\"fas fa-temperature-high text-danger me-2\"></i><b>平均最高温度：</b> ${trends.summary_stats.max_temp_mean.toFixed(1)}°C</div>
            <hr>
            <div class=\"summary-item\"><i class=\"fas fa-temperature-low text-info me-2\"></i><b>平均最低温度：</b> ${trends.summary_stats.min_temp_mean.toFixed(1)}°C</div>
            <hr>
            <div class=\"summary-item\"><i class=\"fas fa-exchange-alt text-success me-2\"></i><b>温度变化率：</b> ${trends.summary_stats.max_temp_change_mean.toFixed(1)}°C/天</div>
        </div>
    `;
}

// 显示季节性分析
function displaySeasonalPatterns(seasonal) {
    const seasonalChart = echarts.init(document.getElementById('seasonalPatternChart'));
    
    const seasons = ['春季', '夏季', '秋季', '冬季'];
    const option = {
        title: { text: '季节性温度分布', left: 'center' },
        tooltip: {
            trigger: 'axis',
            axisPointer: { type: 'shadow' },
            formatter: function(params) {
                let s = params[0].name + '<br>';
                params.forEach(param => {
                    let val = (param.value !== null && param.value !== undefined) ? param.value.toFixed(1) : '-';
                    s += `${param.marker}${param.seriesName}: ${val}°C<br>`;
                });
                return s;
            }
        },
        legend: { data: ['最高温度', '最低温度'], top: 30 },
        xAxis: { type: 'category', data: seasons },
        yAxis: { type: 'value', name: '温度 (°C)' },
        series: [
            {
                name: '最高温度',
                type: 'bar',
                data: seasons.map((_, i) => {
                    const v = seasonal.seasonal_stats.max_temp.mean[i + 1];
                    return v != null ? Number(v.toFixed(1)) : null;
                }),
                itemStyle: { color: '#e65100' }
            },
            {
                name: '最低温度',
                type: 'bar',
                data: seasons.map((_, i) => {
                    const v = seasonal.seasonal_stats.min_temp.mean[i + 1];
                    return v != null ? Number(v.toFixed(1)) : null;
                }),
                itemStyle: { color: '#1e88e5' }
            }
        ]
    };
    
    seasonalChart.setOption(option);
    
    // 更新季节特征摘要
    const summary = document.getElementById('seasonalSummary');
    const mostVolatileSeason = Object.entries(seasonal.seasonal_stats.max_temp.std)
        .reduce((a, b) => a[1] > b[1] ? a : b)[0];
    summary.innerHTML = `
        <p>最显著季节: ${seasons[mostVolatileSeason - 1]}</p>
        <p>温度波动范围: ${seasonal.seasonal_stats.range[mostVolatileSeason].toFixed(1)}°C</p>
    `;
}

// 显示异常天气事件
function displayAnomalies(anomalies) {
    const tbody = document.querySelector('#anomaliesTable tbody');
    tbody.innerHTML = '';
    if (!anomalies.dates || anomalies.dates.length === 0) {
        const row = document.createElement('tr');
        row.innerHTML = `<td colspan="4" class="text-center text-muted">无异常天气事件</td>`;
        tbody.appendChild(row);
        return;
    }
    anomalies.dates.forEach((date, index) => {
        const row = document.createElement('tr');
        const maxTemp = anomalies.max_temps[index];
        const minTemp = anomalies.min_temps[index];
        let anomalyType = '';
        if (maxTemp > 35) anomalyType = '高温异常';
        else if (minTemp < 0) anomalyType = '低温异常';
        else anomalyType = '温度波动异常';
        row.innerHTML = `
            <td>${date}</td>
            <td>${maxTemp.toFixed(1)}°C</td>
            <td>${minTemp.toFixed(1)}°C</td>
            <td>${anomalyType}</td>
        `;
        tbody.appendChild(row);
    });
}

// 显示天气模式分析
function displayWeatherPatterns(patterns) {
    // 温度范围分布图
    const tempRangeChart = echarts.init(document.getElementById('tempRangeChart'));
    const tempRangeOption = {
        title: { text: '日温差分布', left: 'center' },
        tooltip: {
            trigger: 'axis',
            formatter: function(params) {
                let s = '';
                params.forEach(param => {
                    s += `${param.marker}${param.name}: ${param.value.toFixed(1)}°C<br>`;
                });
                return s;
            }
        },
        xAxis: { type: 'category', data: ['最小温差', '平均温差', '最大温差'] },
        yAxis: { type: 'value', name: '温差 (°C)' },
        series: [{
            name: '日温差',
            type: 'bar',
            data: [
                Number(patterns.temp_range_stats.min.toFixed(1)),
                Number(patterns.temp_range_stats.mean.toFixed(1)),
                Number(patterns.temp_range_stats.max.toFixed(1))
            ],
            itemStyle: {
                color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
                    { offset: 0, color: '#83bff6' },
                    { offset: 0.5, color: '#188df0' },
                    { offset: 1, color: '#188df0' }
                ])
            }
        }]
    };
    tempRangeChart.setOption(tempRangeOption);
    
    // 温度变化频率图
    const changeFrequencyChart = echarts.init(document.getElementById('changeFrequencyChart'));
    const changeFrequencyOption = {
        title: { text: '温度变化频率', left: 'center' },
        tooltip: {
            trigger: 'item',
            formatter: function(param) {
                return `${param.marker}${param.name}: ${param.value}天 (${param.percent}%)`;
            }
        },
        legend: { orient: 'horizontal', bottom: 0 },
        series: [{
            type: 'pie',
            radius: '50%',
            label: {
                formatter: '{b}: {c}天 ({d}%)'
            },
            data: [
                { value: patterns.change_frequency.max_temp_increase, name: '最高温上升' },
                { value: patterns.change_frequency.max_temp_decrease, name: '最高温下降' },
                { value: patterns.change_frequency.min_temp_increase, name: '最低温上升' },
                { value: patterns.change_frequency.min_temp_decrease, name: '最低温下降' }
            ],
            emphasis: {
                itemStyle: {
                    shadowBlur: 10,
                    shadowOffsetX: 0,
                    shadowColor: 'rgba(0, 0, 0, 0.5)'
                }
            }
        }]
    };
    changeFrequencyChart.setOption(changeFrequencyOption);
}

// 监听窗口大小变化，调整图表大小
window.addEventListener('resize', function() {
    const charts = [
        document.getElementById('temperatureTrendChart'),
        document.getElementById('seasonalPatternChart'),
        document.getElementById('tempRangeChart'),
        document.getElementById('changeFrequencyChart')
    ];
    
    charts.forEach(chart => {
        if (chart) {
            echarts.getInstanceByDom(chart)?.resize();
        }
    });
});

// --- 右上角分析标签样式统一 ---
document.addEventListener('DOMContentLoaded', function () {
    // 统一分析标签样式
    const badges = document.querySelectorAll('.badge.bg-info, .badge.bg-secondary');
    badges.forEach(badge => {
        badge.style.backgroundColor = '#1e88e5';
        badge.style.color = 'white';
        badge.style.marginBottom = '6px';
        badge.style.fontWeight = 'bold';
        badge.style.letterSpacing = '1px';
        badge.style.borderRadius = '16px';
        badge.style.boxShadow = '0 2px 6px rgba(30,136,229,0.08)';
    });
}); 