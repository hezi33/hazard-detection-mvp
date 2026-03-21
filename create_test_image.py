#!/usr/bin/env python3
"""
创建测试图片
"""

from PIL import Image, ImageDraw
import os

def create_fire_extinguisher_image(output_path="test_fire_extinguisher.jpg"):
    """创建一个简单的灭火器测试图片"""
    
    # 创建白色背景
    width, height = 600, 400
    image = Image.new('RGB', (width, height), color='white')
    draw = ImageDraw.Draw(image)
    
    # 画灭火器主体（红色矩形）
    body_x1, body_y1 = 150, 100
    body_x2, body_y2 = 450, 300
    draw.rectangle([body_x1, body_y1, body_x2, body_y2], 
                   outline='red', fill='lightgray', width=3)
    
    # 画压力表（圆形）
    gauge_center_x = 300
    gauge_center_y = 120
    gauge_radius = 40
    
    # 表盘
    draw.ellipse([gauge_center_x - gauge_radius, gauge_center_y - gauge_radius,
                  gauge_center_x + gauge_radius, gauge_center_y + gauge_radius],
                 outline='black', fill='white', width=2)
    
    # 画刻度
    for angle in range(0, 360, 30):
        rad = angle * 3.14159 / 180
        x1 = gauge_center_x + (gauge_radius - 5) * math.cos(rad)
        y1 = gauge_center_y + (gauge_radius - 5) * math.sin(rad)
        x2 = gauge_center_x + gauge_radius * math.cos(rad)
        y2 = gauge_center_y + gauge_radius * math.sin(rad)
        draw.line([x1, y1, x2, y2], fill='black', width=2)
    
    # 画指针（指向绿区 - 45度）
    pointer_angle = 45  # 绿区
    pointer_length = gauge_radius - 10
    rad = pointer_angle * 3.14159 / 180
    x_end = gauge_center_x + pointer_length * math.cos(rad)
    y_end = gauge_center_y + pointer_length * math.sin(rad)
    
    draw.line([gauge_center_x, gauge_center_y, x_end, y_end], 
              fill='black', width=3)
    
    # 画区域颜色指示
    # 绿区弧线
    draw.arc([gauge_center_x - 30, gauge_center_y - 30,
              gauge_center_x + 30, gauge_center_y + 30],
             0, 120, fill='green', width=5)
    
    # 添加文字
    draw.text((250, 350), "灭火器测试图片", fill='black')
    draw.text((260, 370), "指针在绿区（正常）", fill='green')
    
    # 保存图片
    image.save(output_path)
    print(f"✅ 创建测试图片: {output_path}")
    print(f"   尺寸: {width}x{height}")
    print(f"   指针角度: {pointer_angle}° (绿区)")
    
    return output_path

def create_red_zone_image(output_path="test_fire_extinguisher_red.jpg"):
    """创建红区测试图片"""
    
    width, height = 600, 400
    image = Image.new('RGB', (width, height), color='white')
    draw = ImageDraw.Draw(image)
    
    # 画灭火器主体
    body_x1, body_y1 = 150, 100
    body_x2, body_y2 = 450, 300
    draw.rectangle([body_x1, body_y1, body_x2, body_y2], 
                   outline='red', fill='lightgray', width=3)
    
    # 画压力表
    gauge_center_x = 300
    gauge_center_y = 120
    gauge_radius = 40
    
    draw.ellipse([gauge_center_x - gauge_radius, gauge_center_y - gauge_radius,
                  gauge_center_x + gauge_radius, gauge_center_y + gauge_radius],
                 outline='black', fill='white', width=2)
    
    # 画刻度
    for angle in range(0, 360, 30):
        rad = angle * 3.14159 / 180
        x1 = gauge_center_x + (gauge_radius - 5) * math.cos(rad)
        y1 = gauge_center_y + (gauge_radius - 5) * math.sin(rad)
        x2 = gauge_center_x + gauge_radius * math.cos(rad)
        y2 = gauge_center_y + gauge_radius * math.sin(rad)
        draw.line([x1, y1, x2, y2], fill='black', width=2)
    
    # 画指针（指向红区 - 270度）
    pointer_angle = 270  # 红区
    pointer_length = gauge_radius - 10
    rad = pointer_angle * 3.14159 / 180
    x_end = gauge_center_x + pointer_length * math.cos(rad)
    y_end = gauge_center_y + pointer_length * math.sin(rad)
    
    draw.line([gauge_center_x, gauge_center_y, x_end, y_end], 
              fill='black', width=3)
    
    # 画红区弧线
    draw.arc([gauge_center_x - 30, gauge_center_y - 30,
              gauge_center_x + 30, gauge_center_y + 30],
             240, 360, fill='red', width=5)
    
    # 添加文字
    draw.text((250, 350), "灭火器测试图片", fill='black')
    draw.text((260, 370), "指针在红区（隐患）", fill='red')
    
    # 保存图片
    image.save(output_path)
    print(f"✅ 创建测试图片: {output_path}")
    print(f"   指针角度: {pointer_angle}° (红区)")
    
    return output_path

if __name__ == "__main__":
    import math
    
    print("🎨 创建测试图片")
    print("=" * 40)
    
    # 创建测试图片目录
    os.makedirs("test_images", exist_ok=True)
    
    # 创建正常图片（绿区）
    normal_img = create_fire_extinguisher_image("test_images/fire_extinguisher_green.jpg")
    
    # 创建异常图片（红区）
    hazard_img = create_red_zone_image("test_images/fire_extinguisher_red.jpg")
    
    print("\n📁 测试图片已保存到 test_images/ 目录")
    print("   1. fire_extinguisher_green.jpg - 正常（绿区）")
    print("   2. fire_extinguisher_red.jpg   - 隐患（红区）")
    print("\n🚀 现在可以运行测试:")
    print("   python test_api.py")