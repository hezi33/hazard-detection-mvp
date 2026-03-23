#!/usr/bin/env python3
"""
简单上传测试服务器
"""

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
import uvicorn

app = FastAPI(title="简单上传测试")

@app.get("/", response_class=HTMLResponse)
async def simple_test():
    """简单测试页面"""
    with open("templates/simple_test.html", "r", encoding="utf-8") as f:
        return HTMLResponse(content=f.read())

@app.get("/health")
async def health():
    return {"status": "healthy", "service": "simple-upload-test"}

if __name__ == "__main__":
    print("启动简单上传测试服务器...")
    print("访问: http://localhost:8004")
    uvicorn.run(app, host="0.0.0.0", port=8004)