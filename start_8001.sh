#!/bin/bash
# 专用8001端口启动脚本

echo "========================================"
echo "🚀 启动隐患检测MVP服务 (端口: 8001)"
echo "========================================"
echo ""
echo "📡 访问地址: http://localhost:8001"
echo "🔧 API端点: http://localhost:8001/api/check"
echo "💚 健康检查: http://localhost:8001/health"
echo ""
echo "⚠️  注意:"
echo "   • PyTorch警告信息可忽略，不影响功能"
echo "   • 8000端口可能被占用，使用8001端口"
echo "   • 按 Ctrl+C 停止服务"
echo ""
echo "========================================"

python app.py --port 8001