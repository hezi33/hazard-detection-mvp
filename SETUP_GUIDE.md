# 安装和运行指南

由于当前环境限制，以下是完整的安装和运行步骤：

## 1. 环境要求

### 系统要求
- Python 3.8+
- pip 包管理器
- 虚拟环境支持（可选）

### Python包依赖
```
fastapi==0.104.1
uvicorn[standard]==0.24.0
opencv-python==4.8.1.78
numpy==1.24.3
pillow==10.1.0
ultralytics==8.0.196
python-multipart==0.0.6
aiofiles==23.2.1
```

## 2. 安装步骤

### 方式一：使用虚拟环境（推荐）
```bash
# 1. 创建虚拟环境
python -m venv venv

# 2. 激活虚拟环境
# Linux/Mac:
source venv/bin/activate
# Windows:
# venv\Scripts\activate

# 3. 安装依赖
pip install -r requirements.txt
```

### 方式二：直接安装
```bash
pip install fastapi uvicorn opencv-python numpy pillow ultralytics
```

## 3. 运行服务

### 本地运行
```bash
# 启动服务
python app.py

# 或使用uvicorn
uvicorn app:app --host 0.0.0.0 --port 8000 --reload
```

### Docker运行
```bash
# 构建镜像
docker build -t hazard-detection-mvp .

# 运行容器
docker run -p 8000:8000 hazard-detection-mvp

# 或使用docker-compose
docker-compose up
```

## 4. 访问服务

服务启动后，访问以下地址：

- **Web界面**: http://localhost:8000
- **API端点**: http://localhost:8000/api/check
- **健康检查**: http://localhost:8000/health

## 5. 测试方法

### 使用curl测试API
```bash
curl -X POST -F "file=@test.jpg" http://localhost:8000/api/check
```

### 使用Python测试
```python
import requests

# 测试健康检查
response = requests.get("http://localhost:8000/health")
print(response.json())

# 测试图片检测
with open("test.jpg", "rb") as f:
    files = {"file": f}
    response = requests.post("http://localhost:8000/api/check", files=files)
    print(response.json())
```

### 运行测试脚本
```bash
# 快速测试
python test_api.py quick

# 完整测试
python test_api.py
```

## 6. 创建测试图片

如果没有真实图片，可以使用以下命令创建测试图片：

```bash
python create_test_image.py
```

这会创建两张测试图片：
- `test_images/fire_extinguisher_green.jpg` - 正常（绿区）
- `test_images/fire_extinguisher_red.jpg` - 隐患（红区）

## 7. 项目结构说明

```
hazard-detection-mvp/
├── app.py              # FastAPI主应用
├── detector.py         # 检测核心逻辑
├── templates/          # HTML模板
│   └── index.html     # Web上传界面
├── requirements.txt    # 依赖列表
├── Dockerfile         # Docker构建文件
├── docker-compose.yml # Docker编排
├── test_api.py        # 测试脚本
├── create_test_image.py # 创建测试图片
├── run.sh             # 启动脚本
└── README.md          # 项目文档
```

## 8. 故障排除

### 问题1：端口被占用
```bash
# 检查端口占用
netstat -tulpn | grep :8000

# 或使用其他端口
uvicorn app:app --host 0.0.0.0 --port 8001
```

### 问题2：依赖安装失败
```bash
# 升级pip
pip install --upgrade pip

# 使用国内镜像
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
```

### 问题3：YOLO模型下载慢
```bash
# 手动下载模型
wget https://github.com/ultralytics/assets/releases/download/v0.0.0/yolov8n.pt
# 放入 ~/.cache/ultralytics/ 目录
```

### 问题4：OpenCV无法导入
```bash
# 重新安装OpenCV
pip uninstall opencv-python opencv-python-headless
pip install opencv-python-headless
```

## 9. 开发说明

### 代码结构
- `detector.py` - 核心检测逻辑
  - `FireExtinguisherDetector`类
  - 灭火器检测、压力表定位、指针角度判断
- `app.py` - Web服务
  - FastAPI应用
  - API端点定义
  - 文件上传处理

### 扩展开发
要添加新的检测功能：
1. 在`detector.py`中添加新的检测类
2. 在`app.py`中添加对应的API端点
3. 更新Web界面

## 10. 性能优化

### 模型缓存
首次运行会自动下载YOLO模型（~6MB），后续运行会使用缓存。

### 内存管理
- 单张图片处理内存：~500MB
- 建议配置：2GB RAM以上

### 处理时间
- 模型加载：2-3秒（首次）
- 单张图片检测：1-2秒
- 总响应时间：< 3秒

---

**注意**：当前为MVP版本，主要用于验证技术链路。实际部署时可能需要根据具体环境调整配置。