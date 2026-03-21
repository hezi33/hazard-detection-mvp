#!/usr/bin/env python3
"""
简化测试服务器 - 无需安装额外依赖
"""

import http.server
import socketserver
import json
import os
import base64
from urllib.parse import urlparse, parse_qs

PORT = 8000

class HazardDetectionHandler(http.server.BaseHTTPRequestHandler):
    """简单的HTTP处理器，模拟检测API"""
    
    def do_GET(self):
        """处理GET请求"""
        if self.path == '/':
            # 返回简单的HTML上传页面
            html = """
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="utf-8">
                <title>隐患检测MVP - 简化测试</title>
                <style>
                    body { font-family: Arial, sans-serif; padding: 20px; max-width: 800px; margin: 0 auto; }
                    .upload-area { border: 2px dashed #ccc; padding: 40px; text-align: center; margin: 20px 0; }
                    .result { background: #f5f5f5; padding: 20px; border-radius: 10px; margin: 20px 0; }
                    pre { white-space: pre-wrap; word-wrap: break-word; }
                </style>
            </head>
            <body>
                <h1>🔥 隐患检测MVP - 简化测试版</h1>
                <p>这是一个简化测试版本，用于验证技术链路。</p>
                
                <div class="upload-area">
                    <h3>上传图片测试</h3>
                    <form action="/api/check" method="POST" enctype="multipart/form-data">
                        <input type="file" name="file" accept="image/*">
                        <br><br>
                        <button type="submit">检测</button>
                    </form>
                </div>
                
                <div class="result">
                    <h4>测试说明：</h4>
                    <p>1. 上传任意图片（系统会模拟检测结果）</p>
                    <p>2. 查看返回的JSON格式</p>
                    <p>3. 验证API接口工作正常</p>
                </div>
                
                <div>
                    <h4>API端点：</h4>
                    <ul>
                        <li><code>GET /</code> - 本页面</li>
                        <li><code>POST /api/check</code> - 检测接口</li>
                        <li><code>GET /health</code> - 健康检查</li>
                        <li><code>GET /test</code> - 测试数据</li>
                    </ul>
                </div>
            </body>
            </html>
            """
            self.send_response(200)
            self.send_header('Content-type', 'text/html; charset=utf-8')
            self.end_headers()
            self.wfile.write(html.encode('utf-8'))
            
        elif self.path == '/health':
            # 健康检查
            response = {
                "status": "healthy",
                "service": "hazard-detection-simple",
                "version": "1.0.0",
                "message": "简化测试服务器运行正常"
            }
            self.send_json(response)
            
        elif self.path == '/test':
            # 测试数据
            response = {
                "success": True,
                "hazard_detected": False,
                "confidence": 0.92,
                "hazard_name": "灭火器压力表正常",
                "reasoning": [
                    "模拟检测到灭火器",
                    "模拟定位压力表区域",
                    "模拟指针角度: 45.0°",
                    "指针位于绿区"
                ],
                "evidence": {
                    "fire_extinguisher_bbox": [100, 150, 300, 400],
                    "gauge_center": [200, 250],
                    "gauge_radius": 45,
                    "pointer_angle": 45.0,
                    "zone": "green"
                },
                "note": "这是模拟数据，用于验证API格式"
            }
            self.send_json(response)
            
        else:
            self.send_error(404, "页面不存在")
    
    def do_POST(self):
        """处理POST请求"""
        if self.path == '/api/check':
            # 模拟检测API
            content_length = int(self.headers.get('Content-Length', 0))
            
            # 读取请求体（在实际应用中会解析multipart/form-data）
            # 这里简化处理，直接返回模拟结果
            
            # 随机生成检测结果（50%概率检测到隐患）
            import random
            hazard_detected = random.random() > 0.5
            zone = "red" if hazard_detected else "green"
            
            response = {
                "success": True,
                "hazard_detected": hazard_detected,
                "confidence": round(random.uniform(0.7, 0.95), 2),
                "hazard_name": "灭火器压力表异常" if hazard_detected else "灭火器压力表正常",
                "reasoning": [
                    f"模拟检测到灭火器 (置信度: {round(random.uniform(0.8, 0.98), 2)})",
                    "模拟定位压力表区域",
                    f"模拟指针角度: {random.randint(0, 360)}°",
                    f"指针位于{zone}区"
                ],
                "evidence": {
                    "fire_extinguisher_bbox": [
                        random.randint(50, 200),
                        random.randint(50, 200),
                        random.randint(300, 500),
                        random.randint(300, 500)
                    ],
                    "gauge_center": [random.randint(150, 250), random.randint(150, 250)],
                    "gauge_radius": random.randint(30, 60),
                    "pointer_angle": random.randint(0, 360),
                    "zone": zone
                },
                "note": "这是模拟数据，验证API格式和流程"
            }
            
            self.send_json(response)
        else:
            self.send_error(404, "API不存在")
    
    def send_json(self, data):
        """发送JSON响应"""
        self.send_response(200)
        self.send_header('Content-type', 'application/json; charset=utf-8')
        self.end_headers()
        self.wfile.write(json.dumps(data, ensure_ascii=False, indent=2).encode('utf-8'))
    
    def log_message(self, format, *args):
        """简化日志输出"""
        print(f"[{self.log_date_time_string()}] {format % args}")

def main():
    """启动服务器"""
    print(f"🚀 启动简化测试服务器...")
    print(f"📡 访问地址: http://localhost:{PORT}")
    print(f"🔧 API端点: http://localhost:{PORT}/api/check")
    print(f"💚 健康检查: http://localhost:{PORT}/health")
    print(f"📋 测试数据: http://localhost:{PORT}/test")
    print("\n按 Ctrl+C 停止服务器")
    
    with socketserver.TCPServer(("", PORT), HazardDetectionHandler) as httpd:
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n🛑 服务器已停止")

if __name__ == "__main__":
    main()