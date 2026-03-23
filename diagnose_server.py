#!/usr/bin/env python3
"""
诊断服务器问题
"""

import sys
import os

print("🔍 诊断服务器问题")
print("=" * 50)

# 1. 检查Python版本
print("1. Python版本:")
print(f"   {sys.version}")

# 2. 检查PyTorch
try:
    import torch
    print(f"2. PyTorch版本: {torch.__version__}")
except ImportError:
    print("2. PyTorch: 未安装")

# 3. 检查ultralytics
try:
    import ultralytics
    print(f"3. ultralytics版本: {ultralytics.__version__}")
except ImportError:
    print("3. ultralytics: 未安装")

# 4. 检查OpenCV
try:
    import cv2
    print(f"4. OpenCV版本: {cv2.__version__}")
except ImportError:
    print("4. OpenCV: 未安装")

# 5. 检查FastAPI
try:
    import fastapi
    print(f"5. FastAPI版本: {fastapi.__version__}")
except ImportError:
    print("5. FastAPI: 未安装")

# 6. 测试detector_fixed
print("\n6. 测试detector_fixed导入:")
try:
    from detector_fixed import FireExtinguisherDetector
    print("   ✅ detector_fixed导入成功")
    
    # 测试初始化
    print("   测试初始化...")
    detector = FireExtinguisherDetector(use_simulation=False)
    print(f"   使用模拟模式: {detector.use_simulation}")
    print(f"   模型: {detector.model}")
    
except ImportError as e:
    print(f"   ❌ detector_fixed导入失败: {e}")
except Exception as e:
    print(f"   ❌ 初始化失败: {e}")
    import traceback
    traceback.print_exc()

# 7. 检查文件
print("\n7. 检查关键文件:")
files_to_check = [
    "detector_fixed.py",
    "visual_real_server.py", 
    "templates/visual_simple.html",
    "yolov8n.pt"
]

for file in files_to_check:
    if os.path.exists(file):
        size = os.path.getsize(file)
        print(f"   ✅ {file}: 存在 ({size} bytes)")
    else:
        print(f"   ❌ {file}: 不存在")

# 8. 端口检查
print("\n8. 端口检查建议:")
print("   当前服务器可能在8013端口")
print("   前端页面调用8010端口")
print("   解决方案:")
print("   A. 修改服务器使用8010: python visual_real_server.py --port 8010")
print("   B. 修改前端页面端口: 编辑 templates/visual_simple.html")

print("\n" + "=" * 50)
print("📋 建议操作:")
print("1. 确保服务器在8010端口运行")
print("2. 查看服务器错误日志（上传图片时的详细错误）")
print("3. 发送错误日志给我分析")