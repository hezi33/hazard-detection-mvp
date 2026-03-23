#!/usr/bin/env python3
"""
Windows可视化测试脚本
直接在命令行显示可视化信息
"""

import os
import sys

def print_visualization_info():
    """打印可视化信息"""
    
    print("=" * 60)
    print("🔥 灭火器压力表检测算法可视化")
    print("=" * 60)
    
    print("\n🎨 可视化标注说明:")
    print("-" * 40)
    print("🔴 红色矩形框: YOLOv8检测到的灭火器位置")
    print("🔵 蓝色圆形: 霍夫变换检测到的压力表表盘")
    print("🟢 绿色直线: 霍夫变换检测到的指针方向")
    print("-" * 40)
    
    print("\n📁 相关文件:")
    print("-" * 40)
    files = [
        ("app_visual_demo.py", "完整可视化演示应用"),
        ("visual_annotator.py", "可视化标注器"),
        ("simple_visualization.py", "简单可视化文档"),
        ("detector.py", "核心检测算法"),
        ("detector_fixed.py", "修复版检测器"),
    ]
    
    for file, desc in files:
        if os.path.exists(file):
            print(f"✅ {file:25} - {desc}")
        else:
            print(f"❌ {file:25} - {desc} (未找到)")
    
    print("-" * 40)
    
    print("\n🚀 启动可视化演示:")
    print("-" * 40)
    print("1. 激活虚拟环境:")
    print("   venv\\Scripts\\activate")
    print("\n2. 运行可视化应用:")
    print("   python app_visual_demo.py --port 8002")
    print("\n3. 打开浏览器访问:")
    print("   http://localhost:8002")
    print("-" * 40)
    
    print("\n🔧 备选方案:")
    print("-" * 40)
    print("方案A: 运行修复版测试服务器")
    print("   python app.py --port 8001")
    print("   访问: http://localhost:8001")
    print("\n方案B: 直接测试API")
    print("   curl -X POST http://localhost:8001/api/check \\")
    print("     -F \"image=@test_images/fire_extinguisher.jpg\"")
    print("-" * 40)

def check_dependencies():
    """检查依赖"""
    print("\n📦 依赖检查:")
    print("-" * 40)
    
    try:
        import cv2
        print(f"✅ OpenCV: {cv2.__version__}")
    except ImportError:
        print("❌ OpenCV: 未安装")
    
    try:
        import fastapi
        print(f"✅ FastAPI: {fastapi.__version__}")
    except ImportError:
        print("❌ FastAPI: 未安装")
    
    try:
        import numpy
        print(f"✅ NumPy: {numpy.__version__}")
    except ImportError:
        print("❌ NumPy: 未安装")
    
    print("-" * 40)

def main():
    print_visualization_info()
    check_dependencies()
    
    print("\n" + "=" * 60)
    print("💡 提示:")
    print("1. 确保在项目根目录运行此脚本")
    print("2. 使用 'venv\\Scripts\\activate' 激活虚拟环境")
    print("3. 如果依赖缺失，运行 'pip install -r requirements.txt'")
    print("=" * 60)

if __name__ == "__main__":
    main()