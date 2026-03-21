#!/usr/bin/env python3
"""
立即修复脚本 - 解决上传跳转问题
"""

import os
from pathlib import Path

def create_fix():
    """创建修复文件"""
    
    # 1. 创建修复的HTML（不会跳转）
    html_content = """<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>隐患检测 - 修复版</title>
    <style>
        body { font-family: Arial; padding: 20px; }
        .upload { border: 2px dashed #4CAF50; padding: 30px; text-align: center; margin: 20px 0; }
        .result { background: #f5f5f5; padding: 20px; margin: 20px 0; display: none; }
        .loading { display: none; text-align: center; margin: 20px 0; }
        .error { background: #ffebee; color: #c00; padding: 10px; margin: 10px 0; display: none; }
    </style>
</head>
<body>
    <h1>隐患检测 - 修复版（不跳转）</h1>
    
    <div class="upload">
        <p>选择图片文件：</p>
        <input type="file" id="fileInput" accept="image/*">
        <br><br>
        <button onclick="uploadFile()" id="detectBtn">检测</button>
    </div>
    
    <div class="loading" id="loading">
        检测中，请稍候...
    </div>
    
    <div class="error" id="errorBox"></div>
    
    <div class="result" id="result">
        <h3>检测结果：</h3>
        <pre id="resultJson"></pre>
    </div>
    
    <script>
        function uploadFile() {
            const fileInput = document.getElementById('fileInput');
            const file = fileInput.files[0];
            
            if (!file) {
                showError('请先选择图片文件');
                return;
            }
            
            // 显示加载
            document.getElementById('loading').style.display = 'block';
            document.getElementById('errorBox').style.display = 'none';
            document.getElementById('result').style.display = 'none';
            
            const formData = new FormData();
            formData.append('file', file);
            
            // 关键：使用fetch，不会跳转页面
            fetch('/api/check', {
                method: 'POST',
                body: formData
            })
            .then(response => response.json())
            .then(data => {
                document.getElementById('resultJson').textContent = JSON.stringify(data, null, 2);
                document.getElementById('result').style.display = 'block';
            })
            .catch(error => {
                showError('上传失败: ' + error.message);
            })
            .finally(() => {
                document.getElementById('loading').style.display = 'none';
            });
        }
        
        function showError(message) {
            const errorBox = document.getElementById('errorBox');
            errorBox.textContent = message;
            errorBox.style.display = 'block';
        }
        
        // 测试健康检查
        function testHealth() {
            fetch('/health')
                .then(response => response.json())
                .then(data => {
                    alert('健康检查: ' + JSON.stringify(data));
                });
        }
    </script>
    
    <div style="margin-top: 30px;">
        <button onclick="testHealth()">测试健康检查</button>
        <button onclick="location.reload()">刷新页面</button>
    </div>
</body>
</html>"""
    
    # 保存HTML
    templates_dir = Path("templates")
    templates_dir.mkdir(exist_ok=True)
    
    with open(templates_dir / "fix_now.html", "w", encoding="utf-8") as f:
        f.write(html_content)
    
    # 2. 创建修复的app.py
    app_content = """from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
import uvicorn
import cv2
import numpy as np
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

# 使用修复的检测器
try:
    from detector_fixed import FireExtinguisherDetector
    detector = FireExtinguisherDetector(use_simulation=True)
    logger.info("使用修复版检测器")
except ImportError:
    from detector import FireExtinguisherDetector
    detector = FireExtinguisherDetector()
    logger.info("使用原始检测器")

@app.get("/")
async def home():
    """首页 - 修复版"""
    with open("templates/fix_now.html", "r", encoding="utf-8") as f:
        return HTMLResponse(content=f.read())

@app.post("/api/check")
async def check_fire_extinguisher(file: UploadFile = File(...)):
    """API检测"""
    try:
        contents = await file.read()
        nparr = np.frombuffer(contents, np.uint8)
        image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        if image is None:
            raise HTTPException(status_code=400, detail="无法读取图片")
        
        result = detector.detect(image)
        return result
        
    except Exception as e:
        logger.error(f"检测失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"检测失败: {str(e)}")

@app.get("/health")
async def health_check():
    """健康检查"""
    return {
        "status": "healthy",
        "service": "hazard-detection-fix",
        "version": "1.0.0",
        "fix": "不跳转页面"
    }

if __name__ == "__main__":
    print("启动修复版服务...")
    print("访问: http://localhost:8000")
    print("API: http://localhost:8000/api/check")
    print("健康检查: http://localhost:8000/health")
    uvicorn.run(app, host="0.0.0.0", port=8000)
"""
    
    with open("app_fix.py", "w", encoding="utf-8") as f:
        f.write(app_content)
    
    print("修复文件创建完成！")
    print("1. templates/fix_now.html - 修复的前端（不跳转）")
    print("2. app_fix.py - 修复的后端")
    print("")
    print("启动命令: python app_fix.py")
    print("然后访问: http://localhost:8000")

if __name__ == "__main__":
    create_fix()