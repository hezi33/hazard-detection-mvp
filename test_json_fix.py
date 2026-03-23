#!/usr/bin/env python3
"""
测试JSON序列化修复
"""

import numpy as np
import json

def convert_numpy_types(obj):
    """递归转换NumPy类型为Python原生类型"""
    if isinstance(obj, dict):
        return {key: convert_numpy_types(value) for key, value in obj.items()}
    elif isinstance(obj, list):
        return [convert_numpy_types(item) for item in obj]
    elif isinstance(obj, np.integer):
        return int(obj)
    elif isinstance(obj, np.floating):
        return float(obj)
    elif isinstance(obj, np.ndarray):
        return obj.tolist()
    else:
        return obj

# 模拟真实算法返回的数据结构（包含NumPy类型）
mock_detection_result = {
    "success": True,
    "hazard_detected": False,
    "confidence": np.float64(0.85),
    "hazard_name": "灭火器压力表正常",
    "reasoning": [
        "YOLOv8检测灭火器区域",
        "霍夫圆检测压力表",
        "霍夫直线检测指针",
        "角度分析判断区域"
    ],
    "evidence": {
        "fire_extinguisher_bbox": np.array([50, 50, 269, 155], dtype=np.int32),
        "gauge_center": np.array([159, 102], dtype=np.int32),
        "gauge_radius": np.int32(40),
        "pointer_angle": np.float64(150.5),
        "zone": "green",
        "gauge_detected": True
    },
    "mode": "real"
}

print("=== 转换前 ===")
print(f"类型检查:")
for key, value in mock_detection_result.items():
    if isinstance(value, dict):
        print(f"  {key}: dict")
        for k2, v2 in value.items():
            print(f"    {k2}: {type(v2)} - {v2}")
    else:
        print(f"  {key}: {type(value)} - {value}")

print("\n=== 尝试直接JSON序列化（应该失败）===")
try:
    json_str = json.dumps(mock_detection_result)
    print("✅ 直接序列化成功（不应该发生）")
except Exception as e:
    print(f"❌ 直接序列化失败: {e}")

print("\n=== 转换后 ===")
converted = convert_numpy_types(mock_detection_result)
print(f"类型检查:")
for key, value in converted.items():
    if isinstance(value, dict):
        print(f"  {key}: dict")
        for k2, v2 in value.items():
            print(f"    {k2}: {type(v2)} - {v2}")
    else:
        print(f"  {key}: {type(value)} - {value}")

print("\n=== 尝试JSON序列化转换后的数据 ===")
try:
    json_str = json.dumps(converted, ensure_ascii=False, indent=2)
    print("✅ 转换后序列化成功!")
    print(json_str[:500] + "...")
except Exception as e:
    print(f"❌ 转换后序列化失败: {e}")

print("\n=== 修复建议 ===")
print("1. 确保 convert_numpy_types 函数在 visual_real_server.py 中")
print("2. 确保在 detection_result = detector.detect(original_image) 后调用")
print("3. 调用方式: detection_result = convert_numpy_types(detection_result)")
print("4. 重启服务器测试")