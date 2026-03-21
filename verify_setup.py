#!/usr/bin/env python3
"""
验证设置脚本 - 确保项目可以正常运行
"""

import os
import sys
import subprocess
from pathlib import Path

def check_python_version():
    """检查Python版本"""
    print("🔍 检查Python版本...")
    version = sys.version_info
    print(f"   Python版本: {sys.version.split()[0]}")
    
    if version.major == 3 and version.minor >= 8:
        print("   ✅ Python版本符合要求 (3.8+)")
        return True
    else:
        print(f"   ❌ Python版本过低，需要3.8+，当前是{version.major}.{version.minor}")
        return False

def check_requirements():
    """检查requirements.txt文件"""
    print("\n📦 检查requirements.txt...")
    req_file = Path("requirements.txt")
    
    if not req_file.exists():
        print("   ❌ requirements.txt 不存在")
        return False
    
    with open(req_file, 'r') as f:
        lines = [line.strip() for line in f if line.strip() and not line.startswith('#')]
    
    print(f"   ✅ requirements.txt 存在，包含 {len(lines)} 个依赖")
    print("   依赖列表:")
    for line in lines[:5]:  # 显示前5个
        print(f"     - {line}")
    if len(lines) > 5:
        print(f"     ... 还有 {len(lines)-5} 个")
    
    return True

def check_core_files():
    """检查核心文件"""
    print("\n📁 检查核心文件...")
    
    core_files = [
        "app.py",
        "detector.py", 
        "requirements.txt",
        "Dockerfile",
        "docker-compose.yml",
        "README.md",
        "templates/index.html",
        ".gitignore"
    ]
    
    missing = []
    for file in core_files:
        if Path(file).exists():
            print(f"   ✅ {file}")
        else:
            print(f"   ❌ {file} 不存在")
            missing.append(file)
    
    if missing:
        print(f"   ⚠️ 缺少 {len(missing)} 个文件: {missing}")
        return False
    else:
        print("   ✅ 所有核心文件都存在")
        return True

def check_directory_structure():
    """检查目录结构"""
    print("\n📂 检查目录结构...")
    
    required_dirs = ["templates", "test_images"]
    created_dirs = ["uploads", "static"]
    
    all_ok = True
    
    # 检查必须存在的目录
    for dir_name in required_dirs:
        if Path(dir_name).exists():
            print(f"   ✅ 目录存在: {dir_name}/")
        else:
            print(f"   ❌ 目录不存在: {dir_name}/")
            all_ok = False
    
    # 检查需要创建的目录（如果不存在会自动创建）
    for dir_name in created_dirs:
        Path(dir_name).mkdir(exist_ok=True)
        print(f"   📁 目录已创建/存在: {dir_name}/")
    
    return all_ok

def check_docker_files():
    """检查Docker文件"""
    print("\n🐳 检查Docker配置...")
    
    docker_files = ["Dockerfile", "docker-compose.yml"]
    
    for file in docker_files:
        if Path(file).exists():
            with open(file, 'r') as f:
                content = f.read()
                lines = len(content.split('\n'))
                print(f"   ✅ {file} ({lines} 行)")
        else:
            print(f"   ❌ {file} 不存在")
            return False
    
    # 检查Dockerfile内容
    with open("Dockerfile", 'r') as f:
        dockerfile = f.read()
        if "FROM python:" in dockerfile and "EXPOSE 8000" in dockerfile:
            print("   ✅ Dockerfile 配置正确")
        else:
            print("   ⚠️ Dockerfile 可能配置不正确")
    
    return True

def check_web_interface():
    """检查Web界面"""
    print("\n🌐 检查Web界面...")
    
    html_file = Path("templates/index.html")
    if not html_file.exists():
        print("   ❌ templates/index.html 不存在")
        return False
    
    with open(html_file, 'r', encoding='utf-8') as f:
        content = f.read()
        size_kb = len(content) / 1024
    
    print(f"   ✅ Web界面存在 ({size_kb:.1f} KB)")
    
    # 检查关键元素
    checks = [
        ("<!DOCTYPE html>", "HTML文档声明"),
        ("<form", "表单元素"),
        ("<input type=\"file\"", "文件上传"),
        ("fetch(", "JavaScript API调用")
    ]
    
    for text, description in checks:
        if text in content:
            print(f"     ✅ 包含: {description}")
        else:
            print(f"     ⚠️ 可能缺少: {description}")
    
    return True

def generate_quick_start_guide():
    """生成快速开始指南"""
    print("\n" + "="*60)
    print("🚀 快速开始指南")
    print("="*60)
    
    guide = """
1. 安装依赖:
   pip install -r requirements.txt

2. 启动服务:
   python app.py

3. 打开浏览器访问:
   http://localhost:8000

4. 测试API:
   curl -X POST -F "file=@test.jpg" http://localhost:8000/api/check

5. 或使用Docker:
   docker-compose up --build
   """
    
    print(guide)
    
    print("\n📋 下一步:")
    print("1. 运行 'pip install -r requirements.txt' 安装依赖")
    print("2. 运行 'python app.py' 启动服务")
    print("3. 访问 http://localhost:8000 测试功能")
    print("4. 上传 test_images/ 中的图片验证检测结果")

def main():
    """主函数"""
    print("="*60)
    print("🔥 隐患检测MVP - 环境验证脚本")
    print("="*60)
    
    tests = [
        ("Python版本", check_python_version),
        ("依赖文件", check_requirements),
        ("核心文件", check_core_files),
        ("目录结构", check_directory_structure),
        ("Docker配置", check_docker_files),
        ("Web界面", check_web_interface),
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            success = test_func()
            results.append((test_name, success))
        except Exception as e:
            print(f"   ❌ 测试出错: {e}")
            results.append((test_name, False))
    
    # 汇总结果
    print("\n" + "="*60)
    print("📊 验证结果汇总")
    print("="*60)
    
    passed = sum(1 for _, success in results if success)
    total = len(results)
    
    for test_name, success in results:
        status = "✅ 通过" if success else "❌ 失败"
        print(f"{test_name:15} {status}")
    
    print(f"\n通过率: {passed}/{total} ({passed/total*100:.0f}%)")
    
    if passed == total:
        print("\n🎉 所有检查通过！项目可以正常运行。")
        generate_quick_start_guide()
        return True
    else:
        print("\n⚠️ 部分检查失败，请修复问题后再运行。")
        print("\n💡 建议:")
        print("1. 确保所有核心文件都存在")
        print("2. 检查Python版本 (需要3.8+)")
        print("3. 运行 'python simple_test.py' 进行详细诊断")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)