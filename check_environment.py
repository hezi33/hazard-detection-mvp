#!/usr/bin/env python3
"""
检查当前环境并修复 PyTorch 2.6 YOLOv8 问题
"""

import sys
import subprocess
import importlib

def check_packages():
    """检查已安装的包"""
    packages = [
        'torch',
        'ultralytics',
        'fastapi',
        'uvicorn',
        'opencv-python',
        'numpy',
        'pillow'
    ]
    
    print("📦 检查包版本:")
    print("-" * 40)
    
    for pkg in packages:
        try:
            module = importlib.import_module(pkg.replace('-', '_'))
            if hasattr(module, '__version__'):
                print(f"✅ {pkg}: {module.__version__}")
            else:
                print(f"✅ {pkg}: 已安装 (版本未知)")
        except ImportError:
            print(f"❌ {pkg}: 未安装")
    
    print("-" * 40)

def check_pytorch_issue():
    """检查 PyTorch 2.6 问题"""
    try:
        import torch
        print(f"\n🔧 PyTorch 版本: {torch.__version__}")
        
        if torch.__version__.startswith('2.6'):
            print("⚠️  检测到 PyTorch 2.6，可能存在 weights_only 问题")
            print("   建议修复方法:")
            print("   1. 降级: pip install torch==2.5.1 torchvision==0.20.1")
            print("   2. 修改代码使用 safe_globals")
            print("   3. 使用 ultralytics.YOLO 而不是 torch.load")
            return True
        else:
            print("✅ PyTorch 版本正常")
            return False
    except ImportError:
        print("❌ PyTorch 未安装")
        return False

def check_yolo_model():
    """检查 YOLO 模型"""
    try:
        from ultralytics import YOLO
        print("\n🤖 测试 YOLOv8 加载...")
        
        # 尝试加载一个小模型
        try:
            model = YOLO('yolov8n.pt')
            print("✅ YOLOv8 模型可以正常加载")
            return True
        except Exception as e:
            print(f"❌ YOLOv8 加载失败: {e}")
            
            # 检查是否有本地模型文件
            import os
            model_files = [f for f in os.listdir('.') if f.endswith('.pt')]
            if model_files:
                print(f"📁 找到本地模型文件: {model_files}")
            else:
                print("📁 未找到本地 .pt 模型文件")
            
            return False
    except ImportError:
        print("❌ ultralytics 未安装")
        return False

def suggest_fix():
    """提供修复建议"""
    print("\n" + "="*60)
    print("🛠️  修复建议:")
    print("="*60)
    
    print("\n方案1: 降级 PyTorch (最简单)")
    print("pip install torch==2.5.1 torchvision==0.20.1")
    
    print("\n方案2: 修改模型加载代码")
    print("""在 detector.py 中修改:
import torch.serialization
from ultralytics.nn.tasks import DetectionModel

# 将原来的 torch.load() 改为:
with torch.serialization.safe_globals([DetectionModel]):
    model = torch.load('yolov8n.pt', weights_only=True)""")
    
    print("\n方案3: 使用 ultralytics.YOLO (推荐)")
    print("""from ultralytics import YOLO
model = YOLO('yolov8n.pt')  # 自动处理模型加载""")
    
    print("\n方案4: 临时禁用 weights_only (不推荐)")
    print("model = torch.load('yolov8n.pt', weights_only=False)")

def main():
    print("🔍 环境诊断工具")
    print("="*60)
    
    check_packages()
    has_issue = check_pytorch_issue()
    check_yolo_model()
    
    if has_issue:
        suggest_fix()
    
    print("\n" + "="*60)
    print("💡 快速修复命令:")
    print("pip install torch==2.5.1 torchvision==0.20.1 ultralytics")
    print("="*60)

if __name__ == "__main__":
    main()