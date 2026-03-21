#!/usr/bin/env python3
"""
测试脚本 - 用于验证API功能
"""

import requests
import os
import json
from pathlib import Path

BASE_URL = "http://localhost:8000"
TEST_IMAGES_DIR = "test_images"

def test_health():
    """测试健康检查"""
    print("🔍 测试健康检查...")
    try:
        response = requests.get(f"{BASE_URL}/health")
        if response.status_code == 200:
            print(f"✅ 健康检查通过: {response.json()}")
            return True
        else:
            print(f"❌ 健康检查失败: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ 连接失败: {e}")
        return False

def test_web_interface():
    """测试Web界面"""
    print("\n🌐 测试Web界面...")
    try:
        response = requests.get(BASE_URL)
        if response.status_code == 200:
            print("✅ Web界面可访问")
            return True
        else:
            print(f"❌ Web界面访问失败: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Web界面连接失败: {e}")
        return False

def test_api_with_image(image_path):
    """测试API接口"""
    print(f"\n📤 测试图片: {image_path}")
    
    if not os.path.exists(image_path):
        print(f"❌ 图片不存在: {image_path}")
        return False
    
    try:
        with open(image_path, 'rb') as f:
            files = {'file': f}
            response = requests.post(f"{BASE_URL}/api/check", files=files)
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ API调用成功")
            print(f"   状态: {'隐患 ❌' if result.get('hazard_detected') else '正常 ✅'}")
            print(f"   置信度: {result.get('confidence', 0):.2f}")
            print(f"   消息: {result.get('hazard_name', 'N/A')}")
            
            # 打印推理过程
            if 'reasoning' in result:
                print("   推理过程:")
                for step in result['reasoning']:
                    print(f"     - {step}")
            
            return result
        else:
            print(f"❌ API调用失败: {response.status_code}")
            print(f"   响应: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        return None

def find_test_images():
    """查找测试图片"""
    test_dir = Path(TEST_IMAGES_DIR)
    if not test_dir.exists():
        print(f"⚠️ 测试图片目录不存在: {TEST_IMAGES_DIR}")
        return []
    
    image_extensions = ['.jpg', '.jpeg', '.png', '.bmp', '.gif']
    images = []
    
    for ext in image_extensions:
        images.extend(list(test_dir.glob(f'*{ext}')))
        images.extend(list(test_dir.glob(f'*{ext.upper()}')))
    
    return sorted(images)

def run_all_tests():
    """运行所有测试"""
    print("=" * 60)
    print("🔥 隐患检测MVP - 测试套件")
    print("=" * 60)
    
    # 1. 测试健康检查
    if not test_health():
        print("\n⚠️ 服务可能未启动，请先运行: python app.py")
        return False
    
    # 2. 测试Web界面
    if not test_web_interface():
        print("\n⚠️ Web界面不可用")
        return False
    
    # 3. 查找测试图片
    test_images = find_test_images()
    
    if not test_images:
        print("\n⚠️ 未找到测试图片，请将图片放入 test_images/ 目录")
        print("   或使用以下命令测试:")
        print("   curl -X POST -F \"file=@your_image.jpg\" http://localhost:8000/api/check")
        return True
    
    print(f"\n📷 找到 {len(test_images)} 张测试图片")
    
    # 4. 测试每张图片
    results = []
    for img_path in test_images:
        result = test_api_with_image(img_path)
        if result:
            results.append({
                'image': img_path.name,
                'result': result
            })
    
    # 5. 汇总结果
    print("\n" + "=" * 60)
    print("📊 测试结果汇总")
    print("=" * 60)
    
    if results:
        total = len(results)
        hazards = sum(1 for r in results if r['result'].get('hazard_detected', False))
        successes = sum(1 for r in results if r['result'].get('success', False))
        
        print(f"总测试数: {total}")
        print(f"成功检测: {successes}")
        print(f"检测到隐患: {hazards}")
        print(f"检测正常: {total - hazards}")
        
        # 保存详细结果
        output_file = "test_results.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        print(f"\n📄 详细结果已保存到: {output_file}")
        
        return True
    else:
        print("❌ 所有测试都失败了")
        return False

def quick_test():
    """快速测试（使用模拟数据）"""
    print("\n⚡ 快速测试（模拟模式）")
    
    # 创建一个简单的测试图片
    test_image_path = "test_quick.jpg"
    
    # 如果没有测试图片，创建一个简单的
    if not os.path.exists(test_image_path):
        print("创建模拟测试图片...")
        from PIL import Image, ImageDraw
        img = Image.new('RGB', (400, 300), color='white')
        draw = ImageDraw.Draw(img)
        
        # 画一个简单的灭火器
        draw.rectangle([100, 100, 300, 250], outline='red', width=3)
        draw.ellipse([180, 80, 220, 120], outline='blue', width=2)
        
        img.save(test_image_path)
        print(f"✅ 创建模拟图片: {test_image_path}")
    
    # 测试API
    result = test_api_with_image(test_image_path)
    
    if result:
        print("\n✅ 快速测试完成！")
        print("   服务基本功能正常，可以开始真实图片测试")
        return True
    else:
        print("\n❌ 快速测试失败")
        return False

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "quick":
        quick_test()
    else:
        run_all_tests()