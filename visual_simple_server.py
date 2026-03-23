#!/usr/bin/env python3
"""
独立可视化服务器 - 避免路由冲突
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

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 创建应用
app = FastAPI(
    title="独立可视化服务器",
    version="1.0.0",
    description="基于工作正常逻辑的可视化演示"
)

# 创建目录
Path("static").mkdir(exist_ok=True)
Path("uploads").mkdir(exist_ok=True)
Path("visual_results").mkdir(exist_ok=True)

# 挂载静态文件
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/", response_class=HTMLResponse)
async def home():
    """简化版可视化首页"""
    try:
        with open("templates/visual_simple.html", "r", encoding="utf-8") as f:
            return HTMLResponse(content=f.read())
    except FileNotFoundError:
        # 如果文件不存在，内联HTML
        html = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>独立可视化测试</title>
            <style>
                body { font-family: Arial; padding: 20px; }
                #preview { max-width: 400px; border: 1px solid #ccc; }
            </style>
        </head>
        <body>
            <h1>独立可视化测试</h1>
            <p>如果看到这个页面，说明服务器运行正常。</p>
            <input type="file" id="fileInput" accept="image/*">
            <button onclick="test()">测试</button>
            <img id="preview">
            <script>
                function test() {
                    const file = document.getElementById('fileInput').files[0];
                    const reader = new FileReader();
                    reader.onload = function(e) {
                        document.getElementById('preview').src = e.target.result;
                        alert('文件读取成功！');
                    };
                    reader.readAsDataURL(file);
                }
            </script>
        </body>
        </html>
        """
        return HTMLResponse(content=html)

@app.post("/api/check_visual")
async def check_visual(file: UploadFile = File(...)):
    """可视化检测API"""
    try:
        # 读取图片
        contents = await file.read()
        nparr = np.frombuffer(contents, np.uint8)
        image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        if image is None:
            raise HTTPException(status_code=400, detail="无法读取图片")
        
        # 模拟检测结果
        height, width = image.shape[:2]
        
        # 创建标注图片（模拟红色矩形、蓝色圆形、绿色直线）
        annotated = image.copy()
        
        # 红色矩形框（模拟灭火器检测）
        cv2.rectangle(annotated, (50, 50), (width-50, height-50), (0, 0, 255), 3)
        
        # 蓝色圆形（模拟压力表）
        center_x, center_y = width // 2, height // 2
        radius = min(width, height) // 4
        cv2.circle(annotated, (center_x, center_y), radius, (255, 0, 0), 3)
        
        # 绿色直线（模拟指针）
        angle = 210  # 模拟角度
        length = radius * 0.8
        end_x = int(center_x + length * np.cos(np.radians(angle)))
        end_y = int(center_y + length * np.sin(np.radians(angle)))
        cv2.line(annotated, (center_x, center_y), (end_x, end_y), (0, 255, 0), 3)
        
        # 转换为base64
        _, buffer = cv2.imencode('.jpg', annotated)
        annotated_base64 = base64.b64encode(buffer).decode('utf-8')
        
        # 构建响应
        response = {
            "success": True,
            "detection_result": {
                "success": True,
                "hazard_detected": angle > 240,  # 角度>240°为红区
                "confidence": 0.88,
                "hazard_name": "灭火器压力表" + ("异常" if angle > 240 else "正常"),
                "reasoning": [
                    f"模拟检测: 灭火器边界框 [50, 50, {width-50}, {height-50}]",
                    f"模拟定位: 压力表中心 ({center_x}, {center_y}), 半径 {radius}px",
                    f"模拟检测: 指针角度 {angle}°",
                    f"区域判断: {'红区(隐患)' if angle > 240 else '黄区(警告)' if angle > 120 else '绿区(正常)'}",
                    "注: 当前为模拟演示数据"
                ],
                "evidence": {
                    "fire_extinguisher_bbox": [50, 50, width-50, height-50],
                    "gauge_center": [center_x, center_y],
                    "gauge_radius": radius,
                    "pointer_angle": angle,
                    "zone": "red" if angle > 240 else "yellow" if angle > 120 else "green"
                },
                "mode": "simulation"
            },
            "annotated_image": f"data:image/jpeg;base64,{annotated_base64}"
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
                    "error": str(e)
                }
            }
        )

@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "service": "visual-simple-standalone",
        "version": "1.0.0",
        "endpoints": {
            "/": "简化可视化首页",
            "/api/check_visual": "可视化检测API",
            "/health": "健康检查"
        }
    }

if __name__ == "__main__":
    print("🚀 启动独立可视化服务器")
    print("📡 访问: http://localhost:8009")
    print("🔧 基于工作正常逻辑，包含模拟可视化")
    print("\n按 Ctrl+C 停止服务器")
    
    uvicorn.run(app, host="0.0.0.0", port=8009)