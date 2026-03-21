from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pathlib import Path
import uvicorn
import cv2
import numpy as np
import logging
import json
from detector import FireExtinguisherDetector

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 创建应用
app = FastAPI(
    title="Hazard Detection MVP",
    version="1.0.0",
    description="灭火器压力表检测系统 - MVP验证版本"
)

# 创建目录
Path("static").mkdir(exist_ok=True)
Path("uploads").mkdir(exist_ok=True)

# 挂载静态文件
app.mount("/static", StaticFiles(directory="static"), name="static")

# 初始化检测器
detector = FireExtinguisherDetector()

@app.get("/", response_class=HTMLResponse)
async def home():
    """首页 - 上传页面"""
    # 使用修复后的HTML
    try:
        with open("templates/fixed_index.html", "r", encoding="utf-8") as f:
            return HTMLResponse(content=f.read())
    except FileNotFoundError:
        # 如果修复文件不存在，使用原始文件
        with open("templates/index.html", "r", encoding="utf-8") as f:
            return HTMLResponse(content=f.read())

@app.post("/api/check")
async def check_fire_extinguisher(file: UploadFile = File(...)):
    """API端点：检测灭火器压力表"""
    try:
        # 读取图片
        contents = await file.read()
        nparr = np.frombuffer(contents, np.uint8)
        image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        if image is None:
            raise HTTPException(status_code=400, detail="无法读取图片")
        
        # 检测
        result = detector.detect(image)
        
        return JSONResponse(content=result)
        
    except Exception as e:
        logger.error(f"检测失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"检测失败: {str(e)}")

@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    """上传文件并检测（返回HTML结果）"""
    try:
        # 读取图片
        contents = await file.read()
        nparr = np.frombuffer(contents, np.uint8)
        image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        if image is None:
            return HTMLResponse(content="<h3>错误：无法读取图片</h3>")
        
        # 检测
        result = detector.detect(image)
        
        # 格式化JSON
        formatted_json = json.dumps(result, ensure_ascii=False, indent=2)
        
        # 生成结果HTML
        html_result = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>检测结果</title>
            <style>
                body {{ font-family: Arial, sans-serif; padding: 20px; }}
                .result {{ background: #f5f5f5; padding: 20px; border-radius: 10px; }}
                pre {{ white-space: pre-wrap; word-wrap: break-word; }}
                .back {{ margin-top: 20px; }}
            </style>
        </head>
        <body>
            <h3>检测结果</h3>
            <div class="result">
                <pre>{formatted_json}</pre>
            </div>
            <div class="back">
                <a href="/">返回上传</a>
            </div>
        </body>
        </html>
        """
        
        return HTMLResponse(content=html_result)
        
    except Exception as e:
        return HTMLResponse(content=f"<h3>错误：{str(e)}</h3><p><a href='/'>返回</a></p>")

@app.get("/health")
async def health_check():
    """健康检查"""
    return {"status": "healthy", "service": "hazard-detection-mvp", "version": "1.0.0"}

@app.get("/test")
async def test_endpoint():
    """测试端点"""
    return {
        "message": "服务运行正常",
        "endpoints": {
            "GET /": "Web上传界面",
            "POST /api/check": "API检测接口",
            "POST /upload": "表单上传接口",
            "GET /health": "健康检查",
            "GET /test": "测试端点"
        }
    }

if __name__ == "__main__":
    print("🚀 启动隐患检测MVP服务...")
    print("📡 访问地址: http://localhost:8000")
    print("🔧 API端点: http://localhost:8000/api/check")
    print("💚 健康检查: http://localhost:8000/health")
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")