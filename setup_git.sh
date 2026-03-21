#!/bin/bash

# Git配置脚本

echo "🔧 配置Git用户信息"
echo "=================="

# 设置Git用户信息（请修改为你的信息）
GIT_NAME="Your Name"
GIT_EMAIL="your.email@example.com"

# 配置Git
git config user.name "$GIT_NAME"
git config user.email "$GIT_EMAIL"

echo "✅ Git用户信息已设置:"
echo "   名称: $GIT_NAME"
echo "   邮箱: $GIT_EMAIL"

# 显示当前配置
echo ""
echo "📋 当前Git配置:"
echo "==============="
git config --list | grep -E "(user\.name|user\.email|remote\.origin)"

echo ""
echo "🚀 现在可以提交代码了:"
echo "====================="
echo "1. 添加文件: git add ."
echo "2. 提交更改: git commit -m 'Initial commit'"
echo "3. 添加远程仓库: git remote add origin <your-repo-url>"
echo "4. 推送代码: git push -u origin main"