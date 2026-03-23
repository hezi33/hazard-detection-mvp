#!/usr/bin/env python3
"""
可视化调试服务器
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
    title="算法可视化调试",
    version="1.0.0",
    description="调试文件上传问题"
)

# 创建目录
Path("static").mkdir(exist_ok=True)
Path("uploads").mkdir(exist_ok=True)

# 挂载静态文件
app.mount("/static", StaticFiles(directory="static"), name="static")

# 保存调试JS文件
debug_js_path = Path("templates/visual_demo_debug.js")
if debug_js_path.exists():
    static_js_path = Path("static/visual_demo_debug.js")
    static_js_path.write_text(debug_js_path.read_text())
    logger.info("✅ 调试JS文件已复制到static目录")

@app.get("/", response_class=HTMLResponse)
async def debug_home():
    """调试首页"""
    try:
        with open("templates/visual_demo_debug.html", "r", encoding="utf-8") as f:
            return HTMLResponse(content=f.read())
    except FileNotFoundError:
        # 简单回退
        html = """
        <!DOCTYPE html>
        <html>
        <head><title>调试服务器</title></head>
        <body>
            <h1>可视化调试服务器</h1>
            <p>调试文件: templates/visual_demo_debug.html 未找到</p>
            <p><a href="/health">健康检查</a></p>
        </body>
        </html>
        """
        return HTMLResponse(content=html)

@app.get("/simple", response_class=HTMLResponse)
async def simple_test():
    """简单测试页面"""
    try:
        with open("templates/simple_test.html", "r", encoding="utf-8") as f:
            return HTMLResponse(content=f.read())
    except FileNotFoundError:
        return HTMLResponse(content="<h1>简单测试页面未找到</h1>")

@app.post("/api/check_debug")
async def check_debug(file: UploadFile = File(...)):
    """调试API - 简单返回文件信息"""
    try:
        # 读取文件
        contents = await file.read()
        
        # 尝试解码为图片
        nparr = np.frombuffer(contents, np.uint8)
        image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        response = {
            "success": True,
            "file_info": {
                "filename": file.filename,
                "content_type": file.content_type,
                "size_bytes": len(contents),
                "received": True
            }
        }
        
        if image is not None:
            response["image_info"] = {
                "width": image.shape[1],
                "height": image.shape[0],
                "channels": image.shape[2] if len(image.shape) > 2 else 1,
                "is_valid": True
            }
            
            # 转换为base64返回
            _, buffer = cv2.imencode('.jpg', image)
            img_base64 = base64.b64encode(buffer).decode('utf-8')
            response["image_preview"] = f"data:image/jpeg;base64,{img_base64}"
        else:
            response["image_info"] = {
                "is_valid": False,
                "error": "无法解码为图片"
            }
        
        return JSONResponse(content=response)
        
    except Exception as e:
        logger.error(f"调试API错误: {e}")
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "error": str(e),
                "file_info": {
                    "filename": file.filename if file else "unknown",
                    "content_type": file.content_type if file else "unknown"
                }
            }
        )

@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "service": "visual-debug",
        "version": "1.0.0",
        "endpoints": {
            "/": "调试主页",
            "/simple": "简单测试",
            "/api/check_debug": "调试API",
            "/health": "健康检查"
        }
    }

if __name__ == "__main__":
    print("🔥 启动可视化调试服务器")
    print("📡 访问地址:")
    print("  调试主页: http://localhost:8005")
    print("  简单测试: http://localhost:8005/simple")
    print("  健康检查: http://localhost:8005/health")
    print("\n按 Ctrl+C 停止服务器")
    
    uvicorn.run(app, host="0.0.0.0", port=8005)