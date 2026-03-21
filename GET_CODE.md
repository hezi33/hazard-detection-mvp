# 获取代码指南

## 方式一：直接下载压缩包（推荐）

代码已打包为 `hazard-detection-mvp.tar.gz` (18KB)

### 下载链接：
由于当前环境限制，请通过以下方式获取：

1. **如果你能访问这个服务器**：
   ```bash
   # 从 /home/hezi/hazard-detection-mvp.tar.gz 复制
   scp user@server:/home/hezi/hazard-detection-mvp.tar.gz .
   ```

2. **或者我可以通过其他方式发送给你**（请告诉我你希望的方式）

## 方式二：Git仓库

如果你希望使用Git，我可以：
1. 创建GitHub/GitLab仓库并推送
2. 或提供SSH访问权限

## 方式三：文件列表（手动复制）

如果你只需要核心文件，以下是必须的文件：

### 核心文件：
```
hazard-detection-mvp/
├── app.py              # FastAPI主应用
├── detector.py         # 检测核心逻辑
├── templates/index.html # Web界面
├── requirements.txt    # 依赖列表
├── Dockerfile         # Docker构建
├── docker-compose.yml # Docker编排
├── README.md          # 文档
└── test_api.py        # 测试脚本
```

## 验证清单

### ✅ 已确认可用的文件：
1. **requirements.txt** - 完整依赖列表
2. **Dockerfile** - 已验证可用（基于python:3.9-slim）
3. **docker-compose.yml** - 已验证配置正确
4. **所有核心代码** - 已完成开发

### 🔧 环境要求：
- Python 3.8+
- Docker（可选）
- 约500MB内存（运行YOLO模型）

## 快速开始

### 步骤1：获取代码
```bash
# 解压代码
tar -xzf hazard-detection-mvp.tar.gz
cd hazard-detection-mvp
```

### 步骤2：安装依赖
```bash
pip install -r requirements.txt
```

### 步骤3：运行服务
```bash
python app.py
```

### 步骤4：访问测试
- Web界面: http://localhost:8000
- API测试: `curl -X POST -F "file=@test.jpg" http://localhost:8000/api/check`

## Docker运行
```bash
# 使用docker-compose（推荐）
docker-compose up --build

# 或直接使用Docker
docker build -t hazard-detection-mvp .
docker run -p 8000:8000 hazard-detection-mvp
```

## 测试验证

运行测试脚本验证：
```bash
# 创建测试图片
python create_test_image.py

# 运行测试
python test_api.py
```

## 获取代码后请确认：

1. [ ] 成功解压/克隆代码
2. [ ] requirements.txt 依赖可安装
3. [ ] 能成功启动服务（python app.py）
4. [ ] 能访问Web界面（http://localhost:8000）
5. [ ] 能上传图片并看到检测结果

## 问题支持

如果遇到问题：
1. 检查Python版本（需要3.8+）
2. 检查网络连接（YOLO模型需要下载）
3. 查看错误日志
4. 联系我获取支持

---

**请告诉我你希望如何获取代码**，我会提供相应的访问方式。