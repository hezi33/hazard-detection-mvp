"""
PyTorch 2.6 YOLOv8 模型加载修复方案

问题: PyTorch 2.6 将 torch.load() 的 weights_only 参数默认值从 False 改为 True
错误: WeightsUnpickler error: Unsupported global: GLOBAL ultralytics.nn.tasks.DetectionModel

解决方案:
1. 使用 safe_globals 上下文管理器
2. 或者降级 PyTorch 到 2.5
"""

import torch
import torch.serialization

def fix_model_loading():
    """修复 YOLOv8 模型加载的示例代码"""
    
    # 方法1: 使用 safe_globals（推荐）
    try:
        import ultralytics
        from ultralytics.nn.tasks import DetectionModel
        
        model_path = "yolov8n.pt"  # 你的模型路径
        
        # 使用 safe_globals 允许 DetectionModel
        with torch.serialization.safe_globals([DetectionModel]):
            model = torch.load(model_path, weights_only=True)
            print("✅ 模型加载成功 (使用 safe_globals)")
            return model
    except Exception as e:
        print(f"方法1失败: {e}")
    
    # 方法2: 使用 weights_only=False（不推荐，仅用于测试）
    try:
        model = torch.load(model_path, weights_only=False)
        print("⚠️ 模型加载成功 (使用 weights_only=False，有安全风险)")
        return model
    except Exception as e:
        print(f"方法2失败: {e}")
    
    # 方法3: 使用 ultralytics 的 YOLO 类（最佳实践）
    try:
        from ultralytics import YOLO
        model = YOLO(model_path)
        print("✅ 模型加载成功 (使用 ultralytics.YOLO)")
        return model
    except Exception as e:
        print(f"方法3失败: {e}")
    
    return None

# 如果你的 detector.py 或类似文件中有模型加载代码，可以这样修复
def create_patch_for_detector():
    """为 detector.py 创建修复补丁"""
    
    patch_code = '''
# ====== 修复 PyTorch 2.6 模型加载问题 ======
# 在文件顶部添加导入
import torch.serialization
from ultralytics.nn.tasks import DetectionModel

# 找到模型加载代码（通常是 torch.load 调用）
# 将原来的:
# model = torch.load(model_path)
# 或
# model = torch.load(model_path, weights_only=True)

# 改为:
with torch.serialization.safe_globals([DetectionModel]):
    model = torch.load(model_path, weights_only=True)

# 或者使用 ultralytics.YOLO（推荐）:
# from ultralytics import YOLO
# model = YOLO(model_path)
'''
    
    return patch_code

if __name__ == "__main__":
    print("PyTorch 版本:", torch.__version__)
    print("修复方案已生成")
    
    # 生成修复指南
    print("\n" + "="*60)
    print("修复步骤:")
    print("1. 找到你的 detector.py 或模型加载代码")
    print("2. 添加导入: import torch.serialization")
    print("3. 添加导入: from ultralytics.nn.tasks import DetectionModel")
    print("4. 将 torch.load() 调用包装在 safe_globals 中")
    print("="*60)
    
    # 显示补丁示例
    print("\n补丁示例:")
    print(create_patch_for_detector())