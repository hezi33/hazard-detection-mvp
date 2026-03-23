@echo off
echo ========================================
echo  灭火器压力表检测 - 可视化演示
echo ========================================
echo.

REM 检查Python
python --version >nul 2>&1
if errorlevel 1 (
    echo [错误] Python未安装或不在PATH中
    echo 请安装Python 3.7+ 并添加到系统PATH
    pause
    exit /b 1
)

REM 进入项目目录
cd /d "%~dp0"
echo [信息] 当前目录: %CD%

REM 检查虚拟环境
if exist "venv\Scripts\activate" (
    echo [信息] 激活虚拟环境...
    call venv\Scripts\activate
) else (
    echo [警告] 虚拟环境不存在，使用系统Python
    echo 建议创建虚拟环境: python -m venv venv
)

REM 检查依赖
echo [信息] 检查Python依赖...
python -c "import fastapi, uvicorn, cv2, numpy, PIL" 2>nul
if errorlevel 1 (
    echo [信息] 缺少依赖，正在安装...
    
    REM 先升级pip
    python -m pip install --upgrade pip
    
    REM 安装核心依赖
    pip install fastapi uvicorn
    
    REM 尝试安装OpenCV
    pip install opencv-python
    
    REM 安装其他依赖
    pip install numpy pillow
    
    REM 如果有requirements.txt也安装
    if exist "requirements.txt" (
        echo [信息] 安装requirements.txt中的依赖...
        pip install -r requirements.txt
    )
) else (
    echo [信息] 所有依赖已安装
)

REM 停止可能冲突的进程
echo [信息] 检查端口占用...
for /f "tokens=5" %%a in ('netstat -ano ^| findstr ":800[0-9]"') do (
    echo [信息] 停止占用端口的进程PID: %%a
    taskkill /f /pid %%a 2>nul
)

REM 选择可用端口
set PORT=8002
:check_port
echo [信息] 检查端口 %PORT%...
netstat -ano | findstr ":%PORT%" >nul
if not errorlevel 1 (
    echo [警告] 端口 %PORT% 被占用，尝试下一个端口
    set /a PORT+=1
    if %PORT% gtr 8010 (
        echo [错误] 找不到可用端口 (8002-8010)
        pause
        exit /b 1
    )
    goto check_port
)

echo [成功] 使用端口: %PORT%

REM 启动服务器
echo ========================================
echo  启动可视化演示服务器...
echo  访问: http://localhost:%PORT%
echo  按 Ctrl+C 停止服务器
echo ========================================
echo.

python app_visual_demo.py --port %PORT%

REM 如果启动失败，显示错误
if errorlevel 1 (
    echo.
    echo [错误] 服务器启动失败
    echo 可能的原因:
    echo 1. Python代码有语法错误
    echo 2. 依赖安装不完整
    echo 3. 端口仍然被占用
    echo.
    echo 尝试手动启动查看详细错误:
    echo   python app_visual_demo.py --port %PORT%
)

pause