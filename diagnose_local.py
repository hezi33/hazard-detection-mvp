#!/usr/bin/env python3
"""
本地环境诊断脚本
"""

import requests
import sys
import os
import subprocess
import time
from pathlib import Path

def check_service_running(port=8000):
    """检查服务是否运行"""
    print(f"🔍 检查服务是否在端口 {port} 运行...")
    
    try:
        response = requests.get(f"http://localhost:{port}/health", timeout=2)
        if response.status_code == 200:
            print(f"✅ 服务运行正常: {response.json()}")
            return True
        else:
            print(f"❌ 服务返回错误: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print(f"❌ 无法连接到 localhost:{port}，服务可能未启动")
        return False
    except Exception as e:
        print(f"❌ 检查服务时出错: {e}")
        return False

def test_api_endpoint(port=8000):
    """测试API端点"""
    print(f"\n🔧 测试API端点...")
    
    # 创建测试文件
    test_file = "diagnose_test.txt"
    with open(test_file, "w") as f:
        f.write("诊断测试文件")
    
    try:
        with open(test_file, "rb") as f:
            files = {"file": f}
            response = requests.post(f"http://localhost:{port}/api/check", files=files, timeout=5)
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ API调用成功")
            print(f"   状态码: {response.status_code}")
            print(f"   响应时间: {response.elapsed.total_seconds():.2f}秒")
            print(f"   结果: {result.get('success', 'N/A')}")
            return True
        else:
            print(f"❌ API调用失败: {response.status_code}")
            print(f"   响应: {response.text[:200]}")
            return False
            
    except Exception as e:
        print(f"❌ API测试失败: {e}")
        return False
    finally:
        # 清理测试文件
        if os.path.exists(test_file):
            os.remove(test_file)

def check_frontend_files():
    """检查前端文件"""
    print(f"\n🌐 检查前端文件...")
    
    required_files = [
        "templates/index.html",
        "app.py",
        "requirements.txt"
    ]
    
    all_exist = True
    for file_path in required_files:
        if Path(file_path).exists():
            size = Path(file_path).stat().st_size
            print(f"✅ {file_path} ({size} bytes)")
        else:
            print(f"❌ {file_path} 不存在")
            all_exist = False
    
    # 检查HTML文件内容
    if Path("templates/index.html").exists():
        with open("templates/index.html", "r", encoding="utf-8") as f:
            content = f.read()
            checks = [
                ("<form", "表单元素"),
                ("action=", "表单提交地址"),
                ("fetch(", "JavaScript API调用"),
                ("/api/check", "API端点引用")
            ]
            
            for text, description in checks:
                if text in content:
                    print(f"    ✅ HTML包含: {description}")
                else:
                    print(f"    ⚠️ HTML可能缺少: {description}")
    
    return all_exist

def check_dependencies():
    """检查依赖"""
    print(f"\n📦 检查Python依赖...")
    
    required_packages = [
        "fastapi",
        "uvicorn", 
        "opencv-python",
        "numpy",
        "ultralytics"
    ]
    
    try:
        import importlib
        for package in required_packages:
            try:
                importlib.import_module(package.split('-')[0])  # 处理 opencv-python -> cv2
                print(f"✅ {package}: 已安装")
            except ImportError:
                print(f"❌ {package}: 未安装")
        
        return True
    except Exception as e:
        print(f"⚠️ 检查依赖时出错: {e}")
        return False

def check_port_availability(port=8000):
    """检查端口是否可用"""
    print(f"\n🔌 检查端口 {port} 可用性...")
    
    try:
        import socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(1)
        result = sock.connect_ex(('localhost', port))
        sock.close()
        
        if result == 0:
            print(f"⚠️ 端口 {port} 已被占用")
            return False
        else:
            print(f"✅ 端口 {port} 可用")
            return True
    except Exception as e:
        print(f"❌ 检查端口时出错: {e}")
        return False

def start_service_and_test():
    """启动服务并测试"""
    print(f"\n🚀 尝试启动服务并测试...")
    
    # 检查端口
    if not check_port_availability(8000):
        print("⚠️ 建议使用其他端口，如 8001")
        port = 8001
    else:
        port = 8000
    
    # 启动服务（在后台）
    print(f"启动服务在端口 {port}...")
    
    # 修改app.py使用指定端口
    app_content = Path("app.py").read_text(encoding="utf-8")
    if "port=8000" in app_content:
        app_content = app_content.replace("port=8000", f"port={port}")
        Path("app.py").write_text(app_content, encoding="utf-8")
        print(f"✅ 已更新app.py使用端口 {port}")
    
    # 这里只是提示，实际需要在终端启动
    print(f"\n📋 请在终端执行:")
    print(f"   cd {os.getcwd()}")
    print(f"   python app.py")
    print(f"\n然后打开浏览器访问: http://localhost:{port}")
    
    return port

def generate_fix_guide(issues):
    """生成修复指南"""
    print(f"\n" + "="*60)
    print(f"🔧 修复指南")
    print("="*60)
    
    if "service_not_running" in issues:
        print(f"\n1. 服务未启动:")
        print(f"   执行: python app.py")
        print(f"   确保看到: '🚀 启动隐患检测MVP服务...'")
    
    if "api_failed" in issues:
        print(f"\n2. API调用失败:")
        print(f"   测试: curl -X POST -F 'file=@test.txt' http://localhost:8000/api/check")
        print(f"   检查app.py中的/api/check端点")
    
    if "frontend_issue" in issues:
        print(f"\n3. 前端问题:")
        print(f"   检查 templates/index.html 中的JavaScript代码")
        print(f"   确保表单action指向正确的URL")
    
    if "cors_issue" in issues:
        print(f"\n4. CORS跨域问题:")
        print(f"   在app.py中添加:")
        print(f"   from fastapi.middleware.cors import CORSMiddleware")
        print(f"   app.add_middleware(CORSMiddleware, allow_origins=['*'], ...)")
    
    if "port_in_use" in issues:
        print(f"\n5. 端口被占用:")
        print(f"   使用其他端口:")
        print(f"   python app.py --port 8001")
        print(f"   或修改app.py中的端口号")
    
    print(f"\n📞 如果还有问题，请提供:")
    print(f"   - 浏览器Console错误信息 (F12 → Console)")
    print(f"   - 终端启动服务的完整输出")
    print(f"   - curl测试API的结果")

def main():
    """主诊断函数"""
    print("="*60)
    print("🔧 隐患检测MVP - 本地环境诊断")
    print("="*60)
    
    issues = []
    
    # 1. 检查服务
    if not check_service_running():
        issues.append("service_not_running")
    
    # 2. 检查前端文件
    if not check_frontend_files():
        issues.append("frontend_issue")
    
    # 3. 检查依赖
    check_dependencies()
    
    # 4. 检查端口
    if not check_port_availability():
        issues.append("port_in_use")
    
    # 5. 测试API（如果服务运行）
    if "service_not_running" not in issues:
        if not test_api_endpoint():
            issues.append("api_failed")
    
    # 总结
    print(f"\n" + "="*60)
    print(f"📊 诊断结果")
    print("="*60)
    
    if not issues:
        print(f"✅ 所有检查通过！")
        print(f"   服务应该正常工作")
        print(f"   访问: http://localhost:8000")
    else:
        print(f"⚠️ 发现 {len(issues)} 个问题:")
        for issue in issues:
            print(f"   • {issue}")
        
        # 生成修复指南
        generate_fix_guide(issues)
        
        # 尝试自动修复
        if "service_not_running" in issues:
            start_service_and_test()
    
    print(f"\n🎯 建议操作:")
    print(f"1. 确保在项目目录执行: cd hazard-detection-mvp")
    print(f"2. 安装依赖: pip install -r requirements.txt")
    print(f"3. 启动服务: python app.py")
    print(f"4. 在另一个终端测试: curl http://localhost:8000/health")
    print(f"5. 打开浏览器访问: http://localhost:8000")

if __name__ == "__main__":
    main()