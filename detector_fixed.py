import cv2
import numpy as np
import logging
import os
from pathlib import Path

logger = logging.getLogger(__name__)

class FireExtinguisherDetector:
    def __init__(self, use_simulation=True):
        """初始化检测器"""
        self.model = None
        self.use_simulation = use_simulation
        
        if not use_simulation:
            self.initialize_model()
        else:
            logger.info("使用模拟模式（跳过YOLO模型加载）")
    
    def initialize_model(self):
        """初始化YOLO模型 - 增强错误处理"""
        try:
            from ultralytics import YOLO
            
            # 检查缓存目录
            cache_dir = Path.home() / ".cache" / "ultralytics" / "hub"
            model_path = cache_dir / "yolov8n.pt"
            
            # 如果模型文件存在，使用本地文件
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
            self.model = None
        except Exception as e:
            logger.error(f"模型加载失败: {e}")
            logger.info("切换到模拟模式")
            self.use_simulation = True
            self.model = None
    
    def detect_fire_extinguisher(self, image):
        """检测灭火器"""
        if self.use_simulation or self.model is None:
            # 模拟检测结果
            height, width = image.shape[:2]
            return [{
                'bbox': [width//4, height//4, width*3//4, height*3//4],
                'confidence': 0.85,
                'label': 'fire_extinguisher',
                'simulated': True
            }]
        
        try:
            # 使用YOLO检测
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
                        
                        # 只关注灭火器（根据COCO类别）
                        if label in ['fire extinguisher', 'bottle']:
                            detections.append({
                                'bbox': [int(x1), int(y1), int(x2), int(y2)],
                                'confidence': float(conf),
                                'label': label,
                                'simulated': False
                            })
            
            # 如果没有检测到，返回模拟结果
            if not detections:
                height, width = image.shape[:2]
                return [{
                    'bbox': [width//4, height//4, width*3//4, height*3//4],
                    'confidence': 0.7,
                    'label': 'fire_extinguisher',
                    'simulated': True,
                    'note': 'YOLO未检测到，使用模拟'
                }]
            
            return detections
            
        except Exception as e:
            logger.error(f"YOLO检测失败: {e}")
            # 失败时返回模拟结果
            height, width = image.shape[:2]
            return [{
                'bbox': [width//4, height//4, width*3//4, height*3//4],
                'confidence': 0.6,
                'label': 'fire_extinguisher',
                'simulated': True,
                'note': f'检测失败: {str(e)[:50]}'
            }]
    
    def find_gauge_region(self, image, bbox):
        """在灭火器边界框内找压力表区域"""
        x1, y1, x2, y2 = bbox
        roi = image[y1:y2, x1:x2]
        
        if roi.size == 0:
            return None
        
        try:
            # 转换为灰度图
            gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
            
            # 找圆形（压力表）
            circles = cv2.HoughCircles(
                gray, 
                cv2.HOUGH_GRADIENT, 
                dp=1, 
                minDist=50,
                param1=50, 
                param2=30,
                minRadius=10,
                maxRadius=100
            )
            
            if circles is not None:
                circles = np.uint16(np.around(circles))
                # 取第一个圆
                x, y, r = circles[0][0]
                return {
                    'center': (x1 + x, y1 + y),
                    'radius': r,
                    'roi_bbox': [x1, y1, x2, y2],
                    'detected': True
                }
        except Exception as e:
            logger.warning(f"霍夫圆检测失败: {e}")
        
        # 如果没找到圆，返回ROI中心区域（模拟）
        center_x = x1 + (x2 - x1) // 2
        center_y = y1 + (y2 - y1) // 3  # 压力表通常在灭火器上部
        radius = min(x2 - x1, y2 - y1) // 4
        
        return {
            'center': (center_x, center_y),
            'radius': radius,
            'roi_bbox': [x1, y1, x2, y2],
            'detected': False,
            'estimated': True
        }
    
    def detect_pointer(self, image, gauge_info):
        """检测指针"""
        center_x, center_y = gauge_info['center']
        radius = gauge_info['radius']
        
        # 提取表盘区域
        x1 = max(0, center_x - radius)
        y1 = max(0, center_y - radius)
        x2 = min(image.shape[1], center_x + radius)
        y2 = min(image.shape[0], center_y + radius)
        
        gauge_roi = image[y1:y2, x1:x2]
        
        if gauge_roi.size == 0:
            return None
        
        try:
            # 转换为灰度并找边缘
            gray = cv2.cvtColor(gauge_roi, cv2.COLOR_BGR2GRAY)
            edges = cv2.Canny(gray, 50, 150)
            
            # 霍夫变换找直线
            lines = cv2.HoughLinesP(
                edges, 
                rho=1, 
                theta=np.pi/180, 
                threshold=20,
                minLineLength=radius//2,
                maxLineGap=10
            )
            
            if lines is not None:
                # 找最长的线作为指针
                longest_line = None
                max_length = 0
                
                for line in lines:
                    x1_l, y1_l, x2_l, y2_l = line[0]
                    length = np.sqrt((x2_l - x1_l)**2 + (y2_l - y1_l)**2)
                    if length > max_length:
                        max_length = length
                        longest_line = line[0]
                
                if longest_line is not None:
                    # 计算角度（以中心为原点）
                    dx = longest_line[2] - longest_line[0]
                    dy = longest_line[3] - longest_line[1]
                    angle = np.degrees(np.arctan2(dy, dx)) % 360
                    
                    return {
                        'line': longest_line,
                        'angle': angle,
                        'length': max_length,
                        'detected': True
                    }
        except Exception as e:
            logger.warning(f"霍夫直线检测失败: {e}")
        
        # 模拟指针（用于测试）
        import random
        angle = random.randint(0, 359)
        return {
            'line': [radius//2, radius//2, radius, radius//2],
            'angle': angle,
            'length': radius//2,
            'detected': False,
            'simulated': True
        }
    
    def judge_zone(self, angle):
        """根据角度判断区域"""
        # 绿区：0-120°，黄区：120-240°，红区：240-360°
        if 0 <= angle < 120:
            return "green", 0.9, "正常"
        elif 120 <= angle < 240:
            return "yellow", 0.8, "警告"
        else:
            return "red", 0.7, "隐患"
    
    def detect(self, image):
        """主检测函数"""
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
            
            # 取置信度最高的灭火器
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
            
            # 3. 检测指针
            pointer_info = self.detect_pointer(image, gauge_info)
            
            if pointer_info is None:
                return {
                    "success": False,
                    "message": "未检测到指针",
                    "hazard_detected": False,
                    "confidence": 0.0,
                    "mode": "simulation"
                }
            
            pointer_detected = pointer_info.get('detected', False)
            
            # 4. 判断区域
            zone, confidence, status = self.judge_zone(pointer_info['angle'])
            hazard_detected = zone != "green"
            
            # 5. 构建结果
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
                    "pointer_angle": pointer_info['angle'],
                    "zone": zone,
                    "status": status
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
                result["reasoning"].append(f"检测到指针 (角度: {pointer_info['angle']:.1f}°)")
            else:
                result["reasoning"].append(f"模拟指针角度: {pointer_info['angle']:.1f}°")
            
            result["reasoning"].append(f"指针位于{zone}区 ({status})")
            
            # 调整置信度
            if is_simulated or not gauge_detected or not pointer_detected:
                result["confidence"] *= 0.7
                result["reasoning"].append("注：部分数据为模拟/估计值")
            
            return result
            
        except Exception as e:
            logger.error(f"检测过程中出错: {e}")
            return {
                "success": False,
                "message": f"检测失败: {str(e)}",
                "hazard_detected": False,
                "confidence": 0.0,
                "mode": "error"
            }