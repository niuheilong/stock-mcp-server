#!/usr/bin/env python3
"""
青龙 Stock MCP Server
简单的 FastAPI 服务器
"""

from fastapi import FastAPI
from fastapi.responses import JSONResponse
import uvicorn

app = FastAPI(title="Stock MCP Server", version="3.0.0")

@app.get("/")
def root():
    return {"message": "Stock MCP Server is running", "version": "3.0.0"}

@app.get("/health")
def health():
    return {"status": "healthy"}

@app.get("/stock/{code}")
def get_stock(code: str):
    # 这里应该调用腾讯财经API获取股票数据
    return {
        "code": code,
        "price": 0.0,
        "change": 0.0,
        "message": "Stock data endpoint"
    }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
