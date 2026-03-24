#!/usr/bin/env python3
"""
优化版灭火器压力表检测器
添加红绿黄区域检测和智能指针判断
"""

import cv2
import numpy as np
import logging
import math
from pathlib import Path

logger = logging.getLogger(__name__)

class FireExtinguisherDetectorOptimized:
    def __init__(self, use_simulation=True, use_color_detection=True):
        """初始化优化版检测器"""
        self.model = None
        self.use_simulation = use_simulation
        self.use_color_detection = use_color_detection
        
        # 颜色范围定义 (HSV格式)
        self.color_ranges = {
            'red': [
                (np.array([0, 100, 100]), np.array([10, 255, 255])),
                (np.array([160, 100, 100]), np.array([180, 255, 255]))
            ],
            'green': [
                (np.array([40, 50, 50]), np.array([90, 255, 255]))
            ],
            'yellow': [
                (np.array([15, 50, 50]), np.array([35, 255, 255]))
            ],
            'pointer': [  # 指针颜色（红色或黑色）
                (np.array([0, 50, 50]), np.array([10, 255, 255])),
                (np.array([160, 50, 50]), np.array([180, 255, 255])),
                (np.array([0, 0, 0]), np.array([180, 100, 100]))
            ]
        }
        
        # 区域角度定义
        self.zone_angles = {
            'green': (0, 120),
            'yellow': (120, 240),
            'red': (240, 360)
        }
        
        if not use_simulation:
            self.initialize_model()
        else:
            logger.info("使用模拟模式（跳过YOLO模型加载）")
    
    def initialize_model(self):
        """初始化YOLO模型"""
        try:
            from ultralytics import YOLO
            
            cache_dir = Path.home() / ".cache" / "ultralytics" / "hub"
            model_path = cache_dir / "yolov8n.pt"
            
            if model_path.exists():
                logger.info(f"使用本地模型: {model_path}")
                self.model = YOLO(str(model_path))
            else:
                logger.info("下载YOLOv8模型...")
                self.model = YOLO('yolov8n.pt')
            
            logger.info("YOLO模型加载成功")
            
        except ImportError:
            logger.warning("ultralytics未安装，使用模拟模式")
            self.use_simulation = True
        except Exception as e:
            logger.error(f"模型加载失败: {e}")
            self.use_simulation = True
    
    def detect_fire_extinguisher(self, image):
        """检测灭火器"""
        if self.use_simulation or self.model is None:
            height, width = image.shape[:2]
            return [{
                'bbox': [width//4, height//4, width*3//4, height*3//4],
                'confidence': 0.85,
                'label': 'fire_extinguisher',
                'simulated': True
            }]
        
        try:
            results = self.model(image)
            detections = []
            
            for result in results:
                boxes = result.boxes
                if boxes is not None:
                    for box in boxes:
                        x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
                        conf = box.conf[0].cpu().numpy()
                        cls = int(box.cls[0].cpu().numpy())
                        label = result.names[cls]
                        
                        if label in ['fire extinguisher', 'bottle']:
                            detections.append({
                                'bbox': [int(x1), int(y1), int(x2), int(y2)],
                                'confidence': float(conf),
                                'label': label,
                                'simulated': False
                            })
            
            if not detections:
                height, width = image.shape[:2]
                return [{
                    'bbox': [width//4, height//4, width*3//4, height*3//4],
                    'confidence': 0.7,
                    'label': 'fire_extinguisher',
                    'simulated': True,
                    'note': 'YOLO未检测到'
                }]
            
            return detections
            
        except Exception as e:
            logger.error(f"YOLO检测失败: {e}")
            height, width = image.shape[:2]
            return [{
                'bbox': [width//4, height//4, width*3//4, height*3//4],
                'confidence': 0.6,
                'label': 'fire_extinguisher',
                'simulated': True,
                'note': f'检测失败: {str(e)[:50]}'
            }]
    
    def find_gauge_region(self, image, bbox):
        """在灭火器边界框内找压力表区域（改进版）"""
        x1, y1, x2, y2 = bbox
        roi = image[y1:y2, x1:x2]
        
        if roi.size == 0:
            return None
        
        try:
            gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
            blurred = cv2.GaussianBlur(gray, (9, 9), 2)
            
            circles = cv2.HoughCircles(
                blurred, 
                cv2.HOUGH_GRADIENT, 
                dp=1.2, 
                minDist=30,
                param1=100, 
                param2=40,
                minRadius=15,
                maxRadius=min(roi.shape[0], roi.shape[1]) // 3
            )
            
            if circles is not None:
                circles = np.uint16(np.around(circles))
                x, y, r = circles[0][0]
                return {
                    'center': (x1 + x, y1 + y),
                    'radius': r,
                    'roi_bbox': [x1, y1, x2, y2],
                    'detected': True
                }
        except Exception as e:
            logger.warning(f"霍夫圆检测失败: {e}")
        
        center_x = x1 + (x2 - x1) // 2
        center_y = y1 + (y2 - y1) // 3
        radius = min(x2 - x1, y2 - y1) // 4
        
        return {
            'center': (center_x, center_y),
            'radius': radius,
            'roi_bbox': [x1, y1, x2, y2],
            'detected': False,
            'estimated': True
        }
    
    def detect_color_zones(self, image, gauge_info):
        """检测红绿黄颜色区域"""
        if not self.use_color_detection:
            return {}
        
        center_x, center_y = gauge_info['center']
        radius = gauge_info['radius']
        
        x1 = max(0, center_x - radius)
        y1 = max(0, center_y - radius)
        x2 = min(image.shape[1], center_x + radius)
        y2 = min(image.shape[0], center_y + radius)
        
        gauge_roi = image[y1:y2, x1:x2]
        
        if gauge_roi.size == 0:
            return {}
        
        try:
            hsv_roi = cv2.cvtColor(gauge_roi, cv2.COLOR_BGR2HSV)
            zones = {}
            
            for zone_name in ['red', 'green', 'yellow']:
                if zone_name in self.color_ranges:
                    mask = np.zeros(hsv_roi.shape[:2], dtype=np.uint8)
                    for lower, upper in self.color_ranges[zone_name]:
                        color_mask = cv2.inRange(hsv_roi, lower, upper)
                        mask = cv2.bitwise_or(mask, color_mask)
                    
                    kernel = np.ones((3, 3), np.uint8)
                    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
                    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
                    
                    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
                    
                    if contours:
                        largest_contour = max(contours, key=cv2.contourArea)
                        area = cv2.contourArea(largest_contour)
                        
                        if area > 100:
                            M = cv2.moments(largest_contour)
                            if M['m00'] > 0:
                                cx = int(M['m10'] / M['m00'])
                                cy = int(M['m01'] / M['m00'])
                                
                                global_cx = x1 + cx
                                global_cy = y1 + cy
                                
                                dx = global_cx - center_x
                                dy = global_cy - center_y
                                angle = math.degrees(math.atan2(dy, dx)) % 360
                                
                                zones[zone_name] = {
                                    'center': (global_cx, global_cy),
                                    'angle': angle,
                                    'area': area
                                }
            
            return zones
            
        except Exception as e:
            logger.warning(f"颜色区域检测失败: {e}")
            return {}
    
    def detect_pointer_optimized(self, image, gauge_info):
        """优化版指针检测"""
        center_x, center_y = gauge_info['center']
        radius = gauge_info['radius']
        
        x1 = max(0, center_x - radius)
        y1 = max(0, center_y - radius)
        x2 = min(image.shape[1], center_x + radius)
        y2 = min(image.shape[0], center_y + radius)
        
        gauge_roi = image[y1:y2, x1:x2]
        
        if gauge_roi.size == 0:
            return None
        
        try:
            # 方法1: 颜色检测
            hsv_roi = cv2.cvtColor(gauge_roi, cv2.COLOR_BGR2HSV)
            
            pointer_mask = np.zeros(hsv_roi.shape[:2], dtype=np.uint8)
            for lower, upper in self.color_ranges['pointer']:
                color_mask = cv2.inRange(hsv_roi, lower, upper)
                pointer_mask = cv2.bitwise_or(pointer_mask, color_mask)
            
            kernel = np.ones((3, 3), np.uint8)
            pointer_mask = cv2.morphologyEx(pointer_mask, cv2.MORPH_CLOSE, kernel)
            pointer_mask = cv2.morphologyEx(pointer_mask, cv2.MORPH_OPEN, kernel)
            
            contours, _ = cv2.findContours(pointer_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            if contours:
                longest_contour = max(contours, key=cv2.contourArea)
                [vx, vy, x, y] = cv2.fitLine(longest_contour, cv2.DIST_L2, 0, 0.01, 0.01)
                
                angle = math.degrees(math.atan2(vy[0], vx[0])) % 360
                length = radius * 0.7
                
                start_x = center_x
                start_y = center_y
                end_x = int(start_x + length * vx[0])
                end_y = int(start_y + length * vy[0])
                
                return {
                    'line': [start_x, start_y, end_x, end_y],
                    'angle': angle,
                    'detected': True,
                    'method': 'color_contour',
                    'confidence': 0.9
                }
            
        except Exception as e:
            logger.warning(f"颜色指针检测失败: {e}")
        
        try:
            # 方法2: 霍夫直线检测
            gray_roi = cv2.cvtColor(gauge_roi, cv2.COLOR_BGR2GRAY)
            edges = cv2.Canny(gray_roi, 50, 150)
            
            lines = cv2.HoughLinesP(
                edges,
                rho=1,
                theta=np.pi/180,
                threshold=30,
                minLineLength=radius//2,
                maxLineGap=10
            )
            
            if lines is not None:
                longest_line = None
                max_length = 0
                roi_center_x = radius
                roi_center_y = radius
                
                for line in lines:
                    x1_l, y1_l, x2_l, y2_l = line[0]
                    length = math.sqrt((x2_l - x1_l)**2 + (y2_l - y1_l)**2)
                    
                    dist1 = math.sqrt((x1_l - roi_center_x)**2 + (y1_l - roi_center_y)**2)
                    dist2 = math.sqrt((x2_l - roi_center_x)**2 + (y2_l - roi_center_y)**2)
                    
                    if length > max_length and (dist1 < radius/2 or dist2 < radius/2):
                        max_length = length
                        longest_line = line[0]
                
                if longest_line is not None:
                    x1_l, y1_l, x2_l, y2_l = longest_line
                    global_x1 = x1 + x1_l
                    global_y1 = y1 + y1_l
                    global_x2 = x1 + x2_l
                    global_y2 = y1 + y2_l
                    
                    dx = global_x2 - global_x1
                    dy = global_y2 - global_y1
                    angle = math.degrees(math.atan2(dy, dx)) % 360
                    
                    return {
                        'line': [global_x1, global_y1, global_x2, global_y2],
                        'angle': angle,
                        'detected': True,
                        'method': 'hough_lines',
                        'confidence': 0.7
                    }
            
        except Exception as e:
            logger.warning(f"霍夫直线检测失败: {e}")
        
        # 方法3: 模拟
        return {
            'line': [center_x, center_y, 
                    center_x + int(radius * 0.7), center_y],
            'angle': 180,
            'detected': False,
            'method': 'simulated',
            'confidence': 0.5
        }
    
    def judge_zone_with_color(self, pointer_angle, color_zones):
        """结合颜色信息判断区域"""
        if not color_zones or not self.use_color_detection:
            return self.judge_zone_by_angle(pointer_angle)
        
        min_angle_diff = float('inf')
        closest_zone = "green"
        
        for zone_name, zone_info in color_zones.items():
            zone_angle = zone_info['angle']
            angle_diff = min(abs(pointer_angle - zone_angle),
                           360 - abs(pointer_angle - zone_angle))
            
            if angle_diff < min_angle_diff:
                min_angle_diff = angle_diff
                closest_zone = zone_name
        
        if closest_zone == "green":
            confidence = max(0.9, 1.0 - min_angle_diff/60.0)
            return "green", confidence, "正常（无隐患）"
        elif closest_zone == "yellow":
            confidence = max(0.8, 1.0 - min_angle_diff/60.0)
            return "yellow", confidence, "警告（潜在隐患）"
        else:
            confidence = max(0.7, 1.0 - min_angle_diff/60.0)
            return "red", confidence, "隐患（需要处理）"
    
    def judge_zone_by_angle(self, angle):
        """根据角度判断区域"""
        angle = angle % 360
        
        if 0 <= angle < 120:
            return "green", 0.9, "正常（无隐患）"
        elif 120 <= angle < 240:
            return "yellow", 0.8, "警告（潜在隐患）"
        else:
            return "red", 0.7, "隐患（需要处理）"
    
    def detect(self, image):
        """主检测函数（优化版）"""
        try:
            # 1. 检测灭火器
            fire_detections = self.detect_fire_extinguisher(image)
            
            if not fire_detections:
                return {
                    "success": False,
                    "message": "未检测到灭火器",
                    "hazard_detected": False,
                    "confidence": 0.0,
                    "mode": "simulation"
                }
            
            best_detection = max(fire_detections, key=lambda x: x['confidence'])
            is_simulated = best_detection.get('simulated', False)
            
            # 2. 找压力表区域
            gauge_info = self.find_gauge_region(image, best_detection['bbox'])
            
            if gauge_info is None:
                return {
                    "success": False,
                    "message": "未找到压力表",
                    "hazard_detected": False,
                    "confidence": 0.0,
                    "mode": "simulation"
                }
            
            gauge_detected = gauge_info.get('detected', False)
            
            # 3. 检测颜色区域
            color_zones = self.detect_color_zones(image, gauge_info)
            
            # 4. 检测指针
            pointer_info = self.detect_pointer_optimized(image, gauge_info)
            
            if pointer_info is None:
                return {
                    "success": False,
                    "message": "未检测到指针",
                    "hazard_detected": False,
                    "confidence": 0.0,
                    "mode": "simulation"
                }
            
            pointer_detected = pointer_info.get('detected', False)
            
            # 5. 判断区域
            if color_zones and self.use_color_detection:
                zone, confidence, status = self.judge_zone_with_color(
                    pointer_info['angle'], color_zones)
                judgment_method = "color_based"
            else:
                zone, confidence, status = self.judge_zone_by_angle(pointer_info['angle'])
                judgment_method = "angle_based"
            
            # 结合指针检测置信度
            confidence = confidence * pointer_info.get('confidence', 0.5)
            confidence = min(confidence, 0.99)
            
            # 判断是否有隐患
            hazard_detected = zone != "green"
            
            # 6. 构建结果
            result = {
                "success": True,
                "hazard_detected": hazard_detected,
                "confidence": confidence,
                "hazard_name": "灭火器压力表异常" if hazard_detected else "灭火器压力表正常",
                "reasoning": [],
                "evidence": {
                    "fire_extinguisher_bbox": best_detection['bbox'],
                    "gauge_center": gauge_info['center'],
                    "gauge_radius": gauge_info['radius'],
                    "gauge_detected": gauge_detected,
                    "pointer_angle": float(pointer_info['angle']),
                    "pointer_detected": pointer_detected,
                    "pointer_method": pointer_info.get('method', 'unknown'),
                    "zones_detected": len(color_zones),
                    "zone": zone,
                    "status": status,
                    "judgment_method": judgment_method,
                    "zone_angles": self.zone_angles,
                    "zone_colors": {
                        'green': (0, 255, 0),
                        'yellow': (0, 255, 255),
                        'red': (0, 0, 255)
                    }
                },
                "mode": "simulation" if (is_simulated or not gauge_detected or not pointer_detected) else "real"
            }
            
            # 构建推理过程
            if is_simulated:
                result["reasoning"].append("模拟检测到灭火器")
                if best_detection.get('note'):
                    result["reasoning"].append(f"注: {best_detection['note']}")
            else:
                result["reasoning"].append(f"检测到灭火器 (置信度: {best_detection['confidence']:.2f})")
            
            if gauge_detected:
                result["reasoning"].append(f"定位压力表区域 (半径: {gauge_info['radius']}px)")
            else:
                result["reasoning"].append(f"估计压力表位置 (半径: {gauge_info['radius']}px)")
            
            if pointer_detected:
                result["reasoning"].append(f"检测到指针 (角度: {pointer_info['angle']:.1f}°, 方法: {pointer_info['method']})")
            else:
                result["reasoning"].append(f"模拟指针角度: {pointer_info['angle']:.1f}°")
            
            if color_zones:
                result["reasoning"].append(f"检测到 {len(color_zones)} 个颜色区域: {', '.join(color_zones.keys())}")
                result["reasoning"].append(f"区域判断方法: 基于颜色检测")
            else:
                result["reasoning"].append("未检测到颜色区域")
                result["reasoning"].append(f"区域判断方法: 基于角度 ({pointer_info['angle']:.1f}°)")
            
            result["reasoning"].append(f"指针位于{zone}区 ({status})")
            
            if hazard_detected:
                result["reasoning"].append("⚠️ 检测到隐患")
            else:
                result["reasoning"].append("✅ 无隐患")
            
            return result
            
        except Exception as e:
            import traceback
            logger.error(f"检测过程中出错: {e}")
            return {
                "success": False,
                "message": f"检测失败: {str(e)}",
                "hazard_detected": False,
                "confidence": 0.0,
                "mode": "error",
                "error": traceback.format_exc()
            }


# 测试代码
if __name__ == "__main__":
    print("🔥 优化版灭火器压力表检测器")
    print("=" * 60)
    print("🎯 主要改进:")
    print("  1. 红绿黄颜色区域检测")
    print("  2. 改进指针检测算法")
    print("  3. 智能区域判断（结合颜色和角度）")
    print("  4. 详细的推理过程")
    print()
    print("📊 区域定义:")
    print("  - 绿色区域: 0-120° (无隐患)")
    print("  - 黄色区域: 120-240° (潜在隐患)")
    print("  - 红色区域: 240-360° (有隐患)")
    print()
    print("💡 使用方法:")
    print("  1. 初始化: detector = FireExtinguisherDetectorOptimized()")
    print("  2. 检测: result = detector.detect(image)")
    print("  3. 查看结果: result['evidence']['zone'] 获取区域信息")
    print()
    print("✅ 代码生成完成!")
    print("📋 下一步: 安装OpenCV依赖后测试")