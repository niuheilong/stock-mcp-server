#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
青龙 Stock MCP Server (MCP stdio)
=================================
基于 Model Context Protocol 的 A 股实时数据服务，供 Claude / Cursor / 各类 AI Agent 调用。

数据源：新浪财经（主）、腾讯财经（备用）
传输方式：stdio（标准 MCP，可直接被 mcp-proxy / Glama 等宿主启动）

启动：
    python mcp_server.py
"""

from typing import Any, Dict

from mcp.server.mcpserver import MCPServer

from sina_stock_api import get_sina_stock_price, get_sina_stock_batch
from qq_stock_api import get_qq_stock_price

mcp = MCPServer("stock-mcp-server")


def _get_price(symbol: str) -> Dict[str, Any]:
    """新浪为主、腾讯为备，取单只股票实时行情。"""
    symbol = (symbol or "").strip()
    if not symbol:
        return {"error": "请提供股票代码，例如 600519"}

    data = get_sina_stock_price(symbol)
    if isinstance(data, dict) and "error" not in data:
        return data

    fallback = get_qq_stock_price(symbol)
    if isinstance(fallback, dict) and "error" not in fallback:
        return fallback

    return data if isinstance(data, dict) else {"error": "获取数据失败"}


@mcp.tool()
def get_stock_price(symbol: str) -> Dict[str, Any]:
    """获取单只 A 股股票的实时行情。

    返回：股票名称、当前价、涨跌额、涨跌幅、今开、昨收、最高、最低、成交量、成交额等。

    Args:
        symbol: 6 位股票代码，如 "600519"（贵州茅台）、"000001"（平安银行）。
    """
    return _get_price(symbol)


@mcp.tool()
def get_stock_batch(symbols: str) -> Dict[str, Any]:
    """批量获取多只 A 股股票的实时行情（最多 10 只）。

    Args:
        symbols: 逗号分隔的股票代码，如 "600519,000001,000858"。中英文逗号均可。
    """
    codes = [s.strip() for s in symbols.replace("，", ",").split(",") if s.strip()]
    if not codes:
        return {"error": "请提供至少一个股票代码，例如 600519,000001"}
    return get_sina_stock_batch(codes)


@mcp.tool()
def get_stock_quote_from_qq(symbol: str) -> Dict[str, Any]:
    """从腾讯财经获取单只 A 股实时行情（新浪不可用时的备用通道）。

    Args:
        symbol: 6 位股票代码，如 "600519"。
    """
    symbol = (symbol or "").strip()
    if not symbol:
        return {"error": "请提供股票代码，例如 600519"}
    return get_qq_stock_price(symbol)


if __name__ == "__main__":
    # 默认 stdio 传输，符合 MCP 规范，可被 mcp-proxy 等宿主直接拉起
    mcp.run()
