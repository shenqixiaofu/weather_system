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
    "广西": ["南宁", "桂林", "崇左", "柳州", "来宾", "梧州", "贺州", "贵港", "玉林", "百色", "钦州", "河池", "北海", "防城港"],
    "海南": ["海口", "三亚", "三沙"],
    "香港": ["香港"],
    "澳门": ["澳门"],
    "台湾": ["台北", "高雄", "台中"]
};

let currentPage = 1; // 当前页码
let pageSize = 30;   // 每页显示条数
let totalPages = 1;  // 总页数
let allData = [];    // 当前页数据
let currentCityForTrend = ''; // 当前趋势图显示的城市
let lastQueryParams = {};     // 上一次查询参数

// 显示加载动画
function showLoader() {
    document.getElementById('loader').style.display = 'block';
    document.getElementById('tableSection').style.display = 'none';
    document.getElementById('noDataTip').style.display = 'none';
}

// 隐藏加载动画
function hideLoader() {
    document.getElementById('loader').style.display = 'none';
    document.getElementById('tableSection').style.display = 'block';
}

// 显示无数据提示
function showNoData() {
    document.getElementById('noDataTip').style.display = 'block';
    document.getElementById('tableSection').style.display = 'none';
}

// 初始化省份下拉菜单
const provinceSelect = document.getElementById('provinceSelect');
Object.keys(provinceData).forEach(province => {
    const option = document.createElement('option');
    option.value = province;
    option.textContent = province;
    provinceSelect.appendChild(option);
});

// 省份改变时，城市下拉菜单联动
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
    document.getElementById('trendTitle').textContent = '温度趋势图（请选择城市）';
    renderChart([]);
});

// 获取当前筛选条件
function getQueryParams() {
    const province = document.getElementById('provinceSelect').value;
    const city = document.getElementById('citySelect').value;
    const startDate = document.getElementById('startDate').value;
    const endDate = document.getElementById('endDate').value;
    return {
        province,
        city,
        start: startDate,
        end: endDate
    };
}

// 加载数据并渲染表格、趋势图、分页
function loadData(page = 1) {
    const params = getQueryParams(); // 获取筛选条件
    lastQueryParams = params;
    params.page = page;
    params.size = pageSize;
    // 显示加载动画
    showLoader();
    fetch('/api/weather?' + new URLSearchParams(params))
        .then(response => response.json())
        .then(result => {
            const data = result.data || [];
            const total = result.total || 0;
            allData = data;
            currentPage = page;
            totalPages = Math.ceil(total / pageSize);
            // 隐藏加载
            if (!data || data.length === 0) {
                showNoData();
                renderChart([]); // 清空趋势图
                updateTrendTitle('请选择城市');
                return;
            }
            hideLoader();
            renderTablePage(data); // 渲染表格
            renderPagination(totalPages, currentPage); // 渲染分页
            // 如果选中了城市，渲染趋势图
            if (params.city) {
                renderChart(data.filter(d => d.city_name === params.city));
                updateTrendTitle(params.city);
                currentCityForTrend = params.city;
            } else {
                renderChart([]);
                updateTrendTitle('请选择城市');
                currentCityForTrend = '';
            }
        })
        .catch(err => {
            showNoData();
            renderChart([]);
            updateTrendTitle('请选择城市');
            console.error("数据加载失败", err);
        });
}

// 渲染当前页数据到表格
function renderTablePage(data) {
    let tbody = '';
    data.forEach(item => {
        tbody += `<tr style="border:1px solid #e0e0e0;">
            <td style="border:1px solid #e0e0e0;text-align:center;">${item.city_name}</td>
            <td style="border:1px solid #e0e0e0;text-align:center;">${item.date}</td>
            <td style="border:1px solid #e0e0e0;text-align:center;">${item.temp_max}℃</td>
            <td style="border:1px solid #e0e0e0;text-align:center;">${item.temp_min}℃</td>
            <td style="border:1px solid #e0e0e0;text-align:center;">${item.weather}</td>
        </tr>`;
    });
    document.getElementById('dataBody').innerHTML = tbody;
}

// 渲染分页按钮
function renderPagination(totalPages, currentPage) {
    const nav = document.getElementById('paginationNav');
    const ul = document.getElementById('pagination');
    if (totalPages <= 1) {
        nav.style.display = 'none';
        return;
    }
    nav.style.display = 'block';
    ul.innerHTML = '';
    // 在第一页时设置上一页按钮不可用
    ul.innerHTML += `<li class="page-item${currentPage === 1 ? ' disabled' : ''}"><a class="page-link" href="#" onclick="gotoPage(${currentPage - 1})">上一页</a></li>`;
    // 页码按钮
    for (let i = 1; i <= totalPages; i++) {
        if (i === 1 || i === totalPages || Math.abs(i - currentPage) <= 2) {
            ul.innerHTML += `<li class="page-item${i === currentPage ? ' active' : ''}"><a class="page-link" href="#" onclick="gotoPage(${i})">${i}</a></li>`;
        } else if (i === currentPage - 3 || i === currentPage + 3) {
            //间隔超过3页的位置显示省略号
            ul.innerHTML += `<li class="page-item disabled"><span class="page-link">...</span></li>`;
        }
    }
    // 在第最后一页时设置下一页按钮不可用
    ul.innerHTML += `<li class="page-item${currentPage === totalPages ? ' disabled' : ''}"><a class="page-link" href="#" onclick="gotoPage(${currentPage + 1})">下一页</a></li>`;
}

// 分页跳转函数（全局）
window.gotoPage = function(page) {
    if (page < 1 || page > totalPages) return;
    loadData(page);
}

// 更新趋势图标题
function updateTrendTitle(city) {
    document.getElementById('trendTitle').textContent = city ? `温度趋势图（${city}）` : '温度趋势图（请选择城市）';
}

// 渲染温度趋势图
function renderChart(data) {
    const chart = echarts.init(document.getElementById('tempChart'));
    chart.clear(); // 先清空，防止残留"暂无数据"
    if (!data || data.length === 0) {
        chart.setOption({
            title: { text: '暂无数据', left: 'center', top: 'middle', textStyle: { color: '#aaa', fontSize: 18 } }
        });
        return;
    }
    // 提取日期和温度数据
    const dates = data.map(d => d.date).reverse();
    const maxTemps = data.map(d => d.temp_max).reverse();
    const minTemps = data.map(d => d.temp_min).reverse();
    const option = {
        tooltip: {
            trigger: 'axis',
            formatter: '{b}<br/>{a0}: {c0}℃<br/>{a1}: {c1}℃',
            axisPointer: { type: 'shadow' }
        },
        legend: {
            data: ['最高温', '最低温'],
            textStyle: { color: '#555' },
            right: '5%'
        },
        grid: {
            left: '3%', right: '4%', bottom: '15%', containLabel: true
        },
        xAxis: {
            type: 'category',
            data: dates,
            axisLine: { lineStyle: { color: '#ccc' } },
            axisLabel: {
                rotate: 45, margin: 20, interval: 0,
                formatter: function(value) { return value.split('-').slice(1).join('-'); }
            }
        },
        yAxis: {
            type: 'value', name: '温度(℃)',
            axisLine: { lineStyle: { color: '#ccc' } },
            splitLine: { lineStyle: { type: 'dashed', color: '#eee' } }
        },
        series: [
            {
                name: '最高温', type: 'line', data: maxTemps, smooth: true,
                lineStyle: { width: 3, color: '#ff7675' }, itemStyle: { color: '#ff7675' }
            },
            {
                name: '最低温', type: 'line', data: minTemps, smooth: true,
                lineStyle: { width: 3, color: '#74b9ff' }, itemStyle: { color: '#74b9ff' }
            }
        ]
    };
    chart.setOption(option);
}

// 当DOM加载完成时执行的初始化操作
document.addEventListener('DOMContentLoaded', function() {
    document.getElementById('startDate').value = "2025-01-01";
    document.getElementById('endDate').value = "";
    loadData(1);
});

// 监听窗口大小变化,调整图表大小
window.addEventListener('resize', function() {
     const chart = echarts.init(document.getElementById('tempChart'));
    chart.resize();
});

// 导出当前筛选条件下的数据为CSV
function exportTableData() {
    // 获取当前筛选条件
    const params = getQueryParams();
    params.page = 1;
    params.size = 10000; // 最大1万条数据

    fetch('/api/weather?' + new URLSearchParams(params))
        .then(response => response.json())
        .then(result => {
            const data = result.data || [];
            if (!data.length) {
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

            // 生成文件名
            const fileName = cityName
                ? `${provinceName}-${cityName}天气数据${timeStr}.csv`
                : `${provinceName}天气数据${timeStr}.csv`;

            // 生成CSV内容
            let csv = [];
            // 表头
            csv.push('城市,日期,最高温,最低温,天气');
            // 数据行
            data.forEach(item => {
                csv.push([
                    item.city_name,
                    item.date,
                    item.temp_max,
                    item.temp_min,
                    item.weather
                ].join(','));
            });

            const csvString = csv.join('\n');
            const BOM = "\uFEFF"; // 添加BOM标记以支持UTF-8
            const blob = new Blob([BOM + csvString], { type: 'text/csv;charset=utf-8' });
            // 创建下载链接
            const link = document.createElement('a');
            link.href = URL.createObjectURL(blob);
            link.setAttribute('download', fileName);
            document.body.appendChild(link);
            link.click();
            document.body.removeChild(link);
            setTimeout(() => {
                URL.revokeObjectURL(link.href)
            }, 100);
        });
}

// 城市下拉菜单切换时，自动拉取该城市全部数据并刷新趋势图
const citySelect = document.getElementById('citySelect');
citySelect.addEventListener('change', function() {
    const city = this.value;
    if (city) {
        // 只显示该城市的趋势
        // 重新请求该城市所有数据用于趋势图
        const params = getQueryParams();
        params.city = city;
        params.page = 1;
        params.size = 1000; // 拉取该城市全部数据用于趋势图
        fetch('/api/weather?' + new URLSearchParams(params))
            .then(response => response.json())
            .then(result => {
                renderChart(result.data || []);
                updateTrendTitle(city);
                currentCityForTrend = city;
            });
    } else {
        renderChart([]);
        updateTrendTitle('请选择城市');
        currentCityForTrend = '';
    }
});