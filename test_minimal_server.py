#!/usr/bin/env python3
"""
最小化测试服务器 - 独立运行
"""

from fastapi import FastAPI
from fastapi.responses import HTMLResponse
import uvicorn

app = FastAPI()

@app.get("/")
async def minimal_test():
    """最小化测试页面"""
    html = """
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <title>文件读取测试</title>
        <style>
            body { font-family: Arial; padding: 20px; }
            #status { margin: 20px 0; padding: 10px; background: #f0f0f0; }
            #preview { max-width: 400px; border: 1px solid #ccc; margin-top: 10px; }
            .success { color: green; }
            .error { color: red; }
        </style>
    </head>
    <body>
        <h1>文件读取功能测试</h1>
        <p>测试浏览器File API是否工作正常。</p>
        
        <input type="file" id="fileInput" accept="image/*">
        <button onclick="testRead()">测试读取</button>
        
        <div id="status">状态: 等待测试</div>
        <img id="preview" src="" alt="预览">
        
        <script>
            function testRead() {
                const fileInput = document.getElementById('fileInput');
                const status = document.getElementById('status');
                const preview = document.getElementById('preview');
                
                // 检查文件
                if (!fileInput.files || fileInput.files.length === 0) {
                    status.innerHTML = '<span class="error">❌ 请先选择文件</span>';
                    return;
                }
                
                const file = fileInput.files[0];
                console.log('文件信息:', file.name, file.type, file.size + ' bytes');
                
                // 验证文件类型
                if (!file.type.startsWith('image/')) {
                    status.innerHTML = `<span class="error">❌ 请选择图片文件 (当前: ${file.type})</span>`;
                    return;
                }
                
                status.innerHTML = `📁 文件: <strong>${file.name}</strong><br>
                                    类型: ${file.type}<br>
                                    大小: ${file.size} bytes`;
                
                // 使用FileReader
                const reader = new FileReader();
                
                reader.onloadstart = function() {
                    console.log('FileReader: 开始读取');
                    status.innerHTML += '<br>🔄 读取中...';
                };
                
                reader.onprogress = function(e) {
                    if (e.lengthComputable) {
                        const percent = Math.round((e.loaded / e.total) * 100);
                        console.log(`读取进度: ${percent}%`);
                    }
                };
                
                reader.onload = function(e) {
                    console.log('✅ FileReader: 读取成功');
                    console.log('数据长度:', e.target.result.length);
                    
                    // 显示图片
                    preview.src = e.target.result;
                    
                    // 检查图片加载
                    preview.onload = function() {
                        status.innerHTML += `<br><span class="success">✅ 图片加载成功: ${preview.naturalWidth}×${preview.naturalHeight}</span>`;
                    };
                    
                    preview.onerror = function() {
                        status.innerHTML += '<br><span class="error">❌ 图片显示失败</span>';
                    };
                };
                
                reader.onerror = function(e) {
                    console.error('❌ FileReader错误:', e.target.error);
                    status.innerHTML += `<br><span class="error">❌ 读取失败: ${e.target.error.message}</span>`;
                };
                
                reader.onabort = function() {
                    console.warn('FileReader被取消');
                    status.innerHTML += '<br>⚠️ 读取被取消';
                };
                
                // 开始读取
                reader.readAsDataURL(file);
            }
            
            // 页面加载完成
            document.addEventListener('DOMContentLoaded', function() {
                console.log('✅ 页面加载完成');
                console.log('FileReader可用:', typeof FileReader !== 'undefined');
                console.log('File API可用:', typeof File !== 'undefined');
                console.log('浏览器:', navigator.userAgent);
                
                // 自动测试小文件
                setTimeout(autoTest, 1000);
            });
            
            function autoTest() {
                console.log('尝试自动测试...');
                // 可以在这里添加自动测试逻辑
            }
        </script>
    </body>
    </html>
    """
    return HTMLResponse(content=html)

@app.get("/health")
async def health():
    return {"status": "healthy", "service": "minimal-test"}

if __name__ == "__main__":
    print("🚀 启动最小化测试服务器")
    print("📡 访问: http://localhost:8007")
    print("🔧 测试文件读取基本功能")
    print("\n按 Ctrl+C 停止")
    uvicorn.run(app, host="0.0.0.0", port=8007)