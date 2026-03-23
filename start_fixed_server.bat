@echo off
chcp 65001 >nul
echo 🔧 启动修复版真实算法服务器

REM 检查Python环境
python --version
if errorlevel 1 (
    echo ❌ Python未找到
    pause
    exit /b 1
)

REM 激活虚拟环境
call venv\Scripts\activate.bat
if errorlevel 1 (
    echo ❌ 虚拟环境激活失败
    pause
    exit /b 1
)

REM 检查PyTorch版本
echo 📊 检查PyTorch版本...
python -c "import torch; print(f'PyTorch版本: {torch.__version__}')"

REM 尝试不同端口
set PORT=8013
echo 🔍 尝试端口: %PORT%

:try_port
python visual_real_server.py --port %PORT%
if errorlevel 1 (
    echo ⚠️ 端口 %PORT% 被占用，尝试下一个端口
    set /a PORT+=1
    if %PORT% gtr 8020 (
        echo ❌ 所有端口都被占用，请检查运行中的进程
        pause
        exit /b 1
    )
    goto try_port
)

pause