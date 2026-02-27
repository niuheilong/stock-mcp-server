#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Stock MCP Server - 最终版 v2.0
使用新浪财经 + 腾讯财经（替代 akshare）
"""

import json
from datetime import datetime
from typing import Dict, Any
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

# 导入新浪和腾讯接口
from sina_stock_api import get_sina_stock_price, get_sina_stock_batch
from qq_stock_api import get_qq_stock_price

app = FastAPI(title="Stock MCP Server", version="2.0.0")

# 启用 CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============ 工具注册表 ============

TOOLS = {
    "get_stock_price": {
        "name": "get_stock_price",
        "description": "获取A股实时股价（新浪财经数据源）",
        "inputSchema": {
            "type": "object",
            "properties": {
                "symbol": {
                    "type": "string",
                    "description": "股票代码，例如：000001、600519"
                },
                "source": {
                    "type": "string",
                    "description": "数据源：sina(默认) 或 qq",
                    "enum": ["sina", "qq"],
                    "default": "sina"
                }
            },
            "required": ["symbol"]
        }
    },
    "get_stock_batch": {
        "name": "get_stock_batch",
        "description": "批量获取多只股票数据",
        "inputSchema": {
            "type": "object",
            "properties": {
                "symbols": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "股票代码列表"
                }
            },
            "required": ["symbols"]
        }
    },
    "search_stock": {
        "name": "search_stock",
        "description": "根据名称搜索股票（返回热门股票示例）",
        "inputSchema": {
            "type": "object",
            "properties": {
                "keyword": {
                    "type": "string",
                    "description": "关键词"
                }
            },
            "required": ["keyword"]
        }
    }
}

# ============ 工具实现 ============

def get_stock_price_impl(symbol: str, source: str = "sina") -> Dict:
    """获取股价 - 自动选择数据源"""
    if source == "qq":
        return get_qq_stock_price(symbol)
    else:
        return get_sina_stock_price(symbol)

def search_stock_impl(keyword: str) -> Dict:
    """搜索股票 - 返回匹配的热门股票"""
    # 热门股票数据库
    popular_stocks = {
        "茅台": "600519",
        "平安": "000001",
        "五粮液": "000858",
        "招行": "600036",
        "比亚迪": "002594",
        "宁德时代": "300750",
        "中芯": "688981",
        "隆基": "601012",
    }
    
    results = []
    for name, code in popular_stocks.items():
        if keyword in name or keyword in code:
            # 获取实时价格
            data = get_sina_stock_price(code)
            if "error" not in data:
                results.append({
                    "symbol": code,
                    "name": name,
                    "price": data["price"],
                    "change_percent": data["change_percent"]
                })
    
    return {
        "keyword": keyword,
        "count": len(results),
        "results": results
    }

# ============ API 路由 ============

@app.get("/")
def root():
    return {
        "service": "Stock MCP Server",
        "version": "2.0.0",
        "status": "running",
        "data_source": "sina + qq",
        "tools_count": len(TOOLS)
    }

@app.get("/health")
def health_check():
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

@app.get("/mcp/tools")
def list_tools():
    return {"tools": list(TOOLS.values())}

@app.post("/mcp/call")
def call_tool(request: Dict):
    """调用工具"""
    tool_name = request.get("tool")
    args = request.get("args", {})
    
    if tool_name not in TOOLS:
        raise HTTPException(status_code=404, detail=f"Tool not found: {tool_name}")
    
    if tool_name == "get_stock_price":
        result = get_stock_price_impl(
            args.get("symbol", ""),
            args.get("source", "sina")
        )
    elif tool_name == "get_stock_batch":
        symbols = args.get("symbols", [])
        result = get_sina_stock_batch(symbols)
    elif tool_name == "search_stock":
        result = search_stock_impl(args.get("keyword", ""))
    else:
        result = {"error": "Tool implementation not found"}
    
    return {"tool": tool_name, "result": result}

# ============ 主程序 ============

if __name__ == "__main__":
    print("🚀 启动 Stock MCP Server v2.0")
    print("📊 服务地址: http://localhost:5001")
    print("📖 API 文档: http://localhost:5001/docs")
    print("")
    print("数据源: 新浪财经 + 腾讯财经")
    print("✅ 绕过东方财富反爬虫限制")
    print("")
    print("按 Ctrl+C 停止服务")
    
    uvicorn.run(app, host="0.0.0.0", port=5001, log_level="info")