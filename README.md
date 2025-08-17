# 天气数据可视化系统

## 项目介绍

这是一个基于Python Flask开发的天气数据可视化系统，集成了数据采集、机器学习预测、实时天气查询、历史数据分析等功能。系统支持多用户管理、收藏地点、搜索历史记录，并提供丰富的可视化图表和预测分析功能。

## 功能特性

### 🌤️ 天气功能
- **实时天气查询**：支持全国各城市实时天气数据获取
- **7天天气预报**：提供未来7天的详细天气预报
- **24小时逐小时预报**：精确到小时的天气变化预测
- **历史天气数据**：存储和查询历史天气数据
- **天气预警信息**：获取官方天气预警通知

### 📊 数据可视化
- **温度趋势图**：展示温度变化趋势
- **降水量分析**：降雨量数据可视化
- **空气质量指数**：AQI数据图表展示
- **多城市对比**：支持多个城市数据对比
- **地图热力图**：全国天气状况地图展示

### 🤖 机器学习预测
- **天气预测模型**：基于历史数据的机器学习预测
- **多城市支持**：为多个主要城市训练专属预测模型
- **预测准确率评估**：模型性能实时监控
- **特征工程**：自动特征提取和选择

### 👥 用户管理
- **用户注册/登录**：完整的用户认证系统
- **个人资料管理**：用户信息和头像管理
- **收藏地点**：收藏常用城市快速查询
- **搜索历史**：记录用户搜索历史
- **管理员功能**：后台数据管理和系统设置

### 🔧 系统功能
- **定时数据更新**：自动爬取最新天气数据
- **数据备份**：数据库自动备份功能
- **系统监控**：运行状态和性能监控
- **日志记录**：完整的操作日志和错误日志

## 技术架构

### 后端技术栈
- **Flask**：轻量级Python Web框架
- **SQLAlchemy**：ORM框架，支持MySQL数据库
- **APScheduler**：定时任务调度
- **Scikit-learn**：机器学习库
- **Pandas/NumPy**：数据处理和分析

### 前端技术栈
- **Bootstrap 5**：响应式UI框架
- **ECharts**：数据可视化图表库
- **jQuery**：JavaScript库
- **FontAwesome**：图标库

### 数据存储
- **MySQL**：主数据库
- **Redis**：缓存和会话存储（可选）（当前系统暂无）
- **文件系统**：模型文件和静态资源存储

## 安装教程

### 环境要求
- Python 3.8+
- MySQL 5.7+
- Node.js 14+（前端构建，可选）

### 1. 克隆项目
```bash
git clone [项目地址]
cd weather-vis-system
```

### 2. 创建虚拟环境
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/Mac
python3 -m venv venv
source venv/bin/activate
```

### 3. 安装依赖
```bash
pip install -r requirements.txt
```

### 4. 数据库配置
1. 创建MySQL数据库：
```sql
CREATE DATABASE weather_system_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

2. 修改数据库配置：
编辑 `config.py` 文件，更新数据库连接信息：
```python
SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://username:password@localhost/weather_system_db'
```

### 5. 初始化数据库
```bash
# 创建数据表
flask db upgrade

# 或者使用Python脚本
python -c "from app import app, db; app.app_context().push(); db.create_all()"
```

### 6. 配置API密钥
1. 注册和风天气API账号：https://console.qweather.com
2. 获取API密钥并更新到 `config.py`：
```python
HEFENG_API_KEY = 'your_api_key_here'
```

### 7. 启动应用
```bash
# 开发模式
python app.py

# 或者使用Flask命令
flask run --host=0.0.0.0 --port=5000
```

访问 http://localhost:5000 查看应用

## 使用说明

### 首次使用
1. 注册管理员账号：首次注册的用户自动成为管理员
2. 配置系统设置：登录后访问管理面板进行系统配置
3. 添加城市数据：运行数据爬取脚本初始化城市天气数据

### 基本功能
- **天气查询**：首页搜索框输入城市名查询天气
- **查看预报**：点击城市卡片查看详细预报
- **收藏城市**：点击星标图标收藏常用城市
- **历史数据**：访问历史数据页面查看过往记录

### 管理员功能
- **数据管理**：后台管理界面可以管理所有数据
- **用户管理**：查看和管理注册用户
- **系统设置**：配置网站标题、API密钥等
- **备份恢复**：手动或自动备份数据库

### 数据更新
系统支持自动和手动数据更新：
- **自动更新**：配置定时任务，每30分钟自动更新
- **手动更新**：管理员可手动触发数据更新
- **批量更新**：支持批量城市数据更新

## 项目结构
```
├── app.py                 # 主应用文件
├── config.py             # 配置文件
├── requirements.txt      # Python依赖
├── models/               # 数据模型
│   ├── user_models.py   # 用户模型
│   ├── weather_models.py # 天气模型
│   └── ...
├── spider/               # 数据爬虫
│   ├── weather_spider.py # 天气数据爬取
│   └── data_cleaner.py   # 数据清洗
├── static/               # 静态资源
│   ├── css/              # 样式文件
│   ├── js/               # JavaScript
│   └── images/           # 图片资源
├── templates/            # HTML模板
├── migrations/           # 数据库迁移
├── logs/                 # 日志文件
└── backups/              # 数据库备份


## 开发说明

### 添加新城市
1. 在 `spider/province_data.py` 中添加城市信息
2. 运行数据爬取脚本更新数据
3. 训练新的预测模型

### 自定义图表
1. 修改对应的HTML模板文件
2. 在 `static/js/` 中添加新的图表配置
3. 更新后端API接口

### 扩展功能
- 添加新的天气指标
- 集成新的天气API
- 开发移动端适配

## 贡献指南

我们欢迎社区贡献！请按以下步骤进行：

1. Fork 本仓库
2. 创建功能分支：`git checkout -b feature/AmazingFeature`
3. 提交更改：`git commit -m 'Add some AmazingFeature'`
4. 推送到分支：`git push origin feature/AmazingFeature`
5. 创建 Pull Request

### 开发规范
- 遵循PEP 8 Python编码规范
- 添加适当的注释和文档
- 更新相关测试用例
- 确保通过所有测试

## 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情

## 联系方式

- 项目地址：[GitHub仓库地址]
- 问题反馈：[Issues页面]
- 邮箱联系：[your-email@example.com]

## 致谢

- 感谢和风天气提供天气数据API
- 感谢Bootstrap和ECharts提供的优秀前端框架
- 感谢所有贡献者的支持

---

**注意**：这是一个毕业设计项目，代码仅供参考学习。在生产环境中使用时，请进行适当的安全加固和性能优化。