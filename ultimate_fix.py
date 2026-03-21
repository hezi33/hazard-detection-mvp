#!/usr/bin/env python3
"""
终极修复版本 - 确保上传后不跳转页面
"""

import os
import json
from pathlib import Path

def create_ultimate_fix():
    """创建终极修复文件"""
    
    # 1. 创建不会跳转的HTML
    html_content = """<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>隐患检测MVP - 终极修复版</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: Arial, sans-serif; padding: 20px; background: #f5f5f5; }
        .container { max-width: 800px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; box-shadow: 0 5px 15px rgba(0,0,0,0.1); }
        h1 { color: #333; margin-bottom: 20px; text-align: center; }
        .upload-area { border: 3px dashed #4CAF50; padding: 40px; text-align: center; margin: 20px 0; border-radius: 10px; cursor: pointer; }
        .upload-area:hover { background: #f9f9f9; }
        .preview { margin: 20px 0; text-align: center; }
        .preview img { max-width: 100%; max-height: 300px; border-radius: 5px; }
        .btn { background: #4CAF50; color: white; border: none; padding: 12px 30px; border-radius: 5px; cursor: pointer; font-size: 16px; margin: 10px; }
        .btn:hover { background: #45a049; }
        .btn:disabled { background: #cccccc; cursor: not-allowed; }
        .result { background: #f9f9f9; padding: 20px; border-radius: 10px; margin: 20px 0; display: none; }
        .loading { display: none; text-align: center; margin: 20px 0; }
        .spinner { border: 4px solid #f3f3f3; border-top: 4px solid #4CAF50; border-radius: 50%; width: 40px; height: 40px; animation: spin 1s linear infinite; margin: 0 auto 10px; }
        @keyframes spin { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }
        .error { background: #ffebee; color: #c62828; padding: 15px; border-radius: 5px; margin: 10px 0; display: none; }
        .success { background: #e8f5e9; color: #2e7d32; padding: 15px; border-radius: 5px; margin: 10px 0; display: none; }
        pre { background: white; padding: 15px; border-radius: 5px; overflow-x: auto; font-family: monospace; }
    </style>
</head>
<body>
    <div class="container">
        <h1>🔥 隐患检测MVP - 终极修复版</h1>
        <p style="text-align: center; color: #666; margin-bottom: 20px;">上传后不会跳转页面，直接显示结果</p>
        
        <!-- 上传区域 -->
        <div class="upload-area" id="uploadArea">
            <div style="font-size: 48px; margin-bottom: 20px;">📤</div>
            <div style="font-size: 18px; margin-bottom: 10px;">点击选择图片或拖拽到此处</div>
            <p style="color: #888; margin-bottom: 20px;">支持 JPG、PNG 格式</p>
            
            <!-- 注意：这里没有form标签！ -->
            <input type="file" id="fileInput" accept="image/*" style="display: none;">
            <button class="btn" onclick="document.getElementById('fileInput').click()">选择图片</button>
            <button class="btn" id="detectBtn" disabled onclick="uploadAndDetect()">检测</button>
        </div>
        
        <!-- 加载中 -->
        <div class="loading" id="loading">
            <div class="spinner"></div>
            <p>正在检测中，请稍候...</p>
        </div>
        
        <!-- 错误提示 -->
        <div class="error" id="errorBox">
            <strong>错误：</strong><span id="errorMessage"></span>
        </div>
        
        <!-- 成功提示 -->
        <div class="success" id="successBox">
            <strong>成功：</strong><span id="successMessage"></span>
        </div>
        
        <!-- 图片预览 -->
        <div class="preview" id="preview"></div>
        
        <!-- 结果展示 -->
        <div class="result" id="result">
            <h3>检测结果</h3>
            <pre id="resultJson"></pre>
        </div>
        
        <!-- 测试按钮 -->
        <div style="text-align: center; margin-top: 30px;">
            <button class="btn" onclick="testHealth()" style="background: #2196F3;">测试健康检查</button>
            <button class="btn" onclick="testAPI()" style="background: #FF9800;">测试API</button>
            <button class="btn" onclick="resetForm()" style="background: #9E9E9E;">重置</button>
        </div>
    </div>
    
    <script>
        // 全局变量
        let selectedFile = null;
        
        // DOM元素
        const fileInput = document.getElementById('fileInput');
        const detectBtn = document.getElementById('detectBtn');
        const preview = document.getElementById('preview');
        const result = document.getElementById('result');
        const resultJson = document.getElementById('resultJson');
        const loading = document.getElementById('loading');
        const errorBox = document.getElementById('errorBox');
        const errorMessage = document.getElementById('errorMessage');
        const successBox = document.getElementById('successBox');
        const successMessage = document.getElementById('successMessage');
        
        // 文件选择事件
        fileInput.addEventListener('change', function() {
            if (this.files.length > 0) {
                handleFileSelect(this.files[0]);
            }
        });
        
        // 拖拽功能
        const uploadArea = document.getElementById('uploadArea');
        
        ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
            uploadArea.addEventListener(eventName, preventDefaults, false);
        });
        
        function preventDefaults(e) {
            e.preventDefault();
            e.stopPropagation();
        }
        
        ['dragenter', 'dragover'].forEach(eventName => {
            uploadArea.addEventListener(eventName, () => {
                uploadArea.style.background = '#f0f9ff';
                uploadArea.style.borderColor = '#2196F3';
            }, false);
        });
        
        ['dragleave', 'drop'].forEach(eventName => {
            uploadArea.addEventListener(eventName, () => {
                uploadArea.style.background = '';
                uploadArea.style.borderColor = '#4CAF50';
            }, false);
        });
        
        uploadArea.addEventListener('drop', handleDrop, false);
        
        function handleDrop(e) {
            const dt = e.dataTransfer;
            const files = dt.files;
            if (files.length > 0) {
                handleFileSelect(files[0]);
            }
        }
        
        function handleFileSelect(file) {
            // 验证文件类型
            if (!file.type.match('image.*')) {
                showError('请选择图片文件（JPG、PNG）');
                return;
            }
            
            selectedFile = file;
            
            // 显示预览
            const reader = new FileReader();
            reader.onload = function(e) {
                preview.innerHTML = `<img src="${e.target.result}" alt="预览" style="max-width: 100%; max-height: 300px;">`;
                detectBtn.disabled = false;
                detectBtn.textContent = '检测';
                
                // 隐藏之前的结果和错误
                result.style.display = 'none';
                errorBox.style.display = 'none';
                successBox.style.display = 'none';
            };
            reader.readAsDataURL(file);
        }
        
        function uploadAndDetect() {
            if (!selectedFile) {
                showError('请先选择图片');
                return;
            }
            
            // 显示加载中
            loading.style.display = 'block';
            result.style.display = 'none';
            errorBox.style.display = 'none';
            successBox.style.display = 'none';
            detectBtn.disabled = true;
            detectBtn.textContent = '检测中...';
            
            // 创建FormData
            const formData = new FormData();
            formData.append('file', selectedFile);
            
            // 使用Fetch API发送请求（关键：不会跳转页面）
            fetch('/api/check', {
                method: 'POST',
                body: formData
            })
            .then(response => {
                if (!response.ok) {
                    throw new Error(`HTTP错误: ${response.status}`);
                }
                return response.json();
            })
            .then(data => {
                displayResult(data);
                showSuccess('检测完成！');
            })
            .catch(error => {
                showError('上传失败: ' + error.message);
            })
            .finally(() => {
                loading.style.display = 'none';
                detectBtn.disabled = false;
                detectBtn.textContent = '检测';
            });
        }
        
        function displayResult(data) {
            // 格式化JSON
            resultJson.textContent = JSON.stringify(data, null, 2);
            
            // 显示结果区域
            result.style.display = 'block';
            
            // 滚动到结果
            result.scrollIntoView({ behavior: 'smooth' });
        }
        
        function showError(message) {
            errorMessage.textContent = message;
            errorBox.style.display = 'block';
            errorBox.scrollIntoView({ behavior: 'smooth' });
        }
        
        function showSuccess(message) {
            successMessage.textContent = message;
            successBox.style.display = 'block';
        }
        
        function testHealth() {
            fetch('/health')
                .then(response => response.json())
                .then(data => {
                    alert('健康检查成功:\\n' + JSON.stringify(data, null, 2));
                })
                .catch(error => {
                    alert('健康检查失败: ' + error.message);
                });
        }
        
        function testAPI() {
            // 创建测试文件
            const blob = new Blob(['test'], { type: 'text/plain' });
            const testFile = new File([blob], 'test.txt', { type: 'text/plain' });
            
            selectedFile = testFile;
            uploadAndDetect();
        }
        
        function resetForm() {
            fileInput.value = '';
            selectedFile = null;
            preview.innerHTML = '';
            result.style.display = 'none';
            errorBox.style.display = 'none';
            successBox.style.display = 'none';
            detectBtn.disabled = true;
            detectBtn.textContent = '检测';
        }
        
        // 页面加载完成后的初始化
        document.addEventListener('DOMContentLoaded', function() {
            console.log('终极修复版已加载 - 不会跳转页面');
        });
    </script>
</body>
</html>"""
    
    # 保存HTML文件
    with open("templates/ultimate_fix.html", "w", encoding="utf-8") as f:
        f.write(html_content)
    
    # 2. 创建修复的app.py
    app_content = """from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pathlib import Path
import uvicorn
import cv2
import numpy as np
import logging
import json

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 创建应用
app = FastAPI(
    title="Hazard Detection MVP - 终极修复版",
    version="2.0.0",
    description="灭火器压力表检测系统 - 不会跳转页面"
)

# 创建目录
Path("static").mkdir(exist_ok=True)
Path("uploads").mkdir(exist_ok=True)

# 挂载静态文件
app.mount("/static", StaticFiles(directory="static"), name="static")

# 初始化检测器 - 使用修复版本避免YOLO下载问题
try:
    from detector_fixed import FireExtinguisherDetector
    # 使用模拟模式（避免YOLO下载问题）
    detector = FireExtinguisherDetector(use_simulation=True)
    logger.info("使用修复版检测器（模拟模式）")
except ImportError:
    # 回退到原始检测器
    from detector import FireExtinguisherDetector
    detector = FireExtinguisherDetector()
    logger.info("使用原始检测器")

@app.get("/", response_class=HTMLResponse)
async def home():
    """首页 - 使用终极修复版HTML"""
    try:
        with open("templates/ultimate_fix.html", "r", encoding="utf-8") as f:
            return HTMLResponse(content=f.read())
    except FileNotFoundError:
        # 如果修复文件不存在，使用fixed版本
        try:
            with open("templates/fixed_index.html", "r", encoding="utf-8") as f:
                return HTMLResponse(content=f.read())
        except FileNotFoundError:
            # 最后使用原始版本
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
        
        # 添加调试信息
        result["debug"] = {
            "filename": file.filename,
            "content_type": file.content_type,
            "file_size": len(contents),
            "api_version": "2.0.0"
        }
        
        return JSONResponse(content=result)
        
    except Exception as e:
        logger.error(f"检测失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"检测失败: {str(e)}")

@app.get("/health")
async def health_check():
    """健康检查"""
    return {
        "status": "healthy", 
        "service": "hazard-detection-mvp-ultimate",
        "version": "2.0.0",
        "fix": "不会跳转页面"
    }

@app.get("/test")
async def test_endpoint():
    """测试端点"""
    return {
        "message": "终极修复版运行正常",
        "features": [
            "不会跳转页面",
            "AJAX异步请求",
            "模拟模式支持",
            "完整错误处理"
        ],
        "endpoints": {
            "GET /": "终极修复版界面",
            "POST /api/check": "API检测接口",
            "GET /health": "健康检查",
            "GET /test": "测试端点"
        }
    }

if __name__ == "__main__":
    print("🚀 启动隐患检测MVP - 终极修复版...")
    print("📡 访问地址: http://localhost:8000")
    print("🔧 API端点: http://localhost:8000/api/check")
    print("💚 健康检查: http://localhost:8000/health")
    print("🎯 修复特性: 上传后不会跳转页面！")
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")
"""
    
    # 保存app.py
    with open("app_ultimate.py", "w", encoding="utf-8") as f:
        f.write(app_content)
    
    # 3. 创建启动脚本
    start_script = """#!/bin/bash
# 终极修复版启动脚本

echo "🚀 启动隐患检测MVP - 终极修复版"
echo "========================================"

# 检查Python
if ! command -v python3 &> /dev/null; then
    echo "❌ 未找到Python3，请先安装Python3"
    exit 1
fi

# 检查依赖
echo "📦 检查依赖..."
if [ ! -f "requirements.txt" ]; then
    echo "⚠️  requirements.txt 不存在，跳过依赖检查"
else
    echo "✅ requirements.txt 存在"
fi

# 启动服务
echo "🚀 启动服务..."
echo "📡 访问地址: http://localhost:8000"
echo "🔧 API端点: http://localhost:8000/api/check"
echo "💚 健康检查: http://localhost:8000/health"
echo "🎯 修复特性: 上传后不会跳转页面！"
echo ""
echo "按 Ctrl+C 停止服务"
echo "========================================"

python3 app_ultimate.py
"""
    
    with open("start_ultimate.sh", "w", encoding="utf-8") as f:
        f.write(start_script)
    
    # 设置执行权限
    os.chmod("start_ultimate.sh", 0o755)
    
    print("✅ 终极修复版创建完成！")
    print("📁