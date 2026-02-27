#!/usr/bin/env python3
"""
Stock MCP Server 增强版
集成多智能体分析系统
"""

import json
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Optional

# 导入多智能体系统
from multi_agent_system import multi_agent_stock_analysis
from technical_indicators import TechnicalAnalyst
from jina_reader import fetch_with_jina, fetch_with_fallback

app = FastAPI(title="Stock MCP Server Enhanced", version="3.0.0")

# CORS 配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 数据模型
class StockQuery(BaseModel):
    symbol: str
    source: Optional[str] = "sina"

class MultiAgentAnalysis(BaseModel):
    symbol: str
    include_technical: bool = True
    include_fundamental: bool = True
    include_sentiment: bool = True
    include_risk: bool = True

class WebFetchRequest(BaseModel):
    url: str
    use_jina: bool = True

# 健康检查
@app.get("/health")
async def health_check():
    return {"status": "healthy", "version": "3.0.0", "features": ["multi-agent", "technical-analysis", "web-fetch"]}

# 获取工具列表
@app.get("/mcp/tools")
async def list_tools():
    tools = [
        {
            "name": "get_stock_price",
            "description": "获取单只股票实时价格",
            "parameters": {
                "symbol": "股票代码（如 600519）",
                "source": "数据源（sina 或 qq）"
            }
        },
        {
            "name": "multi_agent_analysis",
            "description": "多智能体股票分析（技术+基本面+情绪+风险）",
            "parameters": {
                "symbol": "股票代码",
                "include_technical": "是否包含技术分析",
                "include_fundamental": "是否包含基本面分析",
                "include_sentiment": "是否包含情绪分析",
                "include_risk": "是否包含风险评估"
            }
        },
        {
            "name": "technical_analysis",
            "description": "专业的技术指标分析（MACD/RSI/KDJ/布林带）",
            "parameters": {
                "symbol": "股票代码"
            }
        },
        {
            "name": "fetch_webpage",
            "description": "抓取网页内容（增强版，支持 Jina Reader）",
            "parameters": {
                "url": "网页URL",
                "use_jina": "是否使用 Jina Reader"
            }
        },
        {
            "name": "get_stock_batch",
            "description": "批量获取多只股票价格",
            "parameters": {
                "symbols": "股票代码列表"
            }
        },
        {
            "name": "search_stock",
            "description": "搜索股票",
            "parameters": {
                "keyword": "搜索关键词"
            }
        }
    ]
    return {"tools": tools}

# 调用工具
@app.post("/mcp/call")
async def call_tool(request: dict):
    try:
        tool_name = request.get("tool")
        args = request.get("args", {})
        
        if tool_name == "get_stock_price":
            from sina_stock_api import get_sina_stock_price
            symbol = args.get("symbol")
            source = args.get("source", "sina")
            
            if source == "sina":
                result = get_sina_stock_price(symbol)
            else:
                from qq_stock_api import get_qq_stock_price
                result = get_qq_stock_price(symbol)
            
            return {"tool": tool_name, "result": result}
        
        elif tool_name == "multi_agent_analysis":
            symbol = args.get("symbol")
            if not symbol:
                raise HTTPException(status_code=400, detail="Missing symbol parameter")
            
            # 执行多智能体分析
            report = multi_agent_stock_analysis(symbol)
            return {"tool": tool_name, "result": report}
        
        elif tool_name == "technical_analysis":
            symbol = args.get("symbol")
            if not symbol:
                raise HTTPException(status_code=400, detail="Missing symbol parameter")
            
            analyst = TechnicalAnalyst(symbol)
            report = analyst.analyze()
            return {"tool": tool_name, "result": report}
        
        elif tool_name == "fetch_webpage":
            url = args.get("url")
            use_jina = args.get("use_jina", True)
            
            if not url:
                raise HTTPException(status_code=400, detail="Missing url parameter")
            
            if use_jina:
                result = fetch_with_jina(url)
            else:
                result = fetch_with_fallback(url)
            
            return {"tool": tool_name, "result": result}
        
        elif tool_name == "get_stock_batch":
            symbols = args.get("symbols", [])
            if not symbols:
                raise HTTPException(status_code=400, detail="Missing symbols parameter")
            
            from sina_stock_api import get_sina_stock_price
            results = []
            for symbol in symbols:
                try:
                    result = get_sina_stock_price(symbol)
                    results.append(result)
                except Exception as e:
                    results.append({"symbol": symbol, "error": str(e)})
            
            return {"tool": tool_name, "result": results}
        
        elif tool_name == "search_stock":
            keyword = args.get("keyword")
            if not keyword:
                raise HTTPException(status_code=400, detail="Missing keyword parameter")
            
            # 简单的搜索实现
            from sina_stock_api import search_stock_by_keyword
            result = search_stock_by_keyword(keyword)
            return {"tool": tool_name, "result": result}
        
        else:
            raise HTTPException(status_code=404, detail=f"Tool {tool_name} not found")
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# 直接 API 端点
@app.post("/api/stock/price")
async def get_stock_price(query: StockQuery):
    try:
        from sina_stock_api import get_sina_stock_price
        result = get_sina_stock_price(query.symbol)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/stock/analysis")
async def get_stock_analysis(query: MultiAgentAnalysis):
    try:
        report = multi_agent_stock_analysis(query.symbol)
        
        # 根据请求过滤结果
        filtered_report = {"stock_code": query.symbol}
        
        if query.include_technical:
            filtered_report["technical_analysis"] = report.get("technical_analysis", {})
        
        if query.include_fundamental:
            filtered_report["fundamental_analysis"] = report.get("fundamental_analysis", {})
        
        if query.include_sentiment:
            filtered_report["sentiment_analysis"] = report.get("sentiment_analysis", {})
        
        if query.include_risk:
            filtered_report["risk_assessment"] = report.get("risk_assessment", {})
        
        filtered_report["final_decision"] = report.get("final_decision", {})
        
        return filtered_report
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/web/fetch")
async def fetch_webpage(request: WebFetchRequest):
    try:
        if request.use_jina:
            result = fetch_with_jina(request.url)
        else:
            result = fetch_with_fallback(request.url)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# 启动服务器
if __name__ == "__main__":
    import uvicorn
    print("🚀 Stock MCP Server Enhanced v3.0.0")
    print("=" * 60)
    print("Features:")
    print("  ✅ Multi-agent stock analysis")
    print("  ✅ Professional technical indicators")
    print("  ✅ Enhanced web fetching with Jina Reader")
    print("  ✅ Real-time stock data")
    print("=" * 60)
    uvicorn.run(app, host="0.0.0.0", port=5001)
