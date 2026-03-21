# 🔥 隐患检测MVP - 灭火器压力表检测

一个基于计算机视觉的灭火器压力表检测系统MVP版本，用于验证"CV工具 + API + Docker + Web + OpenClaw调用"技术链路。

## 🎯 核心功能

- ✅ **灭火器检测** - 基于YOLOv8的目标检测
- ✅ **压力表定位** - 霍夫圆检测找到表盘
- ✅ **指针角度检测** - 霍夫直线检测判断指针位置
- ✅ **隐患判断** - 绿区(正常)/黄区(警告)/红区(隐患)
- ✅ **RESTful API** - 标准HTTP接口
- ✅ **Web界面** - 现代化上传和展示
- ✅ **Docker支持** - 一键容器化部署
- ✅ **完整测试** - 测试脚本和示例

## 🚀 快速开始（5分钟跑通）

### 方式一：本地运行（最简单）

```bash
# 1. 克隆仓库
git clone <repository-url>
cd hazard-detection-mvp

# 2. 安装依赖
pip install -r requirements.txt

# 3. 启动服务
python app.py
```

### 方式二：Docker运行（推荐）

```bash
# 1. 克隆仓库
git clone <repository-url>
cd hazard-detection-mvp

# 2. 使用docker-compose（一键启动）
docker-compose up --build

# 或直接使用Docker
docker build -t hazard-detection-mvp .
docker run -p 8000:8000 hazard-detection-mvp
```

## 🌐 访问服务

服务启动后，打开浏览器访问：

- **Web上传界面**: http://localhost:8000
- **API端点**: http://localhost:8000/api/check
- **健康检查**: http://localhost:8000/health
- **测试端点**: http://localhost:8000/test

## 📡 API使用

### 检测接口

**POST** `/api/check`

```bash
# 使用curl测试
curl -X POST -F "file=@test.jpg" http://localhost:8000/api/check

# 使用Python测试
import requests
response = requests.post('http://localhost:8000/api/check', 
                         files={'file': open('test.jpg', 'rb')})
print(response.json())
```

### 响应格式

```json
{
  "success": true,
  "hazard_detected": false,
  "confidence": 0.92,
  "hazard_name": "灭火器压力表正常",
  "reasoning": [
    "检测到灭火器 (置信度: 0.95)",
    "定位压力表区域 (半径: 45px)",
    "检测到指针 (角度: 45.0°)",
    "指针位于绿区"
  ],
  "evidence": {
    "fire_extinguisher_bbox": [100, 150, 300, 400],
    "gauge_center": [200, 250],
    "gauge_radius": 45,
    "pointer_angle": 45.0,
    "zone": "green"
  }
}
```

## 🧪 测试验证

### 创建测试图片
```bash
python create_test_image.py
```

### 运行测试套件
```bash
# 快速测试
python test_api.py quick

# 完整测试
python test_api.py
```

### 手动测试
1. 访问 http://localhost:8000
2. 上传 `test_images/fire_extinguisher_green.jpg`（正常）
3. 上传 `test_images/fire_extinguisher_red.jpg`（隐患）
4. 查看检测结果

## 🛠️ 技术架构

```
输入图片
    ↓
[YOLOv8] 灭火器检测 → 边界框
    ↓
[霍夫圆检测] 压力表定位 → 圆心+半径
    ↓  
[霍夫直线检测] 指针角度检测 → 角度(0-360°)
    ↓
[规则判断] 绿区(0-120°)/黄区(120-240°)/红区(240-360°)
    ↓
结构化输出（JSON）
```

## 📁 项目结构

```
hazard-detection-mvp/
├── app.py              # FastAPI主应用
├── detector.py         # 检测核心逻辑
├── templates/
│   └── index.html     # Web上传界面
├── requirements.txt    # Python依赖
├── Dockerfile         # Docker构建
├── docker-compose.yml # Docker编排
├── test_api.py        # 测试脚本
├── create_test_image.py # 创建测试图片
├── simple_test.py     # 简化测试
├── run.sh             # 启动脚本
├── README.md          # 本文档
├── SETUP_GUIDE.md     # 详细安装指南
└── test_images/       # 测试图片目录
```

## 🔧 配置说明

### 环境要求
- **Python**: 3.8+
- **内存**: 建议2GB+（YOLO模型需要~500MB）
- **磁盘**: 100MB+（模型缓存）

### 模型配置
- **YOLO模型**: yolov8n.pt（自动下载，~6MB）
- **检测类别**: COCO数据集的80个类别
- **置信度阈值**: 0.5

### 检测参数
- **绿区**: 0-120°（正常）
- **黄区**: 120-240°（警告）
- **红区**: 240-360°（隐患）

## 📈 性能指标

- **模型加载**: 2-3秒（首次）
- **单图检测**: 1-2秒
- **内存占用**: ~500MB
- **响应时间**: < 3秒
- **准确率目标**: >80%（需真实数据验证）

## 🐳 Docker部署

### 生产环境部署
```bash
# 构建生产镜像
docker build -t hazard-detection:prod .

# 运行容器
docker run -d \
  --name hazard-detection \
  -p 8000:8000 \
  --restart unless-stopped \
  hazard-detection:prod
```

### 使用docker-compose
```yaml
# 查看 docker-compose.yml 文件
version: '3.8'
services:
  hazard-detection:
    build: .
    ports:
      - "8000:8000"
    restart: unless-stopped
```

## 🔄 开发扩展

### 添加新的检测工具
1. 在 `detector.py` 中添加新的检测类
2. 在 `app.py` 中添加对应的API端点
3. 更新Web界面（如果需要）

### 优化指针检测
当前使用霍夫直线检测，可优化为：
1. 模板匹配
2. 深度学习关键点检测
3. 边缘检测+角度计算

## 🐛 故障排除

### 常见问题

**Q: 依赖安装失败**
```bash
# 使用国内镜像
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple

# 或升级pip
pip install --upgrade pip
```

**Q: YOLO模型下载慢**
```bash
# 手动下载
wget https://github.com/ultralytics/assets/releases/download/v0.0.0/yolov8n.pt
mv yolov8n.pt ~/.cache/ultralytics/
```

**Q: OpenCV导入错误**
```bash
pip uninstall opencv-python opencv-python-headless
pip install opencv-python-headless
```

**Q: 端口被占用**
```bash
# 使用其他端口
python app.py --port 8001
# 或
uvicorn app:app --host 0.0.0.0 --port 8001
```

### 日志查看
```bash
# 查看服务日志
python app.py 2>&1 | tee app.log

# Docker日志
docker logs hazard-detection-mvp
```

## 📄 许可证

MIT License

## 🤝 贡献

欢迎提交Issue和Pull Request！

## 📞 支持

如有问题，请：
1. 查看 `SETUP_GUIDE.md` 详细指南
2. 运行 `python simple_test.py` 诊断
3. 提交Issue

---

**版本**: 1.0.0  
**状态**: MVP验证版  
**目标**: 验证CV工具+API+Docker+Web技术链路  
**下一步**: 真实数据测试 → 算法优化 → 扩展更多检测工具