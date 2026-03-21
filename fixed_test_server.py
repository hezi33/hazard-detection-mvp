#!/usr/bin/env python3
"""
修复的测试服务器 - 正确处理文件上传
"""

from http.server import HTTPServer, BaseHTTPRequestHandler
import json
import urllib.parse
import cgi
import random

PORT = 8001  # 使用8001端口，避免冲突

class FixedHazardDetectionHandler(BaseHTTPRequestHandler):
    """修复的HTTP处理器，能正确处理文件上传"""
    
    def do_GET(self):
        """处理GET请求"""
        if self.path == '/':
            self.send_html_response()
        elif self.path == '/health':
            self.send_json_response({
                "status": "healthy",
                "service": "hazard-detection-fixed",
                "version": "1.0.0"
            })
        elif self.path == '/test':
            self.send_test_response()
        else:
            self.send_error(404, "页面不存在")
    
    def do_POST(self):
        """处理POST请求 - 正确处理文件上传"""
        if self.path == '/api/check':
            try:
                # 解析multipart/form-data
                content_type = self.headers.get('content-type')
                
                if not content_type or 'multipart/form-data' not in content_type:
                    self.send_json_response({
                        "success": False,
                        "message": "需要multipart/form-data格式"
                    }, status=400)
                    return
                
                # 使用cgi解析表单数据
                form = cgi.FieldStorage(
                    fp=self.rfile,
                    headers=self.headers,
                    environ={'REQUEST_METHOD': 'POST',
                            'CONTENT_TYPE': self.headers['Content-Type']}
                )
                
                # 检查是否有文件
                if 'file' not in form:
                    self.send_json_response({
                        "success": False,
                        "message": "没有上传文件"
                    }, status=400)
                    return
                
                file_item = form['file']
                
                # 检查是否是文件
                if not file_item.filename:
                    self.send_json_response({
                        "success": False,
                        "message": "上传的不是文件"
                    }, status=400)
                    return
                
                # 读取文件内容（在实际应用中会处理图片）
                # 这里简化处理，只获取文件名
                filename = file_item.filename
                file_size = 0
                if hasattr(file_item, 'file'):
                    file_item.file.seek(0, 2)  # 跳到文件末尾
                    file_size = file_item.file.tell()
                    file_item.file.seek(0)  # 回到文件开头
                
                # 生成模拟检测结果
                result = self.generate_detection_result(filename, file_size)
                self.send_json_response(result)
                
            except Exception as e:
                self.send_json_response({
                    "success": False,
                    "message": f"处理请求时出错: {str(e)}"
                }, status=500)
        else:
            self.send_error(404, "API不存在")
    
    def generate_detection_result(self, filename, file_size):
        """生成模拟检测结果"""
        import random
        
        # 随机决定是否有隐患
        hazard_detected = random.random() > 0.5
        zone = "red" if hazard_detected else "green"
        
        return {
            "success": True,
            "hazard_detected": hazard_detected,
            "confidence": round(random.uniform(0.7, 0.95), 2),
            "hazard_name": "灭火器压力表异常" if hazard_detected else "灭火器压力表正常",
            "reasoning": [
                f"收到文件: {filename} ({file_size} bytes)",
                "模拟检测到灭火器",
                "模拟定位压力表区域",
                f"模拟指针角度: {random.randint(0, 360)}°",
                f"指针位于{zone}区"
            ],
            "evidence": {
                "filename": filename,
                "file_size": file_size,
                "detection_time": "模拟数据",
                "zone": zone
            },
            "note": "这是模拟数据，验证API格式和流程"
        }
    
    def send_test_response(self):
        """发送测试响应"""
        self.send_json_response({
            "success": True,
            "hazard_detected": False,
            "confidence": 0.92,
            "hazard_name": "灭火器压力表正常",
            "reasoning": [
                "测试数据：模拟检测到灭火器",
                "测试数据：模拟定位压力表区域",
                "测试数据：模拟指针角度: 45.0°",
                "测试数据：指针位于绿区"
            ],
            "evidence": {
                "test_mode": True,
                "zone": "green"
            }
        })
    
    def send_html_response(self):
        """发送HTML页面"""
        html = """<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>隐患检测MVP - 修复测试版</title>
    <style>
        body { font-family: Arial, sans-serif; padding: 20px; max-width: 800px; margin: 0 auto; }
        .upload-area { border: 2px dashed #4CAF50; padding: 40px; text-align: center; margin: 20px 0; background: #f9f9f9; }
        .result { background: #f5f5f5; padding: 20px; border-radius: 10px; margin: 20px 0; }
        pre { white-space: pre-wrap; word-wrap: break-word; background: white; padding: 15px; border-radius: 5px; }
        button { background: #4CAF50; color: white; border: none; padding: 10px 20px; border-radius: 5px; cursor: pointer; }
        button:hover { background: #45a049; }
    </style>
</head>
<body>
    <h1>🔥 隐患检测MVP - 修复测试版</h1>
    <p>这个版本能正确处理文件上传。</p>
    
    <div class="upload-area">
        <h3>上传图片测试</h3>
        <form action="/api/check" method="POST" enctype="multipart/form-data" id="uploadForm">
            <input type="file" name="file" accept="image/*" id="fileInput" required>
            <br><br>
            <button type="submit" id="submitBtn">检测</button>
        </form>
        <div id="result" class="result" style="display: none;">
            <h4>检测结果：</h4>
            <pre id="resultJson"></pre>
        </div>
    </div>
    
    <div>
        <h4>测试说明：</h4>
        <p>1. 选择任意图片文件</p>
        <p>2. 点击"检测"按钮</p>
        <p>3. 查看JSON格式的检测结果</p>
        <p>4. 验证API接口工作正常</p>
    </div>
    
    <div>
        <h4>其他测试：</h4>
        <button onclick="testHealth()">测试健康检查</button>
        <button onclick="testAPI()">测试API（模拟）</button>
    </div>
    
    <script>
        document.getElementById('uploadForm').onsubmit = async function(e) {
            e.preventDefault();
            
            const formData = new FormData(this);
            const submitBtn = document.getElementById('submitBtn');
            const resultDiv = document.getElementById('result');
            const resultJson = document.getElementById('resultJson');
            
            submitBtn.disabled = true;
            submitBtn.textContent = '检测中...';
            resultDiv.style.display = 'none';
            
            try {
                const response = await fetch('/api/check', {
                    method: 'POST',
                    body: formData
                });
                
                const data = await response.json();
                resultJson.textContent = JSON.stringify(data, null, 2);
                resultDiv.style.display = 'block';
                
            } catch (error) {
                resultJson.textContent = '错误: ' + error.message;
                resultDiv.style.display = 'block';
            } finally {
                submitBtn.disabled = false;
                submitBtn.textContent = '检测';
            }
        };
        
        async function testHealth() {
            const response = await fetch('/health');
            const data = await response.json();
            alert('健康检查: ' + JSON.stringify(data, null, 2));
        }
        
        async function testAPI() {
            const response = await fetch('/test');
            const data = await response.json();
            alert('测试API: ' + JSON.stringify(data, null, 2));
        }
    </script>
</body>
</html>"""
        
        self.send_response(200)
        self.send_header('Content-type', 'text/html; charset=utf-8')
        self.send_header('Content-Length', str(len(html)))
        self.end_headers()
        self.wfile.write(html.encode('utf-8'))
    
    def send_json_response(self, data, status=200):
        """发送JSON响应"""
        json_data = json.dumps(data, ensure_ascii=False, indent=2)
        
        self.send_response(status)
        self.send_header('Content-type', 'application/json; charset=utf-8')
        self.send_header('Content-Length', str(len(json_data)))
        self.end_headers()
        self.wfile.write(json_data.encode('utf-8'))
    
    def log_message(self, format, *args):
        """简化日志输出"""
        print(f"[{self.log_date_time_string()}] {format % args}")

def main():
    """启动服务器"""
    print(f"🚀 启动修复测试服务器...")
    print(f"📡 访问地址: http://localhost:{PORT}")
    print(f"🔧 API端点: POST http://localhost:{PORT}/api/check")
    print(f"💚 健康检查: GET http://localhost:{PORT}/health")
    print(f"📋 测试数据: GET http://localhost:{PORT}/test")
    print("\n按 Ctrl+C 停止服务器")
    
    server = HTTPServer(('', PORT), FixedHazardDetectionHandler)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n🛑 服务器已停止")

if __name__ == "__main__":
    main()