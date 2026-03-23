#!/usr/bin/env python3
"""
调试版真实算法服务器 - 打印完整数据结构
"""

from fastapi import FastAPI, File, UploadFile
from fastapi.responses import HTMLResponse, JSONResponse
import uvicorn
import cv2
import numpy as np
import json
import base64
import traceback

app = FastAPI()

def convert_numpy_types(obj):
    """递归转换NumPy类型为Python原生类型"""
    if isinstance(obj, dict):
        return {key: convert_numpy_types(value) for key, value in obj.items()}
    elif isinstance(obj, list):
        return [convert_numpy_types(item) for item in obj]
    elif isinstance(obj, np.integer):
        return int(obj)
    elif isinstance(obj, np.floating):
        return float(obj)
    elif isinstance(obj, np.ndarray):
        return obj.tolist()
    else:
        return obj

@app.get("/")
async def home():
    html = """
    <!DOCTYPE html>
    <html>
    <head><title>调试服务器</title></head>
    <body>
        <h1>调试真实算法服务器</h1>
        <input type="file" id="fileInput" accept="image/*">
        <button onclick="upload()">上传调试</button>
        <div id="result"></div>
        <script>
            async function upload() {
                const file = document.getElementById('fileInput').files[0];
                const formData = new FormData();
                formData.append('file', file);
                
                const response = await fetch('/api/debug', {
                    method: 'POST',
                    body: formData
                });
                const data = await response.json();
                document.getElementById('result').innerHTML = 
                    '<pre>' + JSON.stringify(data, null, 2) + '</pre>';
            }
        </script>
    </body>
    </html>
    """
    return HTMLResponse(content=html)

@app.post("/api/debug")
async def debug_check(file: UploadFile = File(...)):
    try:
        # 读取图片
        contents = await file.read()
        nparr = np.frombuffer(contents, np.uint8)
        image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        print(f"\n=== 调试开始 ===")
        print(f"文件名: {file.filename}")
        print(f"图片尺寸: {image.shape}")
        
        # 尝试导入真实检测器
        try:
            from detector_fixed import FireExtinguisherDetector
            detector = FireExtinguisherDetector(use_simulation=False)
            print("✅ 真实检测器导入成功")
            
            # 调用检测
            detection_result = detector.detect(image)
            print(f"检测结果类型: {type(detection_result)}")
            
            # 打印原始数据结构
            print("\n=== 原始检测结果 ===")
            self_print_dict(detection_result, indent=2)
            
            # 尝试转换
            print("\n=== 尝试转换 ===")
            converted = convert_numpy_types(detection_result)
            print("✅ 转换完成")
            
            # 尝试JSON序列化
            print("\n=== 尝试JSON序列化 ===")
            try:
                json_str = json.dumps(converted, ensure_ascii=False)
                print(f"✅ JSON序列化成功，长度: {len(json_str)}")
                
                # 返回成功结果
                return {
                    "success": True,
                    "message": "调试成功",
                    "detection_result": converted,
                    "json_length": len(json_str)
                }
                
            except Exception as json_error:
                print(f"❌ JSON序列化失败: {json_error}")
                print(f"错误详情: {traceback.format_exc()}")
                
                # 尝试找出问题字段
                print("\n=== 查找问题字段 ===")
                find_problem_field(converted)
                
                return {
                    "success": False,
                    "error": f"JSON序列化失败: {json_error}",
                    "traceback": traceback.format_exc()
                }
                
        except ImportError as e:
            print(f"❌ 真实检测器导入失败: {e}")
            return {
                "success": False,
                "error": f"导入失败: {e}",
                "mode": "simulation"
            }
            
    except Exception as e:
        print(f"❌ 调试过程错误: {e}")
        print(f"错误详情: {traceback.format_exc()}")
        return {
            "success": False,
            "error": str(e),
            "traceback": traceback.format_exc()
        }

def self_print_dict(obj, indent=0):
    """自定义打印字典，避免递归问题"""
    if isinstance(obj, dict):
        for key, value in obj.items():
            print(" " * indent + f"{key}: {type(value)}", end="")
            if isinstance(value, (dict, list)):
                print()
                if isinstance(value, dict):
                    self_print_dict(value, indent + 4)
                elif isinstance(value, list):
                    self_print_list(value, indent + 4)
            else:
                print(f" = {repr(value)[:50]}")
    else:
        print(" " * indent + f"{type(obj)}: {repr(obj)[:50]}")

def self_print_list(obj, indent=0):
    """自定义打印列表"""
    for i, item in enumerate(obj):
        print(" " * indent + f"[{i}]: {type(item)}", end="")
        if isinstance(item, (dict, list)):
            print()
            if isinstance(item, dict):
                self_print_dict(item, indent + 4)
            elif isinstance(item, list):
                self_print_list(item, indent + 4)
        else:
            print(f" = {repr(item)[:50]}")

def find_problem_field(obj, path=""):
    """递归查找不能JSON序列化的字段"""
    try:
        json.dumps(obj)
        return None
    except TypeError as e:
        if isinstance(obj, dict):
            for key, value in obj.items():
                new_path = f"{path}.{key}" if path else key
                problem = find_problem_field(value, new_path)
                if problem:
                    return problem
        elif isinstance(obj, list):
            for i, item in enumerate(obj):
                new_path = f"{path}[{i}]"
                problem = find_problem_field(item, new_path)
                if problem:
                    return problem
        else:
            print(f"❌ 问题字段: {path}, 类型: {type(obj)}, 值: {repr(obj)[:100]}")
            return path
    return None

if __name__ == "__main__":
    print("🔧 启动调试服务器")
    print("📡 访问: http://localhost:8012")
    print("🔍 功能: 打印真实算法返回的完整数据结构")
    print("\n按 Ctrl+C 停止服务器")
    
    uvicorn.run(app, host="0.0.0.0", port=8012)