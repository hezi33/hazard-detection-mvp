@echo off
echo 简单文件上传测试
echo.

REM 检查Python
python --version
if errorlevel 1 (
    echo Python未找到，请确保Python已安装并添加到PATH
    pause
    exit /b 1
)

REM 创建最简单的Python服务器
echo 创建测试服务器...
(
echo from fastapi import FastAPI
echo from fastapi.responses import HTMLResponse
echo import uvicorn
echo.
echo app = FastAPI()
echo.
echo @app.get^("/"^)
echo async def home^(^):
echo     html = """
echo     ^<!DOCTYPE html^>
echo     ^<html^>
echo     ^<head^>
echo         ^<title^>简单测试^</title^>
echo     ^</head^>
echo     ^<body^>
echo         ^<h1^>文件读取测试^</h1^>
echo         ^<input type="file" id="fileInput" accept="image/*"^>
echo         ^<button onclick="testRead^(^)"^>测试^</button^>
echo         ^<div id="status"^>^</div^>
echo         ^<img id="preview" style="max-width: 400px;"^>
echo         ^<script^>
echo             function testRead^(^) {
echo                 const file = document.getElementById^('fileInput'^).files[0];
echo                 if ^(^!file^) { alert^('请选择文件'^); return; }
echo                 const reader = new FileReader^(^);
echo                 reader.onload = function^(e^) {
echo                     document.getElementById^('preview'^).src = e.target.result;
echo                     document.getElementById^('status'^).innerHTML = '✅ 成功显示图片';
echo                 };
echo                 reader.readAsDataURL^(file^);
echo             }
echo         ^</script^>
echo     ^</body^>
echo     ^</html^>
echo     """
echo     return HTMLResponse^(content=html^)
echo.
echo if __name__ == "__main__":
echo     print^("访问: http://localhost:8008"^)
echo     uvicorn.run^(app, host="0.0.0.0", port=8008^)
) > simple_test.py

echo 启动测试服务器...
python simple_test.py

pause