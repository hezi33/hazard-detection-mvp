#!/usr/bin/env python3
"""
可视化标注器 - 在图片上绘制检测结果
"""

import cv2
import numpy as np
import json
import base64
from io import BytesIO
from PIL import Image
import matplotlib.pyplot as plt

class VisualAnnotator:
    def __init__(self):
        """初始化标注器"""
        self.colors = {
            'fire_extinguisher': (0, 0, 255),      # 红色 - 灭火器框
            'gauge_circle': (255, 0, 0),          # 蓝色 - 压力表圆
            'pointer_line': (0, 255, 0),          # 绿色 - 指针线
            'green_zone': (0, 255, 0, 100),       # 绿色区域 (半透明)
            'yellow_zone': (255, 255, 0, 100),    # 黄色区域
            'red_zone': (255, 0, 0, 100),         # 红色区域
            'text': (255, 255, 255)               # 白色文字
        }
    
    def draw_fire_extinguisher(self, image, bbox, confidence):
        """绘制灭火器边界框"""
        x1, y1, x2, y2 = bbox
        color = self.colors['fire_extinguisher']
        
        # 绘制矩形框
        cv2.rectangle(image, (x1, y1), (x2, y2), color, 2)
        
        # 绘制标签
        label = f"Fire Extinguisher: {confidence:.2f}"
        label_size, baseline = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 2)
        cv2.rectangle(image, (x1, y1 - label_size[1] - 10), 
                     (x1 + label_size[0], y1), color, -1)
        cv2.putText(image, label, (x1, y1 - 5), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)
        
        return image
    
    def draw_gauge_circle(self, image, center, radius, detected=True):
        """绘制压力表圆形"""
        cx, cy = center
        color = self.colors['gauge_circle']
        
        # 绘制圆形
        cv2.circle(image, (cx, cy), radius, color, 2)
        
        # 绘制圆心
        cv2.circle(image, (cx, cy), 3, color, -1)
        
        # 绘制标签
        label = "Gauge" if detected else "Estimated Gauge"
        cv2.putText(image, label, (cx - 30, cy - radius - 10), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)
        
        return image
    
    def draw_pointer_line(self, image, gauge_center, pointer_angle, length=50):
        """绘制指针线"""
        cx, cy = gauge_center
        color = self.colors['pointer_line']
        
        # 计算指针端点
        angle_rad = np.radians(pointer_angle)
        end_x = int(cx + length * np.cos(angle_rad))
        end_y = int(cy + length * np.sin(angle_rad))
        
        # 绘制指针线
        cv2.line(image, (cx, cy), (end_x, end_y), color, 3)
        
        # 绘制指针箭头
        cv2.circle(image, (end_x, end_y), 5, color, -1)
        
        # 绘制角度标签
        angle_label = f"Angle: {pointer_angle:.1f}°"
        cv2.putText(image, angle_label, (cx + 10, cy - 10), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)
        
        return image
    
    def draw_zones(self, image, gauge_center, radius):
        """绘制区域扇形"""
        cx, cy = gauge_center
        
        # 创建透明图层
        overlay = image.copy()
        
        # 绘制绿色区域 (0-120°)
        self.draw_sector(overlay, (cx, cy), radius, 0, 120, self.colors['green_zone'])
        
        # 绘制黄色区域 (120-240°)
        self.draw_sector(overlay, (cx, cy), radius, 120, 240, self.colors['yellow_zone'])
        
        # 绘制红色区域 (240-360°)
        self.draw_sector(overlay, (cx, cy), radius, 240, 360, self.colors['red_zone'])
        
        # 合并图层
        cv2.addWeighted(overlay, 0.3, image, 0.7, 0, image)
        
        # 绘制区域标签
        self.draw_zone_labels(image, (cx, cy), radius)
        
        return image
    
    def draw_sector(self, image, center, radius, start_angle, end_angle, color):
        """绘制扇形区域"""
        cx, cy = center
        
        # 创建多边形点
        points = [(cx, cy)]
        for angle in np.arange(start_angle, end_angle, 1):
            rad = np.radians(angle)
            x = int(cx + radius * np.cos(rad))
            y = int(cy + radius * np.sin(rad))
            points.append((x, y))
        
        # 闭合多边形
        points.append((cx, cy))
        
        # 绘制填充扇形
        pts = np.array(points, np.int32)
        cv2.fillPoly(image, [pts], color[:3])
        
        # 绘制扇形边界
        for angle in [start_angle, end_angle]:
            rad = np.radians(angle)
            x = int(cx + radius * np.cos(rad))
            y = int(cy + radius * np.sin(rad))
            cv2.line(image, (cx, cy), (x, y), (255, 255, 255), 1)
    
    def draw_zone_labels(self, image, center, radius):
        """绘制区域标签"""
        cx, cy = center
        font = cv2.FONT_HERSHEY_SIMPLEX
        
        # 绿色区域标签
        green_angle = 60  # 中间角度
        green_rad = np.radians(green_angle)
        green_x = int(cx + (radius + 20) * np.cos(green_rad))
        green_y = int(cy + (radius + 20) * np.sin(green_rad))
        cv2.putText(image, "GREEN", (green_x - 30, green_y), font, 0.5, (0, 255, 0), 2)
        
        # 黄色区域标签
        yellow_angle = 180
        yellow_rad = np.radians(yellow_angle)
        yellow_x = int(cx + (radius + 20) * np.cos(yellow_rad))
        yellow_y = int(cy + (radius + 20) * np.sin(yellow_rad))
        cv2.putText(image, "YELLOW", (yellow_x - 30, yellow_y), font, 0.5, (255, 255, 0), 2)
        
        # 红色区域标签
        red_angle = 300
        red_rad = np.radians(red_angle)
        red_x = int(cx + (radius + 20) * np.cos(red_rad))
        red_y = int(cy + (radius + 20) * np.sin(red_rad))
        cv2.putText(image, "RED", (red_x - 15, red_y), font, 0.5, (255, 0, 0), 2)
    
    def draw_status_info(self, image, result, position=(20, 30)):
        """绘制状态信息"""
        x, y = position
        font = cv2.FONT_HERSHEY_SIMPLEX
        
        # 状态标题
        status = "NORMAL" if not result.get('hazard_detected', False) else "HAZARD"
        color = (0, 255, 0) if status == "NORMAL" else (255, 0, 0)
        cv2.putText(image, f"STATUS: {status}", (x, y), font, 0.7, color, 2)
        
        # 置信度
        confidence = result.get('confidence', 0)
        cv2.putText(image, f"Confidence: {confidence:.2f}", (x, y + 30), font, 0.5, (255, 255, 255), 2)
        
        # 隐患名称
        hazard_name = result.get('hazard_name', '')
        cv2.putText(image, f"Hazard: {hazard_name}", (x, y + 60), font, 0.5, (255, 255, 255), 2)
        
        # 检测模式
        mode = result.get('mode', 'unknown')
        cv2.putText(image, f"Mode: {mode}", (x, y + 90), font, 0.5, (255, 255, 255), 2)
        
        return image
    
    def annotate_image(self, image, detection_result):
        """主标注函数"""
        # 创建副本
        annotated = image.copy()
        
        # 提取检测结果
        evidence = detection_result.get('evidence', {})
        
        # 1. 绘制灭火器边界框
        if 'fire_extinguisher_bbox' in evidence:
            bbox = evidence['fire_extinguisher_bbox']
            confidence = detection_result.get('confidence', 0.5)
            annotated = self.draw_fire_extinguisher(annotated, bbox, confidence)
        
        # 2. 绘制压力表圆形
        if 'gauge_center' in evidence and 'gauge_radius' in evidence:
            center = evidence['gauge_center']
            radius = evidence['gauge_radius']
            detected = evidence.get('gauge_detected', True)
            annotated = self.draw_gauge_circle(annotated, center, radius, detected)
        
        # 3. 绘制指针线
        if 'pointer_angle' in evidence and 'gauge_center' in evidence:
            angle = evidence['pointer_angle']
            center = evidence['gauge_center']
            radius = evidence.get('gauge_radius', 50)
            annotated = self.draw_pointer_line(annotated, center, angle, radius * 0.8)
        
        # 4. 绘制区域扇形
        if 'gauge_center' in evidence and 'gauge_radius' in evidence:
            center = evidence['gauge_center']
            radius = evidence['gauge_radius']
            annotated = self.draw_zones(annotated, center, radius)
        
        # 5. 绘制状态信息
        annotated = self.draw_status_info(annotated, detection_result)
        
        # 6. 绘制推理过程
        reasoning = detection_result.get('reasoning', [])
        self.draw_reasoning(annotated, reasoning, (image.shape[1] - 300, 30))
        
        return annotated
    
    def draw_reasoning(self, image, reasoning_list, position):
        """绘制推理过程"""
        x, y = position
        font = cv2.FONT_HERSHEY_SIMPLEX
        
        cv2.putText(image, "Reasoning:", (x, y), font, 0.6, (255, 255, 255), 2)
        
        for i, reason in enumerate(reasoning_list[:5]):  # 最多显示5条
            text_y = y + 25 + i * 25
            if text_y > image.shape[0] - 50:  # 不超过图像底部
                break
            
            # 简化文本
            short_reason = reason[:40] + "..." if len(reason) > 40 else reason
            cv2.putText(image, f"• {short_reason}", (x, text_y), font, 0.4, (200, 200, 200), 1)
    
    def image_to_base64(self, image):
        """将图像转换为base64字符串"""
        # 将BGR转换为RGB
        rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        
        # 转换为PIL图像
        pil_image = Image.fromarray(rgb_image)
        
        # 保存到字节流
        buffered = BytesIO()
        pil_image.save(buffered, format="JPEG", quality=85)
        
        # 转换为base64
        img_str = base64.b64encode(buffered.getvalue()).decode()
        
        return f"data:image/jpeg;base64,{img_str}"
    
    def create_visualization_report(self, original_image, annotated_image, detection_result):
        """创建可视化报告"""
        # 调整图像大小以便并排显示
        height = max(original_image.shape[0], annotated_image.shape[0])
        width = original_image.shape[1] + annotated_image.shape[1]
        
        report_image = np.zeros((height, width, 3), dtype=np.uint8)
        
        # 放置原始图像
        report_image[0:original_image.shape[0], 0:original_image.shape[1]] = original_image
        
        # 放置标注图像
        report_image[0:annotated_image.shape[0], original_image.shape[1]:] = annotated_image
        
        # 添加标题
        cv2.putText(report_image, "Original Image", (10, 30), 
                   cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
        cv2.putText(report_image, "Annotated Result", (original_image.shape[1] + 10, 30), 
                   cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
        
        # 添加分隔线
        cv2.line(report_image, (original_image.shape[1], 0), 
                (original_image.shape[1], height), (255, 255, 255), 2)
        
        return report_image

def test_visual_annotator():
    """测试可视化标注器"""
    print("测试可视化标注器...")
    
    # 创建测试图像
    test_image = np.zeros((400, 600, 3), dtype=np.uint8)
    test_image[:] = (50, 50, 50)  # 灰色背景
    
    # 模拟检测结果
    test_result = {
        "success": True,
        "hazard_detected": False,
        "confidence": 0.85,
        "hazard_name": "灭火器压力表正常",
        "reasoning": [
            "检测到灭火器 (置信度: 0.95)",
            "定位压力表区域 (半径: 45px)",
            "检测到指针 (角度: 45.0°)",
            "指针位于绿区"
        ],
        "evidence": {
            "fire_extinguisher_bbox": [100, 100, 400, 350],
            "gauge_center": [250, 200],
            "gauge_radius": 45,
            "pointer_angle": 45.0,
            "zone": "green",
            "gauge_detected": True
        },
        "mode": "simulation"
    }
    
    # 创建标注器
    annotator = VisualAnnotator()
    
    # 标注图像
    annotated = annotator.annotate_image(test_image, test_result)
    
    # 创建报告
    report = annotator.create_visualization_report(test_image, annotated, test_result)
    
    # 保存结果
    cv2.imwrite("test_visualization.jpg", report)
    print("✅ 测试完成，结果保存为 test_visualization.jpg")
    
    # 转换为base64
    base64_str = annotator.image_to_base64(annotated)
    print(f"Base64长度: {len(base64_str)} 字符")
    
    return annotator

if __name__ == "__main__":
    test_visual_annotator()