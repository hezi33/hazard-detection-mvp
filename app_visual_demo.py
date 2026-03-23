#!/usr/bin/env python3
"""
可视化演示应用 - 完整的算法可视化展示
"""

from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pathlib import Path
import uvicorn
import cv2
import numpy as np
import logging
import json
import base64
from io import BytesIO
import random

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 创建应用
app = FastAPI(
    title="算法可视化演示 - 隐患检测",
    version="4.0.0",
    description="完整的算法可视化展示，理解检测工作流程"
)

# 创建目录
Path("static").mkdir(exist_ok=True)
Path("uploads").mkdir(exist_ok=True)
Path("visual_results").mkdir(exist_ok=True)

# 挂载静态文件
app.mount("/static", StaticFiles(directory="static"), name="static")

# 尝试导入可视化组件
try:
    from visual_annotator import VisualAnnotator
    from detector_fixed import FireExtinguisherDetector
    
    annotator = VisualAnnotator()
    detector = FireExtinguisherDetector(use_simulation=True)
    logger.info("✅ 可视化组件加载成功")
    
except ImportError as e:
    logger.warning(f"可视化组件导入失败: {e}")
    
    # 创建模拟组件
    class VisualAnnotator:
        def annotate_image(self, image, result):
            # 简单绘制一些图形作为演示
            h, w = image.shape[:2]
            cv2.rectangle(image, (w//4, h//4), (w*3//4, h*3//4), (0, 0, 255), 2)
            cv2.circle(image, (w//2, h//2), min(w, h)//4, (255, 0, 0), 2)
            cv2.line(image, (w//2, h//2), (w//2 + 50, h//2), (0, 255, 0), 3)
            cv2.putText(image, "演示标注", (50, 50), 
                       cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
            return image
    
    class FireExtinguisherDetector:
        def detect(self, image):
            # 模拟检测结果
            h, w = image.shape[:2]
            angle = random.randint(0, 359)
            
            zone = "green"
            if 120 <= angle < 240:
                zone = "yellow"
            elif angle >= 240:
                zone = "red"
            
            return {
                "success": True,
                "hazard_detected": zone == "red",
                "confidence": 0.7 + random.random() * 0.25,
                "hazard_name": "灭火器压力表异常" if zone == "red" else "灭火器压力表正常",
                "reasoning": [
                    f"模拟检测到灭火器 (置信度: {0.8 + random.random()*0.15:.2f})",
                    f"估计压力表位置 (半径: {min(w, h)//8}px)",
                    f"模拟指针角度: {angle:.1f}°",
                    f"指针位于{zone}区",
                    "注：当前为演示数据，真实算法需要完整环境"
                ],
                "evidence": {
                    "fire_extinguisher_bbox": [w//4, h//4, w*3//4, h*3//4],
                    "gauge_center": [w//2, h//2],
                    "gauge_radius": min(w, h)//8,
                    "pointer_angle": float(angle),
                    "zone": zone,
                    "gauge_detected": False
                },
                "mode": "demo"
            }
    
    annotator = VisualAnnotator()
    detector = FireExtinguisherDetector()

def image_to_base64(image):
    """将OpenCV图像转换为base64字符串"""
    try:
        # 将BGR转换为RGB
        if len(image.shape) == 3 and image.shape[2] == 3:
            rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        else:
            rgb_image = image
        
        # 编码为JPEG
        success, encoded_image = cv2.imencode('.jpg', rgb_image, [cv2.IMWRITE_JPEG_QUALITY, 85])
        if not success:
            return None
        
        # 转换为base64
        img_str = base64.b64encode(encoded_image.tobytes()).decode()
        return f"data:image/jpeg;base64,{img_str}"
    
    except Exception as e:
        logger.error(f"图像转换失败: {e}")
        return None

@app.get("/", response_class=HTMLResponse)
async def home():
    """可视化演示首页"""
    try:
        with open("templates/visual_demo.html", "r", encoding="utf-8") as f:
            html_content = f.read()
        
        # 注入JavaScript
        with open("templates/visual_demo.js", "r", encoding="utf-8") as f:
            js_content = f.read()
        
        # 合并HTML和JS
        html_content = html_content.replace('</body>', f'<script>{js_content}</script></body>')
        
        return HTMLResponse(content=html_content)
        
    except FileNotFoundError:
        # 简单回退页面
        simple_html = """
        <!DOCTYPE html>
        <html>
        <head><title>算法可视化演示</title></head>
        <body>
            <h1>算法可视化演示</h1>
            <p>可视化文件未找到，请确保 visual_demo.html 和 visual_demo.js 在 templates 目录中。</p>
            <p><a href="/health">健康检查</a></p>
        </body>
        </html>
        """
        return HTMLResponse(content=simple_html)

@app.post("/api/check_visual")
async def check_with_visualization(file: UploadFile = File(...)):
    """可视化检测API"""
    try:
        # 读取图片
        contents = await file.read()
        nparr = np.frombuffer(contents, np.uint8)
        original_image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        if original_image is None:
            raise HTTPException(status_code=400, detail="无法读取图片")
        
        # 检测
        detection_result = detector.detect(original_image)
        
        # 可视化标注
        annotated_image = annotator.annotate_image(original_image.copy(), detection_result)
        
        # 创建对比图
        h1, w1 = original_image.shape[:2]
        h2, w2 = annotated_image.shape[:2]
        h = max(h1, h2)
        w = w1 + w2 + 20  # 留出间隔
        
        comparison_image = np.zeros((h, w, 3), dtype=np.uint8)
        comparison_image[:] = (40, 40, 40)  # 灰色背景
        
        # 放置原始图片
        comparison_image[0:h1, 0:w1] = original_image
        cv2.putText(comparison_image, "原始图片", (10, 30), 
                   cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
        
        # 放置标注图片
        comparison_image[0:h2, w1+20:w1+20+w2] = annotated_image
        cv2.putText(comparison_image, "算法标注", (w1+30, 30), 
                   cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
        
        # 转换为base64
        annotated_base64 = image_to_base64(annotated_image)
        comparison_base64 = image_to_base64(comparison_image)
        
        # 构建响应
        response = {
            "success": True,
            "detection_result": detection_result,
            "images": {
                "original": image_to_base64(original_image),
                "annotated": annotated_base64,
                "comparison": comparison_base64
            },
            "visualization": {
                "has_annotations": True,
                "annotation_types": [
                    "fire_extinguisher_bbox",
                    "gauge_circle", 
                    "pointer_line",
                    "zones"
                ]
            }
        }
        
        # 保存结果
        filename = Path(file.filename).stem
        cv2.imwrite(f"visual_results/{filename}_comparison.jpg", comparison_image)
        logger.info(f"✅ 可视化结果已保存: visual_results/{filename}_comparison.jpg")
        
        return JSONResponse(content=response)
        
    except Exception as e:
        logger.error(f"可视化检测失败: {str(e)}")
        
        # 返回错误但包含模拟数据
        error_response = {
            "success": False,
            "error": str(e),
            "detection_result": detector.detect(np.zeros((300, 400, 3), dtype=np.uint8)),
            "images": {
                "original": None,
                "annotated": None,
                "comparison": None
            },
            "message": "检测失败，返回模拟数据供演示"
        }
        
        return JSONResponse(content=error_response, status_code=500)

@app.get("/api/demo")
async def get_demo_data():
    """获取演示数据"""
    # 创建演示图像
    demo_image = np.zeros((400, 600, 3), dtype=np.uint8)
    demo_image[:] = (60, 60, 60)
    
    # 添加一些图形
    cv2.rectangle(demo_image, (100, 100), (500, 350), (0, 0, 255), 3)
    cv2.circle(demo_image, (300, 225), 80, (255, 0, 0), 3)
    cv2.line(demo_image, (300, 225), (380, 225), (0, 255, 0), 4)
    
    # 添加文本
    cv2.putText(demo_image, "算法可视化演示", (150, 50), 
               cv2.FONT_HERSHEY_SIMPLEX, 1.2, (255, 255, 255), 3)
    cv2.putText(demo_image, "红色框: 灭火器检测", (150, 380), 
               cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)
    cv2.putText(demo_image, "蓝色圆: 压力表定位", (150, 410), 
               cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 0, 0), 2)
    cv2.putText(demo_image, "绿色线: 指针方向", (150, 440), 
               cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
    
    # 模拟检测结果
    demo_result = {
        "success": True,
        "hazard_detected": False,
        "confidence": 0.88,
        "hazard_name": "灭火器压力表正常",
        "reasoning": [
            "演示: 检测到灭火器区域",
            "演示: 定位压力表位置",
            "演示: 分析指针方向 (45°)",
            "演示: 判断为绿区正常状态",
            "这是演示数据，上传真实图片查看实际检测"
        ],
        "evidence": {
            "fire_extinguisher_bbox": [100, 100, 500, 350],
            "gauge_center": [300, 225],
            "gauge_radius": 80,
            "pointer_angle": 45.0,
            "zone": "green",
            "gauge_detected": True
        },
        "mode": "demo"
    }
    
    # 标注图像
    demo_annotated = annotator.annotate_image(demo_image.copy(), demo_result)
    
    return {
        "demo_data": demo_result,
        "images": {
            "demo": image_to_base64(demo_image),
            "annotated": image_to_base64(demo_annotated)
        },
        "instructions": "上传真实图片查看算法实际工作流程"
    }

@app.get("/health")
async def health_check():
    """健康检查"""
    return {
        "status": "healthy",
        "service": "algorithm-visualization-demo",
        "version": "4.0.0",
        "features": [
            "完整的算法可视化",
            "实时图片标注",
            "对比视图",
            "模拟和真实检测",
            "交互式演示"
        ],
        "endpoints": {
            "GET /": "可视化演示界面",
            "POST /api/check_visual": "可视化检测API",
            "GET /api/demo": "演示数据",
            "GET /health": "健康检查"
        }
    }

@app.get("/test")
async def test_endpoint():
    """测试端点"""
    return {
        "message": "算法可视化演示服务运行正常",
        "timestamp": __import__("datetime").datetime.now().isoformat(),
        "ready": True
    }

if __name__ == "__main__":
    import sys
    
    # 获取端口参数
    port = 8003  # 使用新端口
    if "--port" in sys.argv:
        try:
            port_index = sys.argv.index("--port")
            port = int(sys.argv[port_index + 1])
        except:
            pass
    
    print("=" * 60)
    print("🚀 启动算法可视化演示服务")
    print("=" * 60)
    print(f"📡 主界面: http://localhost:{port}")
    print(f"🔧 可视化API: http://localhost:{port}/api/check_visual")
    print(f"🎮 演示数据: http://localhost:{port}/api/demo")
    print(f"💚 健康检查: http://localhost:{port}/health")
    print("")
    print("🎯 核心功能:")
    print("   • 上传图片实时可视化算法工作流程")
    print("   • 标注灭火器、压力表、指针、区域")
    print("   • 对比原始图片和标注结果")
    print("   • 理解算法每一步的检测过程")
    print("")
    print("📚 学习价值:")
    print("   • 看到算法如何'思考'和'判断'")
    print("   • 理解计算机视觉的工作原理")
    print("   • 验证算法输出的准确性")
    print("=" * 60)
    
    uvicorn.run(app, host="0.0.0.0", port=port, log_level="info")