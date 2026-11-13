"""Qinglong MCP server — real-time A-share market data for AI agents.

Run over stdio (Claude Code / Cursor / Claude Desktop default):

    uvx --from git+https://github.com/niuheilong/stock-mcp-server qinglong-mcp

Or over streamable HTTP:

    qinglong-mcp --transport http --port 8000
"""

from __future__ import annotations

import argparse
from typing import Any, Dict, List

from mcp.server.fastmcp import FastMCP

from qinglong import api

mcp = FastMCP(
    "qinglong-a-share",
    instructions=(
        "Real-time mainland China A-share market data (Shanghai, Shenzhen, Beijing). "
        "Prices are quoted in CNY, volume in lots (1 lot = 100 shares), "
        "amounts in 10k CNY, market cap in 100m CNY. "
        "Data comes from public Tencent Finance endpoints, delayed by seconds. "
        "For research only — never present output as investment advice."
    ),
)


@mcp.tool()
def get_stock_quote(code: str) -> Dict[str, Any]:
    """Get a real-time snapshot for one A-share ticker.

    Args:
        code: Ticker such as "600519", "sh600519" or "600519.SH".
              Shanghai starts with 6, Shenzhen with 0/2/3, Beijing with 4/8.
    """
    return api.get_quote(code)


@mcp.tool()
def get_stock_quotes(codes: List[str]) -> List[Dict[str, Any]]:
    """Get real-time snapshots for several A-share tickers in one call (max 50)."""
    return api.get_quotes(codes)


@mcp.tool()
def get_stock_kline(code: str, period: str = "day", count: int = 60, adjust: str = "qfq") -> Dict[str, Any]:
    """Get historical OHLCV bars for an A-share ticker.

    Args:
        code: Ticker such as "600519" or "sh600519".
        period: "day", "week" or "month".
        count: Number of bars, 1-320.
        adjust: "qfq" (forward-adjusted, default), "hfq" (backward) or "none".
    """
    return api.get_kline(code, period=period, count=count, adjust=adjust)


@mcp.tool()
def search_stock(keyword: str, limit: int = 10) -> List[Dict[str, Any]]:
    """Search A-share tickers by code, Chinese name or pinyin initials.

    Args:
        keyword: For example "平安", "600519" or "payh".
        limit: Maximum results, default 10.
    """
    return api.search_stock(keyword, limit=limit)


@mcp.tool()
def get_market_indices() -> List[Dict[str, Any]]:
    """Get snapshots for major mainland indices: SSE Composite, SZSE Component,
    ChiNext, STAR 50 and CSI 300."""
    return api.get_index_quotes()


@mcp.tool()
def check_data_source() -> Dict[str, Any]:
    """Check whether the upstream A-share data source is reachable."""
    return api.health_check()


def main() -> None:
    parser = argparse.ArgumentParser(description="Qinglong A-share MCP server")
    parser.add_argument("--transport", choices=["stdio", "http", "sse"], default="stdio")
    parser.add_argument("--port", type=int, default=8000)
    parser.add_argument("--host", default="0.0.0.0")
    args = parser.parse_args()

    if args.transport == "stdio":
        mcp.run()
    else:
        mcp.settings.host = args.host
        mcp.settings.port = args.port
        mcp.run(transport="streamable-http" if args.transport == "http" else "sse")


if __name__ == "__main__":
    main()
