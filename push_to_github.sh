#!/bin/bash

# 隐患检测MVP - GitHub推送脚本

set -e

echo "🚀 准备推送代码到GitHub"
echo "========================"

# 检查Git
if ! command -v git &> /dev/null; then
    echo "❌ Git未安装，请先安装Git"
    exit 1
fi

# 初始化Git仓库
echo "📦 初始化Git仓库..."
if [ ! -d ".git" ]; then
    git init
    echo "✅ Git仓库已初始化"
else
    echo "✅ Git仓库已存在"
fi

# 添加文件
echo "📁 添加文件到Git..."
git add .

# 检查是否有更改
if git diff --cached --quiet; then
    echo "⚠️ 没有更改需要提交"
else
    # 提交更改
    echo "💾 提交更改..."
    git commit -m "Initial commit: Hazard Detection MVP - Fire extinguisher pressure gauge detection
    
    Features:
    - Fire extinguisher detection using YOLOv8
    - Pressure gauge localization with Hough Circle Transform
    - Pointer angle detection with Hough Line Transform
    - Hazard judgment (green/yellow/red zones)
    - FastAPI RESTful API
    - Modern web upload interface
    - Docker support
    - Complete test suite
    - Documentation and setup guides"
    
    echo "✅ 更改已提交"
fi

# 显示远程仓库信息
echo ""
echo "🌐 远程仓库配置"
echo "================"

if git remote -v | grep -q "origin"; then
    echo "当前远程仓库:"
    git remote -v
else
    echo "⚠️ 未配置远程仓库"
    echo ""
    echo "请按以下步骤配置:"
    echo "1. 在GitHub创建仓库: https://github.com/new"
    echo "2. 仓库名: hazard-detection-mvp"
    echo "3. 不要初始化README/.gitignore/license"
    echo "4. 创建后复制仓库URL"
    echo ""
    echo "然后运行以下命令:"
    echo "  git remote add origin https://github.com/YOUR_USERNAME/hazard-detection-mvp.git"
    echo "  git branch -M main"
    echo "  git push -u origin main"
fi

echo ""
echo "📋 推送命令参考"
echo "================"
echo "1. 添加远程仓库:"
echo "   git remote add origin https://github.com/YOUR_USERNAME/hazard-detection-mvp.git"
echo ""
echo "2. 重命名分支:"
echo "   git branch -M main"
echo ""
echo "3. 推送到GitHub:"
echo "   git push -u origin main"
echo ""
echo "4. 如果推送被拒绝（仓库非空）:"
echo "   git pull origin main --allow-unrelated-histories"
echo "   git push -u origin main"
echo ""
echo "5. 或强制推送（谨慎使用）:"
echo "   git push -f origin main"

echo ""
echo "🔍 当前仓库状态"
echo "================"
echo "分支: $(git branch --show-current 2>/dev/null || echo '未设置')"
echo "提交: $(git log --oneline -1 2>/dev/null | cut -d' ' -f2- || echo '无提交')"
echo "文件数: $(git ls-files | wc -l)"

echo ""
echo "✅ 代码已准备好推送到GitHub！"
echo "请按照上面的步骤配置远程仓库并推送。"