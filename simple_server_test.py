#!/usr/bin/env python3
"""
最简单的测试服务器 - 排除复杂代码问题
"""

from fastapi import FastAPI, File, UploadFile
from fastapi.responses import HTMLResponse, JSONResponse
import uvicorn

app = FastAPI()

# 简单主页
@app.get("/")
async def home():
    html = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>简单上传测试</title>
        <style>
            body { font-family: Arial; padding: 20px; }
            #preview { max-width: 400px; margin-top: 20px; }
        </style>
    </head>
    <body>
        <h1>简单文件上传测试</h1>
        <p>如果这个能工作，说明FastAPI基础功能正常。</p>
        
        <input type="file" id="fileInput" accept="image/*">
        <button onclick="uploadFile()">上传测试</button>
        
        <div id="result"></div>
        <img id="preview" src="" alt="预览">
        
        <script>
            async function uploadFile() {
                const fileInput = document.getElementById('fileInput');
                if (!fileInput.files[0]) {
                    alert('请先选择文件');
                    return;
                }
                
                const formData = new FormData();
                formData.append('file', fileInput.files[0]);
                
                try {
                    const response = await fetch('/api/simple_upload', {
                        method: 'POST',
                        body: formData
                    });
                    
                    const result = await response.json();
                    document.getElementById('result').innerHTML = 
                        `<pre>${JSON.stringify(result, null, 2)}</pre>`;
                    
                    if (result.image_preview) {
                        document.getElementById('preview').src = result.image_preview;
                    }
                    
                } catch (error) {
                    document.getElementById('result').innerHTML = 
                        `<div style="color: red;">错误: ${error}</div>`;
                }
            }
            
            // 文件选择时预览
            document.getElementById('fileInput').addEventListener('change', function(e) {
                const file = e.target.files[0];
                if (file) {
                    const reader = new FileReader();
                    reader.onload = function(e) {
                        document.getElementById('preview').src = e.target.result;
                    };
                    reader.readAsDataURL(file);
                }
            });
        </script>
    </body>
    </html>
    """
    return HTMLResponse(content=html)

# 简单上传API
@app.post("/api/simple_upload")
async def simple_upload(file: UploadFile = File(...)):
    """最简单的上传测试"""
    try:
        # 读取文件
        contents = await file.read()
        
        return {
            "success": True,
            "filename": file.filename,
            "content_type": file.content_type,
            "size_bytes": len(contents),
            "message": "文件上传成功！",
            "image_preview": f"data:{file.content_type};base64,{contents.hex()[:100]}..."  # 简化
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

@app.get("/health")
async def health():
    return {"status": "healthy", "service": "simple-test"}

if __name__ == "__main__":
    print("🚀 启动简单测试服务器")
    print("📡 访问: http://localhost:8006")
    print("🔧 这个服务器只测试基本功能")
    uvicorn.run(app, host="0.0.0.0", port=8006)