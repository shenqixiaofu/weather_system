let myChart;
let showLegend = true;
let lastUpdated = new Date();

// 等待DOM加载完成
document.addEventListener('DOMContentLoaded', function() {
    initMap();
    bindButtonEvents();

    // 初始化最后更新时间
    updateLastUpdatedTime();
});

// 更新最后更新时间显示
function updateLastUpdatedTime() {
    const options = { hour: '2-digit', minute: '2-digit', second: '2-digit' };
    document.getElementById('last-updated').textContent = lastUpdated.toLocaleTimeString('zh-CN', options);
}

// 初始化地图函数
async function initMap() {
    try {
        if (!myChart) {
            myChart = echarts.init(document.getElementById('map-container'));
            // 监听 echarts 的初始化完成事件 (重要!)
            myChart.on('finished', () => {
              myChart.resize();
           });
        }
        // 显示加载状态
        myChart.showLoading({
            text: '正在加载中国天气数据...',
            color: '#1e88e5',
            textColor: '#000',
            maskColor: 'rgba(255, 255, 255, 0.8)',
            zlevel: 0
        });

        const [mapJson, provinceData] = await Promise.all([
            fetch('/static/json/china.json').then(res => res.json()),
            fetch('/get_provinces_temp').then(res => res.json())
        ]);

        echarts.registerMap('china', mapJson);
        renderMap(provinceData);
        myChart.hideLoading();

        // 更新最后更新时间
        lastUpdated = new Date();
        updateLastUpdatedTime();

        return true;
    } catch (error) {
        console.error('初始化失败:', error);
        myChart.hideLoading();
        // 显示错误提示
        myChart.setOption({
            title: {
                text: '数据加载失败，请刷新重试',
                subtext: '请检查网络连接并点击刷新按钮',
                left: 'center',
                top: 'center',
                textStyle: {
                    fontSize: 20,
                    color: '#333'
                },
                subtextStyle: {
                    fontSize: 14,
                    color: '#666'
                }
            }
        });

        return false;
    }
}

// 渲染地图数据
function renderMap(data) {
    const option = {
        backgroundColor: '#fafbfe',
        title: {
            text: '中国各省实时温度',
            subtext: '数据实时更新，每6小时刷新一次',
            left: 'center',
            top: 10,
            textStyle: {
                fontSize: 18,
                color: '#333'
            },
            subtextStyle: {
                fontSize: 12,
                color: '#666'
            }
        },
        tooltip: {
            trigger: 'item',
            formatter: params => {
                const data = params.data || {};
                return `<div style="font-weight:bold;margin-bottom:5px;font-size:14px;">${params.name}</div>
                        <div style="margin:3px 0;">平均温度: <span style="float:right;font-weight:bold;">${data.value ?? '--'}℃</span></div>
                        <div style="margin:3px 0;">最高温度: <span style="float:right;color:#d73027;font-weight:bold;">${data.temp_max || '--'}℃</span></div>
                        <div style="margin:3px 0;">最低温度: <span style="float:right;color:#313695;font-weight:bold;">${data.temp_min || '--'}℃</span></div>`;
            },
            backgroundColor: 'rgba(255,255,255,0.9)',
            borderColor: '#1e88e5',
            borderWidth: 1,
            padding: 10,
            textStyle: {
                color: '#333'
            }
        },
        visualMap: {
            min: -25,
            max: 45,
            text: ['高温', '低温'],
            realtime: false,
            calculable: true,
            show: showLegend,
            inRange: {
                color: [
                    '#313695', '#4575b4', '#74add1', '#abd9e9',
                    '#e0f3f8', '#ffffbf', '#fee090',
                    '#fdae61', '#f46d43', '#d73027', '#a50026'
                ]
            },
            orient: 'horizontal',
            left: 'center',
            bottom: 20,
            textStyle: {
                color: '#333'
            }
        },
        series: [{
            type: 'map',
            map: 'china',
            roam: true,
            zoom: 1.2,
            scaleLimit: {
                min: 1,
                max: 5
            },
            data: data,
            emphasis: {
                label: {
                    show: true,
                    color: '#333',
                    fontSize: 12
                },
                itemStyle: {
                    areaColor: '#a50026',
                    borderWidth: 1
                }
            },
            itemStyle: {
                borderColor: '#ccc',
                borderWidth: 0.5,
                shadowColor: 'rgba(0, 0, 0, 0.2)',
                shadowBlur: 5
            },
            select: {
                itemStyle: {
                    areaColor: '#1e88e5'
                }
            }
        }]
    };
    myChart.setOption(option);

    // 点击事件：显示详细信息面板
    myChart.on('click', function(params) {
        const data = params.data || {};
        if(data && data.value) {
            const weatherDetail = document.getElementById('weather-detail');
            const provinceName = document.getElementById('province-name');
            const weatherData = document.getElementById('weather-data');

            provinceName.innerHTML = `${params.name} <span class="text-muted small">实时天气数据</span>`;

            let weatherHtml = `
                <div class="mb-2">
                    <div class="d-flex justify-content-between align-items-center">
                        <span>平均温度:</span>
                        <span class="fw-bold">${data.value}℃</span>
                    </div>
                </div>
                <div class="mb-2">
                    <div class="d-flex justify-content-between align-items-center">
                        <span>最高温度:</span>
                        <span class="text-danger fw-bold">${data.temp_max || '--'}℃</span>
                    </div>
                </div>
                <div class="mb-2">
                    <div class="d-flex justify-content-between align-items-center">
                        <span>最低温度:</span>
                        <span class="text-primary fw-bold">${data.temp_min || '--'}℃</span>
                    </div>
                </div>
            `;

            // 如果有更多气象数据，可以在这里添加
            if(data.humidity) {
                weatherHtml += `
                    <div class="mb-2">
                        <div class="d-flex justify-content-between align-items-center">
                            <span>湿度:</span>
                            <span class="fw-bold">${data.humidity}%</span>
                        </div>
                    </div>
                `;
            }

            weatherData.innerHTML = weatherHtml;
            weatherDetail.classList.remove('d-none');
        }
    });
}

// 切换图例显示/隐藏
function toggleLegend() {
    showLegend = !showLegend;
    if (myChart) {
        myChart.setOption({
            visualMap: {
                show: showLegend
            }
        });
    }
}

// 重置地图视图函数
function resetMapView() {
    if (myChart) {
        // 重置缩放和位置
        myChart.dispatchAction({
            type: 'restore'
        });

        // 关闭详细信息面板
        document.getElementById('weather-detail').classList.add('d-none');
    }
}

// 绑定按钮事件
function bindButtonEvents() {
    // 全屏按钮事件
    document.getElementById('fullscreen-btn').addEventListener('click', function() {
        const mapContainer = document.getElementById('map-container');

        if (!document.fullscreenElement) {
            if (mapContainer.requestFullscreen) {
                mapContainer.requestFullscreen();
            } else if (mapContainer.webkitRequestFullscreen) {
                mapContainer.webkitRequestFullscreen();
            } else if (mapContainer.msRequestFullscreen) {
                mapContainer.msRequestFullscreen();
            }
            this.innerHTML = '<i class="fas fa-compress me-1"></i>退出全屏';
        } else {
            if (document.exitFullscreen) {
                document.exitFullscreen();
            } else if (document.webkitExitFullscreen) {
                document.webkitExitFullscreen();
            } else if (document.msExitFullscreen) {
                document.msExitFullscreen();
            }
            this.innerHTML = '<i class="fas fa-expand me-1"></i>全屏查看';
        }
    });

    // 在进入/退出全屏后强制 resize
    setTimeout(() => {
      myChart.resize();
     }, 50); // 延迟一点时间, 确保浏览器完成了全屏/退出全屏的渲染

    // 重置视图按钮事件
    document.getElementById('reset-btn').addEventListener('click', function() {
        resetMapView();
    });

    // 监听全屏变化事件
    document.addEventListener('fullscreenchange', handleFullscreenChange);
    document.addEventListener('webkitfullscreenchange', handleFullscreenChange); // Safari
    document.addEventListener('mozfullscreenchange', handleFullscreenChange); // Firefox
    document.addEventListener('MSFullscreenChange', handleFullscreenChange);      // IE/Edge

    // 每6小时更新一次数据
    setInterval(async () => {
        try {
            const newData = await fetch('/get_provinces_temp').then(res => res.json());
            renderMap(newData);

            // 更新最后更新时间
            lastUpdated = new Date();
            updateLastUpdatedTime();

            // 显示更新提示
            const toast = document.createElement('div');
            toast.className = 'position-fixed bottom-0 end-0 p-3 m-3 bg-success text-white rounded shadow-sm';
            toast.style.zIndex = '1050';
            toast.innerHTML = '<i class="fas fa-check-circle me-2"></i>数据已更新';
            document.body.appendChild(toast);

            // 3秒后自动消失
            setTimeout(() => {
                toast.style.opacity = '0';
                toast.style.transition = 'opacity 0.5s';
                setTimeout(() => {
                    document.body.removeChild(toast);
                }, 500);
            }, 3000);
        } catch (error) {
            console.error('数据更新失败:', error);
        }
    }, 21600000); // 6小时 = 6 * 60 * 60 * 1000 = 21600000毫秒

    // 监听窗口大小变化，调整地图大小
    window.addEventListener('resize', function() {
        if (myChart) {
            myChart.resize();
        }
    });

    // 抽离的全屏状态改变处理函数
    function handleFullscreenChange() {
        if (!document.fullscreenElement && !document.webkitIsFullScreen && !document.mozFullScreen && !document.msFullscreenElement) {
            document.getElementById('fullscreen-btn').innerHTML = '<i class="fas fa-expand me-1"></i>全屏查看';
            // 退出全屏时，先重置容器大小，再 resize ECharts (关键!)
            const mapContainer = document.getElementById('map-container');
            mapContainer.style.width = '100%';       // 恢复宽度
            mapContainer.style.height = '78vh';    // 恢复高度 (重要!)
            setTimeout(() => {
                myChart.resize();
            }, 50);

        } else{
            // 进入全屏
             setTimeout(() => {
                  myChart.resize();
             }, 50); // 延迟一点时间

        }
    }
}