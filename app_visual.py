#!/usr/bin/env python3
"""
增强版API - 返回带可视化标注的图片
"""

from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse, Response
from fastapi.staticfiles import StaticFiles
from pathlib import Path
import uvicorn
import cv2
import numpy as np
import logging
import json
import base64
from io import BytesIO

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 创建应用
app = FastAPI(
    title="Hazard Detection MVP - 可视化增强版",
    version="3.0.0",
    description="灭火器压力表检测系统 - 返回带标注的图片"
)

# 创建目录
Path("static").mkdir(exist_ok=True)
Path("uploads").mkdir(exist_ok=True)
Path("annotated").mkdir(exist_ok=True)

# 挂载静态文件
app.mount("/static", StaticFiles(directory="static"), name="static")

# 导入检测器和标注器
try:
    from detector_fixed import FireExtinguisherDetector
    from visual_annotator import VisualAnnotator
    
    # 初始化
    detector = FireExtinguisherDetector(use_simulation=True)
    annotator = VisualAnnotator()
    logger.info("✅ 使用增强版检测器和标注器")
    
except ImportError as e:
    logger.error(f"导入失败: {e}")
    # 创建虚拟类
    class FireExtinguisherDetector:
        def detect(self, image):
            return {"success": False, "message": "检测器未加载"}
    
    class VisualAnnotator:
        def annotate_image(self, image, result):
            return image
    
    detector = FireExtinguisherDetector()
    annotator = VisualAnnotator()

def image_to_base64(image):
    """将OpenCV图像转换为base64字符串"""
    try:
        # 将BGR转换为RGB
        rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        
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
    """首页 - 可视化增强版"""
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <title>隐患检测 - 可视化增强版</title>
        <style>
            body { font-family: Arial; padding: 20px; }
            .container { max-width: 1200px; margin: 0 auto; }
            .upload-area { border: 2px solid #4CAF50; padding: 20px; margin: 20px 0; }
            .result-area { display: flex; gap: 20px; margin: 20px 0; }
            .image-box { flex: 1; border: 1px solid #ddd; padding: 10px; }
            .image-box img { max-width: 100%; max-height: 400px; }
            .json-box { flex: 1; background: #f5f5f5; padding: 15px; overflow: auto; }
            pre { white-space: pre-wrap; }
            .loading { display: none; text-align: center; margin: 20px; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🔥 隐患检测 - 可视化增强版</h1>
            <p>上传图片，返回带标注的可视化结果</p>
            
            <div class="upload-area">
                <h3>上传图片</h3>
                <input type="file" id="fileInput" accept="image/*">
                <br><br>
                <button onclick="uploadFile()">检测并可视化</button>
                <div class="loading" id="loading">处理中...</div>
            </div>
            
            <div class="result-area" id="resultArea" style="display:none;">
                <div class="image-box">
                    <h3>原始图片</h3>
                    <img id="originalImage" src="" alt="原始图片">
                </div>
                
                <div class="image-box">
                    <h3>标注结果</h3>
                    <img id="annotatedImage" src="" alt="标注结果">
                </div>
                
                <div class="json-box">
                    <h3>检测数据</h3>
                    <pre id="resultJson"></pre>
                </div>
            </div>
        </div>
        
        <script>
            let originalImageData = null;
            
            function uploadFile() {
                const fileInput = document.getElementById('fileInput');
                const file = fileInput.files[0];
                
                if (!file) {
                    alert('请先选择图片');
                    return;
                }
                
                // 显示加载
                document.getElementById('loading').style.display = 'block';
                document.getElementById('resultArea').style.display = 'none';
                
                // 预览原始图片
                const reader = new FileReader();
                reader.onload = function(e) {
                    document.getElementById('originalImage').src = e.target.result;
                    originalImageData = e.target.result;
                };
                reader.readAsDataURL(file);
                
                // 上传文件
                const formData = new FormData();
                formData.append('file', file);
                
                fetch('/api/check_visual', {
                    method: 'POST',
                    body: formData
                })
                .then(response => response.json())
                .then(data => {
                    displayResults(data);
                })
                .catch(error => {
                    alert('上传失败: ' + error.message);
                })
                .finally(() => {
                    document.getElementById('loading').style.display = 'none';
                });
            }
            
            function displayResults(data) {
                // 显示标注图片
                if (data.annotated_image) {
                    document.getElementById('annotatedImage').src = data.annotated_image;
                }
                
                // 显示JSON数据
                document.getElementById('resultJson').textContent = 
                    JSON.stringify(data.detection_result, null, 2);
                
                // 显示结果区域
                document.getElementById('resultArea').style.display = 'flex';
            }
            
            // 测试功能
            function testVisualization() {
                // 使用测试图片
                const testImage = 'https://via.placeholder.com/400x300/4CAF50/FFFFFF?text=Test+Image';
                document.getElementById('originalImage').src = testImage;
                
                // 模拟结果
                const mockResult = {
                    detection_result: {
                        success: true,
                        hazard_detected: false,
                        confidence: 0.85,
                        hazard_name: "灭火器压力表正常",
                        reasoning: ["测试数据"],
                        evidence: {
                            fire_extinguisher_bbox: [50, 50, 350, 250],
                            gauge_center: [200, 150],
                            gauge_radius: 40,
                            pointer_angle: 45,
                            zone: "green"
                        }
                    },
                    annotated_image: testImage
                };
                
                displayResults(mockResult);
            }
        </script>
        
        <div style="margin-top: 30px; text-align: center;">
            <button onclick="testVisualization()">测试可视化</button>
            <button onclick="fetch('/health').then(r => r.json()).then(d => alert(JSON.stringify(d)))">健康检查</button>
        </div>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)

@app.post("/api/check_visual")
async def check_with_visualization(file: UploadFile = File(...)):
    """API端点：检测并返回带标注的图片"""
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
        
        # 转换为base64
        annotated_base64 = image_to_base64(annotated_image)
        
        # 构建响应
        response = {
            "success": True,
            "detection_result": detection_result,
            "annotated_image": annotated_base64,
            "image_info": {
                "original_size": original_image.shape,
                "filename": file.filename,
                "content_type": file.content_type
            }
        }
        
        # 保存文件（可选）
        if detection_result.get('success', False):
            filename = Path(file.filename).stem
            cv2.imwrite(f"annotated/{filename}_annotated.jpg", annotated_image)
            logger.info(f"✅ 标注图片已保存: annotated/{filename}_annotated.jpg")
        
        return JSONResponse(content=response)
        
    except Exception as e:
        logger.error(f"可视化检测失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"可视化检测失败: {str(e)}")

@app.post("/api/check")
async def check_fire_extinguisher(file: UploadFile = File(...)):
    """原始API端点（保持兼容）"""
    try:
        contents = await file.read()
        nparr = np.frombuffer(contents, np.uint8)
        image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        if image is None:
            raise HTTPException(status_code=400, detail="无法读取图片")
        
        result = detector.detect(image)
        return JSONResponse(content=result)
        
    except Exception as e:
        logger.error(f"检测失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"检测失败: {str(e)}")

@app.get("/health")
async def health_check():
    """健康检查"""
    return {
        "status": "healthy",
        "service": "hazard-detection-visual",
        "version": "3.0.0",
        "features": [
            "可视化标注",
            "原始图片+标注图片对比",
            "Base64图像返回",
            "兼容原始API"
        ]
    }

@app.get("/test_annotation")
async def test_annotation():
    """测试标注功能"""
    # 创建测试图像
    test_image = np.zeros((300, 400, 3), dtype=np.uint8)
    test_image[:] = (100, 100, 100)
    
    # 模拟检测结果
    test_result = {
        "success": True,
        "hazard_detected": False,
        "confidence": 0.9,
        "hazard_name": "测试数据",
        "reasoning": ["这是测试数据"],
        "evidence": {
            "fire_extinguisher_bbox": [50, 50, 350, 250],
            "gauge_center": [200, 150],
            "gauge_radius": 40,
            "pointer_angle": 60,
            "zone": "green"
        }
    }
    
    # 标注
    annotated = annotator.annotate_image(test_image, test_result)
    
    # 转换为base64
    base64_str = image_to_base64(annotated)
    
    return {
        "test_result": test_result,
        "annotated_image": base64_str,
        "message": "标注测试完成"
    }

if __name__ == "__main__":
    import sys
    
    # 获取端口参数
    port = 8002  # 使用新端口避免冲突
    if "--port" in sys.argv:
        try:
            port_index = sys.argv.index("--port")
            port = int(sys.argv[port_index + 1])
        except:
            pass
    
    print("🚀 启动隐患检测 - 可视化增强版")
    print("=" * 50)
    print(f"📡 访问地址: http://localhost:{port}")
    print(f"🔧 可视化API: http://localhost:{port}/api/check_visual")
    print(f"🔧 原始API: http://localhost:{port}/api/check")
    print(f"💚 健康检查: http://localhost:{port}/health")
    print(f"🧪 测试标注: http://localhost:{port}/test_annotation")
    print("")
    print("🎯 新功能:")
    print("   • 返回带标注的图片")
    print("   • 原始图片和标注图片对比")
    print("   • 可视化算法输出")
    print("=" * 50)
    
    uvicorn.run(app, host="0.0.0.0", port=port, log_level="info")