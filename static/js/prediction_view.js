// static/js/prediction_view.js
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
    "西藏": ["**", "日喀则", "山南", "林芝", "昌都", "那曲", "阿里"],
    "青海": ["西宁", "海东", "黄南", "海南", "果洛", "玉树", "海西", "海北"],
    "甘肃": ["兰州", "定西", "平凉", "庆阳", "武威", "金昌", "张掖", "酒泉", "天水", "陇南", "临夏", "甘南", "白银", "嘉峪关"],
    "宁夏": ["银川", "石嘴山", "吴忠", "固原", "中卫"],
    "河南": ["郑州", "安阳", "新乡", "许昌", "平顶山", "信阳", "南阳", "开封", "洛阳", "商丘", "焦作", "鹤壁", "濮阳", "周口", "漯河", "驻马店", "三门峡", "济源"],
    "江苏": ["南京", "无锡", "镇江", "苏州", "南通", "扬州", "盐城", "徐州", "淮安", "连云港", "常州", "泰州", "宿迁"],
    "湖北": ["武汉", "襄阳", "鄂州", "孝感", "黄冈", "黄石", "咸宁", "荆州", "宜昌", "恩施", "十堰", "神农架", "随州", "荆门", "天门", "仙桃", "潜江"],
    "浙江": ["杭州", "湖州", "嘉兴", "宁波", "绍兴", "台州", "温州", "丽水", "金华", "衢州", "舟山"],
    "安徽": ["合肥", "蚌埠", "芜湖", "淮南", "马鞍山", "安庆", "宿州", "阜阳", "亳州", "黄山", "滁州", "淮北", "铜陵", "宣城", "六安", "池州"],
    "福建": ["福州", "厦门", "宁德", "莆田", "泉州", "漳州", "龙岩", "三明", "南平", "***"],
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

// 初始化省份下拉框 (使用 Bootstrap 的样式)
const provinceSelect = document.getElementById('provinceSelect');
Object.keys(provinceData).forEach(province => {
    const option = document.createElement('option');
    option.value = province;
    option.textContent = province;
    provinceSelect.appendChild(option);
});

// 省份选择变化事件 (使用 Bootstrap 的样式)
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

// 城市选择变化事件 (可根据需要扩展)
document.getElementById('citySelect').addEventListener('change', function () {
    if (this.value) {
        // 执行城市选择后的操作 (例如加载天气数据)
        console.log('已选择城市:', this.value);
    }
});

// 初始化 ECharts 图表
document.addEventListener('DOMContentLoaded', function () {
    const predictionChart = echarts.init(document.getElementById('predictionChart'));
    const temperatureRangeChart = echarts.init(document.getElementById('temperatureRangeChart'));

    // 监听窗口大小变化，调整图表大小
    window.addEventListener('resize', function () {
        predictionChart.resize();
        temperatureRangeChart.resize();
    });
});

// 显示加载动画 (使用 Bootstrap 的 class)
function showLoader() {
    document.getElementById('loader').style.display = 'block';
    document.getElementById('prediction-metrics').style.display = 'none';
    document.getElementById('tableSection').style.display = 'none';
}

// 隐藏加载动画
function hideLoader() {
    document.getElementById('loader').style.display = 'none';
}

// 发起预测请求
function loadPrediction() {
    const city = document.getElementById('citySelect').value;
    if (!city) {
        alert('请选择一个城市');
        return;
    }

    showLoader();

    fetch(`/predict_weather/${city}`)
        .then(response => response.json())
        .then(data => {
            hideLoader();
            if (data.status === 'success') {
                displayPrediction(data.predictions, city);
            } else {
                alert(`获取预测失败: ${data.message}`);
            }
        })
        .catch(error => {
            hideLoader();
            console.error('预测请求失败:', error);
            alert('系统错误，请稍后再试');
        });
}

// 显示预测结果
function displayPrediction(predictions, cityName) {
    // 显示预测指标和表格区域
    document.getElementById('prediction-metrics').style.display = 'flex';
    document.getElementById('tableSection').style.display = 'block';

    // 计算统计指标
    const maxTemps = predictions.temp_max;
    const minTemps = predictions.temp_min;
    const avgHigh = (maxTemps.reduce((a, b) => a + b, 0) / maxTemps.length).toFixed(1);
    const avgLow = (minTemps.reduce((a, b) => a + b, 0) / minTemps.length).toFixed(1);
    const maxTemp = Math.max(...maxTemps).toFixed(1);
    const minTemp = Math.min(...minTemps).toFixed(1);

    // 更新统计指标显示 (使用 Bootstrap 的 class)
    document.getElementById('avg-high').textContent = avgHigh + '°C';
    document.getElementById('avg-low').textContent = avgLow + '°C';
    document.getElementById('max-temp').textContent = maxTemp + '°C';
    document.getElementById('min-temp').textContent = minTemp + '°C';

    // 更新表格内容
    let tbody = '';
    for (let i = 0; i < predictions.dates.length; i++) {
        const range = (maxTemps[i] - minTemps[i]).toFixed(1);
        tbody += `
            <tr>
                <td>${predictions.dates[i]}</td>
                <td>${maxTemps[i].toFixed(1)}°C</td>
                <td>${minTemps[i].toFixed(1)}°C</td>
                <td>${range}°C</td>
            </tr>`;
    }
    document.getElementById('predictionBody').innerHTML = tbody;

    // 渲染预测趋势图 (ECharts 配置)
    const predictionChart = echarts.init(document.getElementById('predictionChart'));
    const predictionOption = {
        title: {
            text: `${cityName} 未来温度预测趋势`,
            left: 'center',
            textStyle: {
                color: '#333',
                fontSize: 18 // 增大标题字号
            }
        },
        tooltip: {
            trigger: 'axis',
            formatter: function (params) {
                let date = params[0].name;
                let result = `<b>${date}</b><br>`; // 加粗日期
                params.forEach(param => {
                    if (param.seriesName.indexOf('_lower') === -1  && param.seriesName.indexOf('置信区间') === -1) {
                        let value = param.value.toFixed(1);
                        let seriesName = param.seriesName;
                        result += `${param.marker} <span style="color:${param.color}; font-weight:bold;">${seriesName}: ${value}°C</span><br>`;
                    }

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
        legend: {
            data: ['预测最高温度', '预测最低温度', '平均温度'], // 包含平均温度
            top: 30,
            textStyle: {
                color: '#555',
                fontSize: 14 // 增大图例字号
            }
        },
        grid: {
            left: '5%', // 增大左边距
            right: '5%', // 增大右边距
            bottom: '8%', // 增大底边距
            containLabel: true
        },
        xAxis: {
            type: 'category',
            boundaryGap: false,
            data: predictions.dates,
            axisLine: {
                lineStyle: {
                    color: '#ccc'
                }
            },
            axisLabel: {
                color: '#666',
                rotate: predictions.dates.length > 10 ? 45 : 0,
                fontSize: 12 // 调整x轴标签字号
            }
        },
        yAxis: {
            type: 'value',
            name: '温度 (°C)',
            nameTextStyle: {
                color: '#666',
                fontSize: 14 // 增大y轴名称字号
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
                color: '#666',
                fontSize: 12 // 调整y轴标签字号
            }
        },
        series: [
            {
                name: '预测最高温度',
                type: 'line',
                data: predictions.temp_max,
                smooth: true,
                lineStyle: {
                    width: 3,
                    color: '#e65100'
                },
                itemStyle: {
                    color: '#e65100'
                },
                symbol: 'circle',
                symbolSize: 8,
                areaStyle: {
                    color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
                        { offset: 0, color: 'rgba(230, 81, 0, 0.8)' },
                        { offset: 1, color: 'rgba(230, 81, 0, 0.1)' }
                    ])
                }
            },
            {
                name: '预测最低温度',
                type: 'line',
                data: predictions.temp_min,
                smooth: true,
                lineStyle: {
                    width: 3,
                    color: '#1e88e5'
                },
                itemStyle: {
                    color: '#1e88e5'
                },
                symbol: 'circle',
                symbolSize: 8,
                areaStyle: {
                    color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
                        { offset: 0, color: 'rgba(30, 136, 229, 0.8)' },
                        { offset: 1, color: 'rgba(30, 136, 229, 0.1)' }
                    ])
                }
            },
              {
                name: '最高温度置信区间',
                type: 'line',
                data: predictions.temp_max_upper,
                stack: 'confidence-max',
                lineStyle: {
                    color: 'transparent'
                },
                  itemStyle:{
                    color: 'transparent'
                },
                areaStyle: {
                    color: 'rgba(230, 81, 0, 0.2)'
                },

            },
            {
                name: '最低温度置信区间',
                type: 'line',
                data: predictions.temp_min_lower,
                stack: 'confidence-min',
                lineStyle: {
                    color: 'transparent'
                },
                 itemStyle:{
                    color: 'transparent'
                },
                areaStyle: {
                    color: 'rgba(30, 136, 229, 0.2)'
                }
            },
             {
                name: '最高温度置信区间_lower',
                type: 'line',
                data: predictions.temp_max_lower,
                stack: 'confidence-max',
                lineStyle: {
                    color: 'transparent'
                },
                 itemStyle:{
                    color: 'transparent'
                },
                areaStyle: {
                    color: 'transparent'
                },

            },
               {
                name: '最低温度置信区间_lower',
                type: 'line',
                data: predictions.temp_min_upper,
                stack: 'confidence-min',
                lineStyle: {
                    color: 'transparent'
                },
                   itemStyle:{
                    color: 'transparent'
                },
                areaStyle: {
                  color: 'transparent'
                }
            },
             {
                name: '历史最高',
                type: 'line',
                markLine: {
                    data: [
                        { yAxis: 35, name: '历史最高' }
                    ],
                     lineStyle: {
                        color: 'red',
                        type: 'dotted'
                    },
                      label:{
                      formatter: '{b}: {c}°C'
                    }
                }
            },
        ]
    };

    predictionChart.setOption(predictionOption);


    // 渲染温度区间图 (ECharts 配置)
    const temperatureRangeChart = echarts.init(document.getElementById('temperatureRangeChart'));
    const rangeOption = {
        title: {
            text: `${cityName} 预测温度区间`,
            left: 'center',
            textStyle: {
              color: '#333' //深灰色标题
            }
        },
        tooltip: {
            trigger: 'axis',
            axisPointer: {
                type: 'shadow'
            },
            formatter: function (params) {
                // params 包含当前 x 轴位置对应的所有 series 数据点
                const date = params[0].name; // 获取日期 (x轴标签)
                let highTemp, originalMinTemp; // 定义变量存储最高温和原始最低温

                // 遍历 params 数组，找到最高温和最低温对应的数据点
                params.forEach(param => {
                    if (param.seriesName === '最高温度') {
                        highTemp = param.value; // 最高温度的值是原始值
                    } else if (param.seriesName === '最低温度') {
                        // 最低温度的 param.value 是被取反后的值 (正数或0)
                        // 需要再次取反得到原始的最低温度 (负数或0)
                        originalMinTemp = -param.value;
                    }
                });

                // 确保成功获取到最高温和最低温
                if (highTemp !== undefined && originalMinTemp !== undefined) {
                    // 计算温差：最高温 - 最低温
                    const range = (highTemp - originalMinTemp).toFixed(1);

                    // 构建 tooltip 显示内容
                    return `
                        <div style="text-align:center; line-height: 1.6;"> <!-- 调整行高让内容更清晰 -->
                            <b>${date}</b><br>
                            <span style="color:#e65100">▲ 最高温度: ${highTemp.toFixed(1)}°C</span><br>
                            <span style="color:#1e88e5">▼ 最低温度: ${originalMinTemp.toFixed(1)}°C</span><br> <!-- 直接使用原始最低温 -->
                            温差: ${range}°C <!-- 使用正确计算的温差 -->
                        </div>
                    `;
                }
                // 如果数据不完整，返回提示信息
                return `<div style="color:#666">数据加载中或不完整...</div>`;
            }
        },
        legend: {
            data: ['温度区间'],
            top: 30,
            textStyle: {
              color: '#555'  // 浅灰色图例文字
            }
        },
        xAxis: {
            type: 'category',
            data: predictions.dates,
            axisLine: {
                lineStyle: {
                    color: '#ccc'  // 浅灰色坐标轴线
                }
            },
            axisLabel: {
                color: '#666',  // 较浅灰色标签
                rotate: predictions.dates.length > 10 ? 45 : 0
            }
        },
        yAxis: {
            type: 'value',
            name: '温度 (°C)',
            nameTextStyle: {
                color: '#666'  // 较浅灰色轴名称
            },
            axisLine: {
                lineStyle: {
                    color: '#ccc' // 浅灰色坐标轴线
                }
            },
            splitLine: {
                lineStyle: {
                    type: 'dashed',
                    color: '#eee'  // 浅灰色分割线
                }
            },
            axisLabel: {
               color: '#666'  // 较浅灰色标签
            }
        },
        series: [
            {
                name: '最高温度',
                type: 'bar',
                stack: 'Total',
                itemStyle: {
                    color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
                        { offset: 0, color: '#e65100' },  // 橙红色渐变
                        { offset: 1, color: '#ff8a65' }
                    ])
                },
                data: predictions.temp_max
            },
            {
                name: '最低温度',
                type: 'bar',
                stack: 'Total',
                itemStyle: {
                    color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
                        { offset: 0, color: '#1e88e5' },  // 蓝色渐变
                        { offset: 1, color: '#64b5f6' }
                    ])
                },
                data: predictions.temp_min.map(val => -val) // 取反以堆叠显示
            }
        ]
    };
    temperatureRangeChart.setOption(rangeOption);
}

// 模拟数据示例 (当 API 不可用时使用)
function loadDemoData() {
    const demoData = {
        status: 'success',
        predictions: {
            dates: ['2025-03-04', '2025-03-05', '2025-03-06', '2025-03-07', '2025-03-08', '2025-03-09', '2025-03-10'],
            temp_max: [1, 2, 3, 4, 5, 6, 7],
            temp_min: [-1, -2, -3, -4, -5, -6, -7]
        }
    };
    displayPrediction(demoData.predictions, '北京');
}

// 在脚本加载完毕后添加一个快速测试按钮 (只在开发环境下显示)
document.addEventListener('DOMContentLoaded', function () {
    // 检查 URL 参数是否包含 demo 模式
    const urlParams = new URLSearchParams(window.location.search);
    if (urlParams.has('demo')) {
        const testBtn = document.createElement('button');
        testBtn.innerText = '加载示例数据';
        testBtn.className = 'btn btn-sm btn-secondary mt-2'; // 使用 Bootstrap 样式
        testBtn.style.position = 'fixed';
        testBtn.style.bottom = '10px';
        testBtn.style.right = '10px';
        testBtn.style.zIndex = 1000;
        testBtn.onclick = loadDemoData;
        document.body.appendChild(testBtn);
    }
});

// 添加导出数据功能 (使用 Bootstrap 样式)
document.addEventListener('click', function (e) {
    if (e.target.closest('.btn-outline-info')) { // 修改按钮选择器
        exportTableData();
    }
});

// 导出表格数据为 CSV
function exportTableData() {
    const table = document.querySelector('table');
    if (!table || table.rows.length <= 1) {
        alert('没有数据可导出');
        return;
    }

    // 获取当前城市名称
    const cityName = document.getElementById('citySelect').value || '未知城市';

    // 获取当前时间，格式化为 YYYY-MM-DD-HHmmss
    const now = new Date();
    const year = now.getFullYear();
    const month = String(now.getMonth() + 1).padStart(2, '0');
    const day = String(now.getDate()).padStart(2, '0');
    const hours = String(now.getHours()).padStart(2, '0');
    const minutes = String(now.getMinutes()).padStart(2, '0');
    const seconds = String(now.getSeconds()).padStart(2, '0');
    const timeStr = `${year}-${month}-${day}-${hours}${minutes}${seconds}`;

    // 生成文件名
    const fileName = `${cityName}天气预测数据${timeStr}.csv`;

    let csv = [];

    // 获取表头
    let headerRow = [];
    const headers = table.querySelectorAll('th');
    for (let i = 0; i < headers.length; i++) {
        headerRow.push(headers[i].textContent);
    }
    csv.push(headerRow.join(','));

    // 获取数据行
    const rows = table.querySelectorAll('tbody tr');
    for (let i = 0; i < rows.length; i++) {
        let row = [];
        const cells = rows[i].querySelectorAll('td');
        for (let j = 0; j < cells.length; j++) {
             // 移除°C符号
            let cellText = cells[j].textContent.replace('°C', '');
            row.push(cellText);
        }
        csv.push(row.join(','));
    }

    // 创建 CSV 内容 - 修复中文乱码问题
    const csvString = csv.join('\n');
    const BOM = "\uFEFF"; // 添加 BOM 标记以支持 UTF-8 中文

    // 使用 Blob 对象创建 CSV 文件，并指定正确的编码
    const blob = new Blob([BOM + csvString], { type: 'text/csv;charset=utf-8' });

    // 创建下载链接
    const link = document.createElement('a');
    link.href = URL.createObjectURL(blob);
    link.setAttribute('download', fileName);
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);

    // 释放 URL 对象
    setTimeout(() => {
        URL.revokeObjectURL(link.href);
    }, 100);
}
