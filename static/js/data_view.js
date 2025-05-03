// static/js/data_view.js

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

function showLoader() {
    document.getElementById('loader').style.display = 'block';
    document.getElementById('tableSection').style.display = 'none';
}

function hideLoader() {
    document.getElementById('loader').style.display = 'none';
    document.getElementById('tableSection').style.display = 'block';
}
// 初始化省份下拉菜单
const provinceSelect = document.getElementById('provinceSelect');
Object.keys(provinceData).forEach(province => {
    const option = document.createElement('option');
    option.value = province;
    option.textContent = province;
    provinceSelect.appendChild(option);
});

// 省份改变，城市选择对应改变
provinceSelect.addEventListener('change', (e) => {
    const citySelect = document.getElementById('citySelect');
    citySelect.innerHTML = '<option value="">请先选择省份</option>';
    citySelect.disabled = !e.target.value;
    if (e.target.value) {
        const cities = provinceData[e.target.value];
        cities.forEach(city => {
            const option = document.createElement('option');
            option.value = city;
            option.textContent = city;
            citySelect.appendChild(option);
        })
    }
});

//发送请求
function loadData() {
    const province = document.getElementById('provinceSelect').value;
    const city = document.getElementById('citySelect').value;
    const startDate = document.getElementById('startDate').value;
    const endDate = document.getElementById('endDate').value;

     // 构建参数对象
    const params = {
      start: startDate,
      end: endDate,
      period: 'day'
    };
    if (province) {
        params.province = province;
    }
    if (city) {
        params.city = city;
    }

    // 显示加载动画
    showLoader();
    // 发送请求
    fetch('/api/weather?' + new URLSearchParams(params))
        .then(response => response.json())
        .then(data => {
            // 隐藏加载
            hideLoader();
            // 更新表格
            let tbody = '';
            data.forEach(item => {
                tbody += `<tr>
                    <td>${item.city_name}</td>
                    <td>${item.date}</td>
                    <td>${item.temp_max}℃</td>
                    <td>${item.temp_min}℃</td>
                    <td>${item.weather}</td>
                </tr>`;
            });
            document.getElementById('dataBody').innerHTML = tbody;
            // 更新图表
            renderChart(data);
        })
        .catch(err => {
            hideLoader();
            console.error("数据加载失败", err);
        });
}

function renderChart(data) {
    const chart = echarts.init(document.getElementById('tempChart'));

    // 提取日期和温度数据
    const dates = data.map(d => d.date).reverse();
    const maxTemps = data.map(d => d.temp_max).reverse();
    const minTemps = data.map(d => d.temp_min).reverse();


    const option = {
        tooltip: {
            trigger: 'axis',
            formatter: '{b}<br/>{a0}: {c0}℃<br/>{a1}: {c1}℃',
            axisPointer: {
                type: 'shadow'
            }
        },
        legend: {
            data: ['最高温', '最低温'],
            textStyle: {
                color: '#555'
            },
            right: '5%'
        },
        grid: {
            left: '3%',
            right: '4%',
            bottom: '15%',  // 修改：底部留更多空间
            containLabel: true
        },
        xAxis: {
            type: 'category',
            data: dates,
            axisLine: {
                lineStyle: {
                    color: '#ccc'
                }
            },
            axisLabel: {
                rotate: 45,  // 新增：标签旋转45度
                margin: 20,  // 新增：标签与坐标轴的间距
                interval: 0, // 强制显示所有标签
                formatter: function(value) {
                    return value.split('-').slice(1).join('-'); // 只显示月-日
                }
            }
        },
        yAxis: {
            type: 'value',
            name: '温度(℃)',
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
            }
        },
        series: [
            {
                name: '最高温',
                type: 'line',
                data: maxTemps,
                smooth: true,
                 lineStyle: {
                    width: 3,
                    color: '#ff7675'
                },
                itemStyle: {
                    color: '#ff7675'
                }
            },
            {
                name: '最低温',
                type: 'line',
                data: minTemps,
                smooth: true,
                 lineStyle: {
                    width: 3,
                    color: '#74b9ff'
                },
                itemStyle: {
                    color: '#74b9ff'
                }
            }
        ]
    };
    chart.setOption(option);
}

//初始加载与事件绑定
document.addEventListener('DOMContentLoaded', function() {

    document.getElementById('startDate').value = "2025-01-01";
    document.getElementById('endDate').value = "";

    loadData();
});

// 监听窗口大小变化,调整图表大小
window.addEventListener('resize', function() {
     const chart = echarts.init(document.getElementById('tempChart'));
    chart.resize();
});

//导出数据
function exportTableData() {
    const table = document.querySelector('table');
    if (!table || table.rows.length <= 1) {
        alert('没有数据可导出');
        return;
    }

    // 获取当前省份和城市名称
    const provinceName = document.getElementById('provinceSelect').value || '全部省份';
    const cityName = document.getElementById('citySelect').value || '全部城市';


    // 获取当前时间，格式化为 YYYY-MM-DD-HHmmss
    const now = new Date();
    const year = now.getFullYear();
    const month = String(now.getMonth() + 1).padStart(2, '0');
    const day = String(now.getDate()).padStart(2, '0');
    const hours = String(now.getHours()).padStart(2, '0');
    const minutes = String(now.getMinutes()).padStart(2, '0');
    const seconds = String(now.getSeconds()).padStart(2, '0');
    const timeStr = `${year}-${month}-${day}-${hours}${minutes}${seconds}`;

    // 生成文件名, 根据是否有城市来决定文件名
    const fileName = cityName
        ? `${provinceName}-${cityName}天气数据${timeStr}.csv`
        : `${provinceName}天气数据${timeStr}.csv`;

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
            let cellText = cells[j].textContent.replace('℃', ''); // 移除°C
            row.push(cellText);
        }
        csv.push(row.join(','));
    }
    // 创建CSV内容
    const csvString = csv.join('\n');
    const BOM = "\uFEFF"; // 添加BOM标记以支持UTF-8
    const blob = new Blob([BOM + csvString], { type: 'text/csv;charset=utf-8' });
    //创建下载链接
    const link = document.createElement('a');
    link.href = URL.createObjectURL(blob);
    link.setAttribute('download', fileName);
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    setTimeout(() => {
        URL.revokeObjectURL(link.href)
    }, 100);
}