@echo off
cd /d "D:\Documents\git_Projects\hazard-detection-mvp"
echo ========================================
echo 🚀 启动隐患检测服务 (端口: 8001)
echo ========================================
echo.
echo 📡 访问: http://localhost:8001
echo 🔧 API: http://localhost:8001/api/check
echo 💚 健康: http://localhost:8001/health
echo.
echo 按 Ctrl+C 停止
echo ========================================
echo.
python app.py --port 8001
pause