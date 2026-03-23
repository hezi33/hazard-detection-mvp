#!/usr/bin/env python3
"""
真实算法可视化服务器 - 使用真实的灭火器压力表检测算法
"""

from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pathlib import Path
import uvicorn
import cv2
import numpy as np
import logging
import base64
from io import BytesIO

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 创建应用
app = FastAPI(
    title="真实算法可视化服务器",
    version="1.0.0",
    description="使用真实的灭火器压力表检测算法"
)

# 创建目录
Path("static").mkdir(exist_ok=True)
Path("uploads").mkdir(exist_ok=True)
Path("visual_results").mkdir(exist_ok=True)

# 挂载静态文件
app.mount("/static", StaticFiles(directory="static"), name="static")

# 尝试导入真实检测器
try:
    from detector_fixed import FireExtinguisherDetector
    from visual_annotator import VisualAnnotator
    
    # 初始化检测器和标注器
    detector = FireExtinguisherDetector(use_simulation=False)  # 使用真实模式
    annotator = VisualAnnotator()
    
    logger.info("✅ 真实算法组件加载成功")
    
except ImportError as e:
    logger.warning(f"真实算法导入失败: {e}")
    logger.info("⚠️  使用模拟模式作为后备")
    
    # 创建模拟组件作为后备
    class MockDetector:
        def detect(self, image):
            height, width = image.shape[:2]
            return {
                "success": True,
                "hazard_detected": False,
                "confidence": 0.85,
                "hazard_name": "灭火器压力表正常（模拟）",
                "reasoning": [
                    "模拟: YOLOv8检测灭火器区域",
                    "模拟: 霍夫圆检测压力表",
                    "模拟: 霍夫直线检测指针",
                    "模拟: 角度分析判断区域",
                    "注: 当前为模拟数据，需解决PyTorch 2.6兼容性问题"
                ],
                "evidence": {
                    "fire_extinguisher_bbox": [50, 50, width-50, height-50],
                    "gauge_center": [width//2, height//2],
                    "gauge_radius": min(width, height)//4,
                    "pointer_angle": 150,
                    "zone": "green",
                    "gauge_detected": True
                },
                "mode": "simulation"
            }
    
    class MockAnnotator:
        def annotate_image(self, image, detection_result):
            annotated = image.copy()
            height, width = image.shape[:2]
            
            evidence = detection_result.get("evidence", {})
            
            # 红色矩形框 - 灭火器
            bbox = evidence.get("fire_extinguisher_bbox", [50, 50, width-50, height-50])
            cv2.rectangle(annotated, (bbox[0], bbox[1]), (bbox[2], bbox[3]), (0, 0, 255), 3)
            
            # 蓝色圆形 - 压力表
            center = evidence.get("gauge_center", [width//2, height//2])
            radius = evidence.get("gauge_radius", min(width, height)//4)
            cv2.circle(annotated, (center[0], center[1]), radius, (255, 0, 0), 3)
            cv2.circle(annotated, (center[0], center[1]), 5, (255, 0, 0), -1)
            
            # 绿色直线 - 指针
            angle = evidence.get("pointer_angle", 150)
            length = radius * 0.8
            end_x = int(center[0] + length * np.cos(np.radians(angle)))
            end_y = int(center[1] + length * np.sin(np.radians(angle)))
            cv2.line(annotated, (center[0], center[1]), (end_x, end_y), (0, 255, 0), 3)
            cv2.circle(annotated, (end_x, end_y), 5, (0, 255, 0), -1)
            
            return annotated
    
    detector = MockDetector()
    annotator = MockAnnotator()

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

@app.get("/", response_class=HTMLResponse)
async def home():
    """真实算法可视化首页"""
    try:
        with open("templates/visual_simple.html", "r", encoding="utf-8") as f:
            html = f.read()
            # 修改标题
            html = html.replace("算法可视化演示", "真实算法可视化演示")
            return HTMLResponse(content=html)
    except FileNotFoundError:
        # 简单回退
        html = """
        <!DOCTYPE html>
        <html>
        <head><title>真实算法可视化</title></head>
        <body>
            <h1>真实算法可视化演示</h1>
            <p>使用真实的灭火器压力表检测算法</p>
            <p><a href="/health">健康检查</a></p>
        </body>
        </html>
        """
        return HTMLResponse(content=html)

@app.post("/api/check_visual")
async def check_visual(file: UploadFile = File(...)):
    """真实算法可视化检测API"""
    try:
        # 读取图片
        contents = await file.read()
        nparr = np.frombuffer(contents, np.uint8)
        original_image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        if original_image is None:
            raise HTTPException(status_code=400, detail="无法读取图片")
        
        logger.info(f"处理图片: {file.filename}, 尺寸: {original_image.shape}")
        
        # 使用真实算法检测
        detection_result = detector.detect(original_image)
        logger.info(f"检测结果: {detection_result.get('hazard_name', '未知')}")
        
        # 转换NumPy类型为Python原生类型（修复JSON序列化问题）
        detection_result = convert_numpy_types(detection_result)
        
        # 可视化标注
        annotated_image = annotator.annotate_image(original_image.copy(), detection_result)
        
        # 创建对比图
        h1, w1 = original_image.shape[:2]
        h2, w2 = annotated_image.shape[:2]
        h = max(h1, h2)
        w = w1 + w2 + 20
        
        comparison_image = np.zeros((h, w, 3), dtype=np.uint8)
        comparison_image[:] = (40, 40, 40)
        
        # 放置原始图片
        comparison_image[0:h1, 0:w1] = original_image
        cv2.putText(comparison_image, "原始图片", (10, 30), 
                   cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
        
        # 放置标注图片
        comparison_image[0:h2, w1+20:w1+20+w2] = annotated_image
        cv2.putText(comparison_image, "算法标注", (w1+30, 30), 
                   cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
        
        # 添加图例
        legend_y = h - 100
        cv2.rectangle(comparison_image, (10, legend_y), (30, legend_y+20), (0, 0, 255), -1)
        cv2.putText(comparison_image, "灭火器检测", (40, legend_y+15), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)
        
        cv2.circle(comparison_image, (150, legend_y+10), 8, (255, 0, 0), -1)
        cv2.putText(comparison_image, "压力表定位", (170, legend_y+15), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)
        
        cv2.line(comparison_image, (280, legend_y), (320, legend_y+20), (0, 255, 0), 3)
        cv2.putText(comparison_image, "指针方向", (330, legend_y+15), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)
        
        # 转换为base64
        _, buffer = cv2.imencode('.jpg', annotated_image)
        annotated_base64 = base64.b64encode(buffer).decode('utf-8')
        
        _, buffer2 = cv2.imencode('.jpg', comparison_image)
        comparison_base64 = base64.b64encode(buffer2).decode('utf-8')
        
        # 构建响应
        response = {
            "success": True,
            "detection_result": detection_result,
            "images": {
                "annotated": f"data:image/jpeg;base64,{annotated_base64}",
                "comparison": f"data:image/jpeg;base64,{comparison_base64}"
            }
        }
        
        return JSONResponse(content=response)
        
    except Exception as e:
        logger.error(f"API错误: {e}")
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "error": str(e),
                "detection_result": {
                    "success": False,
                    "hazard_detected": False,
                    "error": str(e),
                    "mode": "error"
                }
            }
        )

@app.get("/health")
async def health():
    mode = "real" if hasattr(detector, '__class__') and detector.__class__.__name__ != "MockDetector" else "simulation"
    return {
        "status": "healthy",
        "service": "visual-real-algorithm",
        "version": "1.0.0",
        "mode": mode,
        "algorithm": "真实灭火器压力表检测" if mode == "real" else "模拟算法（需解决PyTorch兼容性）"
    }

if __name__ == "__main__":
    print("🚀 启动真实算法可视化服务器")
    print("📡 访问: http://localhost:8010")
    print("🔧 模式:", "真实算法" if hasattr(detector, '__class__') and detector.__class__.__name__ != "MockDetector" else "模拟算法")
    print("\n按 Ctrl+C 停止服务器")
    
    uvicorn.run(app, host="0.0.0.0", port=8010)