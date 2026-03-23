#!/bin/bash

# 隐患识别平台启动脚本

echo "🚀 启动隐患识别平台..."

# 检查Node.js版本
NODE_VERSION=$(node --version)
echo "Node.js版本: $NODE_VERSION"

# 安装依赖
echo "📦 安装依赖..."
npm install

# 启动Mock API服务器（后台运行）
echo "🔧 启动Mock API服务器..."
npm run mock-api &
MOCK_PID=$!
echo "Mock API服务器PID: $MOCK_PID"

# 等待Mock API服务器启动
echo "⏳ 等待Mock API服务器启动..."
sleep 3

# 启动主服务器
echo "🌐 启动主服务器..."
npm start &
MAIN_PID=$!
echo "主服务器PID: $MAIN_PID"

# 等待主服务器启动
echo "⏳ 等待主服务器启动..."
sleep 5

# 显示服务器状态
echo ""
echo "✅ 服务器启动完成！"
echo ""
echo "📡 服务器地址:"
echo "  主服务器: http://localhost:3000"
echo "  Mock API: http://localhost:3001"
echo ""
echo "🌐 Web界面: http://localhost:3000/web/index.html"
echo ""
echo "🔧 可用端点:"
echo "  GET  /health          - 健康检查"
echo "  POST /detect          - 单图隐患检测"
echo "  POST /batch-test      - 批量测试"
echo "  GET  /hazard-types    - 获取隐患类型"
echo ""
echo "🛠️  调试工具:"
echo "  node debug/debug-single.js <image_url> [points]"
echo "  node debug/debug-single.js --batch <test_file>"
echo ""
echo "🧪 测试工具:"
echo "  node test/test-runner.js data/minimal-dataset.json"
echo ""
echo "📝 按 Ctrl+C 停止所有服务器"

# 捕获Ctrl+C信号
trap 'echo ""; echo "🛑 停止服务器..."; kill $MAIN_PID $MOCK_PID; exit 0' INT

# 保持脚本运行
wait