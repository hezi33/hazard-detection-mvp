#!/usr/bin/env python3
"""
修复可视化演示问题
"""

import os
import sys

def check_dependencies():
    """检查依赖"""
    print("检查依赖...")
    
    missing = []
    
    try:
        import fastapi
        print(f"✅ FastAPI: {fastapi.__version__}")
    except ImportError:
        print("❌ FastAPI: 未安装")
        missing.append("fastapi")
    
    try:
        import uvicorn
        print(f"✅ Uvicorn: {uvicorn.__version__}")
    except ImportError:
        print("❌ Uvicorn: 未安装")
        missing.append("uvicorn")
    
    try:
        import cv2
        print(f"✅ OpenCV: {cv2.__version__}")
    except ImportError:
        print("❌ OpenCV: 未安装")
        missing.append("opencv-python")
    
    try:
        import numpy
        print(f"✅ NumPy: {numpy.__version__}")
    except ImportError:
        print("❌ NumPy: 未安装")
        missing.append("numpy")
    
    return missing

def create_windows_batch():
    """创建Windows批处理文件"""
    batch_content = """@echo off
echo 灭火器压力表检测 - 可视化演示
echo.

REM 检查Python
python --version >nul 2>&1
if errorlevel 1 (
    echo 错误: Python未安装或不在PATH中
    pause
    exit /b 1
)

REM 激活虚拟环境
if exist "venv\\Scripts\\activate" (
    call venv\\Scripts\\activate
    echo 虚拟环境已激活
) else (
    echo 警告: 虚拟环境不存在，使用系统Python
)

REM 检查依赖
echo 检查依赖...
pip install fastapi uvicorn opencv-python numpy pillow >nul 2>&1
if errorlevel 1 (
    echo 依赖安装失败，尝试使用requirements.txt
    if exist requirements.txt (
        pip install -r requirements.txt
    )
)

REM 停止可能冲突的服务
echo 停止可能冲突的服务...
taskkill /f /im python.exe 2>nul

REM 启动服务
echo 启动可视化演示服务...
echo 访问: http://localhost:8002
echo 按 Ctrl+C 停止服务
echo.

python app_visual_demo.py --port 8002

pause
"""
    
    with open("start_visual.bat", "w", encoding="gbk") as f:
        f.write(batch_content)
    
    print("✅ 已创建 start_visual.bat")

def create_simple_server():
    """创建简化版本的可视化服务器"""
    simple_code = """#!/usr/bin/env python3
"""
    
    # 这里可以创建一个简化版本，但先不实现
    pass

def main():
    print("=" * 60)
    print("🔥 灭火器压力表检测 - 可视化演示修复工具")
    print("=" * 60)
    
    # 检查当前目录
    if not os.path.exists("app_visual_demo.py"):
        print("❌ 错误: 请在项目根目录运行此脚本")
        print("   当前目录:", os.getcwd())
        return
    
    # 检查依赖
    missing = check_dependencies()
    
    if missing:
        print(f"\n⚠️  缺少 {len(missing)} 个依赖:")
        print("   pip install " + " ".join(missing))
    
    # 创建Windows批处理文件
    create_windows_batch()
    
    print("\n" + "=" * 60)
    print("🎯 操作步骤:")
    print("1. 双击运行 start_visual.bat")
    print("2. 等待服务启动完成")
    print("3. 打开浏览器访问: http://localhost:8002")
    print("4. 上传图片测试可视化功能")
    print("=" * 60)
    
    print("\n💡 如果仍有问题:")
    print("1. 确保端口8002未被占用")
    print("2. 检查防火墙设置")
    print("3. 尝试其他端口: python app_visual_demo.py --port 8003")
    print("=" * 60)

if __name__ == "__main__":
    main()