# 最简单的测试服务器
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
import uvicorn

app = FastAPI()

@app.get("/")
async def home():
    html = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>简单文件读取测试</title>
        <style>
            body { font-family: Arial; padding: 20px; }
            #preview { max-width: 400px; border: 1px solid #ccc; margin-top: 10px; }
            .status { margin: 10px 0; padding: 10px; }
            .success { background: #d4edda; color: #155724; }
            .error { background: #f8d7da; color: #721c24; }
        </style>
    </head>
    <body>
        <h1>简单文件读取测试</h1>
        <p>测试浏览器FileReader API是否工作。</p>
        
        <input type="file" id="fileInput" accept="image/*">
        <button onclick="testRead()">测试读取</button>
        
        <div id="status" class="status">状态: 等待测试</div>
        <img id="preview" src="" alt="预览">
        
        <script>
            function testRead() {
                const fileInput = document.getElementById('fileInput');
                const status = document.getElementById('status');
                const preview = document.getElementById('preview');
                
                if (!fileInput.files || fileInput.files.length === 0) {
                    status.innerHTML = '<span class="error">请先选择文件</span>';
                    return;
                }
                
                const file = fileInput.files[0];
                console.log('测试文件:', file.name, file.type, file.size);
                
                const reader = new FileReader();
                
                reader.onload = function(e) {
                    preview.src = e.target.result;
                    status.innerHTML = '<span class="success">✅ 文件读取成功！图片已显示</span>';
                    console.log('FileReader成功');
                };
                
                reader.onerror = function(e) {
                    status.innerHTML = '<span class="error">❌ 文件读取失败</span>';
                    console.error('FileReader错误:', e.target.error);
                };
                
                reader.readAsDataURL(file);
            }
            
            // 页面加载日志
            console.log('测试页面加载完成');
            console.log('浏览器:', navigator.userAgent);
        </script>
    </body>
    </html>
    """
    return HTMLResponse(content=html)

@app.get("/health")
async def health():
    return {"status": "healthy", "service": "simple-test"}

if __name__ == "__main__":
    print("启动简单测试服务器...")
    print("访问: http://localhost:8008")
    print("按 Ctrl+C 停止")
    uvicorn.run(app, host="0.0.0.0", port=8008)