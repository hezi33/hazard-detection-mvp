# GitHub仓库设置指南

## 步骤1：在GitHub创建仓库

1. 登录GitHub
2. 点击右上角 "+" → "New repository"
3. 填写仓库信息：
   - **Repository name**: `hazard-detection-mvp`
   - **Description**: `Fire extinguisher pressure gauge detection system - MVP验证版本`
   - **Public** (或 Private，根据你的需求)
   - 不要初始化README、.gitignore或license
4. 点击 "Create repository"

## 步骤2：获取仓库URL

创建成功后，你会看到类似这样的URL：
```
https://github.com/your-username/hazard-detection-mvp.git
```

## 步骤3：推送代码到GitHub

在你的本地终端执行：

```bash
# 1. 进入项目目录
cd /path/to/hazard-detection-mvp

# 2. 初始化Git仓库（如果还没初始化）
git init

# 3. 添加所有文件
git add .

# 4. 提交更改
git commit -m "Initial commit: Hazard Detection MVP - Fire extinguisher pressure gauge detection"

# 5. 添加远程仓库
git remote add origin https://github.com/your-username/hazard-detection-mvp.git

# 6. 推送代码
git branch -M main
git push -u origin main
```

## 步骤4：验证推送成功

访问你的GitHub仓库页面：
```
https://github.com/your-username/hazard-detection-mvp
```

应该能看到所有文件：
- `app.py`
- `detector.py`
- `requirements.txt`
- `Dockerfile`
- `docker-compose.yml`
- `README.md`
- 等等

## 步骤5：其他人克隆使用

```bash
# 克隆仓库
git clone https://github.com/your-username/hazard-detection-mvp.git
cd hazard-detection-mvp

# 安装依赖
pip install -r requirements.txt

# 启动服务
python app.py
```

## Git配置建议

### 1. 创建 .gitignore 文件
```bash
# 创建 .gitignore
cat > .gitignore << EOF
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# Virtual Environment
venv/
env/
ENV/

# IDE
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db

# Logs
*.log
logs/

# Uploads
uploads/*
!uploads/.gitkeep

# Test images (可以保留，但大文件建议用Git LFS)
# test_images/*.jpg
# test_images/*.png
EOF
```

### 2. 使用Git LFS管理大文件（可选）
如果需要管理大的测试图片：
```bash
# 安装Git LFS
git lfs install

# 跟踪大文件
git lfs track "*.jpg"
git lfs track "*.png"
git lfs track "*.pt"  # YOLO模型文件

git add .gitattributes
git commit -m "Add Git LFS tracking"
```

## 仓库维护

### 更新代码
```bash
# 拉取最新代码
git pull origin main

# 提交更改
git add .
git commit -m "Update: 描述更改内容"
git push origin main
```

### 创建分支开发新功能
```bash
# 创建新分支
git checkout -b feature/improve-detection

# 开发完成后合并
git checkout main
git merge feature/improve-detection
git push origin main
```

## 问题解决

### 问题：推送被拒绝
```bash
# 如果仓库已有内容，需要先拉取
git pull origin main --allow-unrelated-histories

# 或强制推送（谨慎使用）
git push -f origin main
```

### 问题：大文件推送失败
```bash
# 使用Git LFS
git lfs install
git lfs track "*.pt"
git add .gitattributes
git add yolov8n.pt
git commit -m "Add YOLO model via Git LFS"
git push origin main
```

### 问题：依赖安装慢
在README中建议使用国内镜像：
```bash
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
```

## 仓库URL格式

根据你的认证方式，可以使用不同的URL：

### HTTPS（推荐，最简单）
```
https://github.com/your-username/hazard-detection-mvp.git
```

### SSH（需要配置SSH密钥）
```
git@github.com:your-username/hazard-detection-mvp.git
```

### GitHub CLI
```
gh repo clone your-username/hazard-detection-mvp
```

## 完成验证

完成以上步骤后，你应该能够：

1. ✅ 访问GitHub仓库页面
2. ✅ 看到所有代码文件
3. ✅ 使用 `git clone` 克隆仓库
4. ✅ 使用 `pip install` 安装依赖
5. ✅ 使用 `python app.py` 启动服务
6. ✅ 访问 http://localhost:8000 测试功能

现在你可以将仓库URL分享给团队成员，开始测试和开发！