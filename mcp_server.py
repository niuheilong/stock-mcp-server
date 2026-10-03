#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
青龙 Stock MCP Server (MCP stdio)
=================================
基于 Model Context Protocol 的 A 股数据服务，供 Claude / Cursor / 各类 AI Agent 调用。

数据源：新浪财经（行情/指数/搜索）、腾讯财经（K线/基本面/行情备用）
传输方式：stdio（标准 MCP，可直接被 mcp-proxy / Glama 等宿主启动）

启动：
    python mcp_server.py
"""

import urllib.parse
from typing import Any, Dict, List

import requests
import urllib3

from mcp.server.mcpserver import MCPServer

from sina_stock_api import get_sina_stock_price, get_sina_stock_batch
from qq_stock_api import get_qq_stock_price

import usage_log

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

mcp = MCPServer("stock-mcp-server")

_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    ),
    "Referer": "https://finance.sina.com.cn",
    "Accept": "*/*",
}

# 常用大盘指数（新浪代号 -> 名称）
INDEX_ALIASES = {
    "sh000001": "上证指数",
    "sz399001": "深证成指",
    "sz399006": "创业板指",
    "sh000300": "沪深300",
    "sh000905": "中证500",
    "sh000016": "上证50",
    "sz399005": "中小100",
    "sz399852": "中证1000",
}


# --------------------------------------------------------------------------- #
# 内部工具函数
# --------------------------------------------------------------------------- #
def _split_codes(symbols: str) -> List[str]:
    """逗号（中/英文）分隔的代码串 -> 代码列表。"""
    return [s.strip() for s in (symbols or "").replace("，", ",").split(",") if s.strip()]


def _market_symbol(symbol: str) -> str:
    """把股票代码规范成带市场前缀的形式：600519 -> sh600519。"""
    code = (symbol or "").strip().lower()
    if code[:2] in ("sh", "sz", "bj"):
        return code
    if code.startswith(("6", "5", "9")):
        return "sh" + code
    if code.startswith(("4", "8")):
        return "bj" + code
    return "sz" + code


def _f(value: Any, default: float = 0.0) -> float:
    """安全转 float。"""
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def _tencent_fields(symbol: str) -> List[str]:
    """取腾讯行情原始字段（按 ~ 分隔）。"""
    sec = _market_symbol(symbol)
    resp = requests.get(
        "https://qt.gtimg.cn/q=" + sec,
        headers=_HEADERS,
        timeout=15,
        verify=False,
    )
    resp.encoding = "gb18030"
    if '"' not in resp.text:
        return []
    return resp.text.split('"')[1].split("~")


# --------------------------------------------------------------------------- #
# MCP 工具
# --------------------------------------------------------------------------- #
@mcp.tool()
def get_stock_quote(symbol: str, source: str = "auto") -> Dict[str, Any]:
    """获取单只 A 股股票的实时行情。

    默认自动选源（新浪优先，失败后回退腾讯）；也可用 source 强制指定数据源。

    Args:
        symbol: 股票代码，如 "600519"（贵州茅台）、"000001"（平安银行）。
        source: 数据源，"auto"（默认，自动回退）| "sina" | "tencent"。
    """
    usage_log.record("get_stock_quote")
    symbol = (symbol or "").strip()
    if not symbol:
        return {"error": "请提供股票代码，例如 600519"}

    src = (source or "auto").strip().lower()

    if src in ("tencent", "qq"):
        data = get_qq_stock_price(symbol)
    elif src == "sina":
        data = get_sina_stock_price(symbol)
    else:  # auto：新浪优先，失败回退腾讯
        data = get_sina_stock_price(symbol)
        if isinstance(data, dict) and "error" in data:
            fallback = get_qq_stock_price(symbol)
            if isinstance(fallback, dict) and "error" not in fallback:
                data = fallback

    return data if isinstance(data, dict) else {"error": "获取数据失败"}


@mcp.tool()
def get_stock_quotes(symbols: str) -> Dict[str, Any]:
    """批量获取多只 A 股股票的实时行情（最多 10 只）。

    Args:
        symbols: 逗号分隔的股票代码，如 "600519,000001,000858"。中英文逗号均可。
    """
    usage_log.record("get_stock_quotes")
    codes = _split_codes(symbols)
    if not codes:
        return {"error": "请提供至少一个股票代码，例如 600519,000001"}
    return get_sina_stock_batch(codes)


@mcp.tool()
def get_stock_history(symbol: str, period: str = "daily", count: int = 30) -> Dict[str, Any]:
    """获取单只 A 股的历史 K 线数据（前复权）。

    Args:
        symbol: 股票代码，如 "600519"。
        period: 周期，"daily"（日K，默认）| "weekly"（周K）| "monthly"（月K）。
        count: 返回的 K 线根数，默认 30，最大 320。
    """
    usage_log.record("get_stock_history")
    symbol = (symbol or "").strip()
    if not symbol:
        return {"error": "请提供股票代码，例如 600519"}

    p = {"daily": "day", "day": "day", "weekly": "week", "week": "week",
         "monthly": "month", "month": "month"}.get((period or "daily").lower())
    if not p:
        return {"error": "period 只能是 daily / weekly / monthly"}

    n = max(1, min(int(count or 30), 320))
    sec = _market_symbol(symbol)

    try:
        resp = requests.get(
            "https://web.ifzq.gtimg.cn/appstock/app/fqkline/get",
            params={"param": f"{sec},{p},,,{n},qfq"},
            headers=_HEADERS,
            timeout=15,
            verify=False,
        )
        node = (resp.json().get("data") or {}).get(sec, {})
        rows = node.get(f"qfq{p}") or node.get(p) or []
    except Exception as exc:  # noqa: BLE001
        return {"error": f"获取 K 线失败: {exc}"}

    if not rows:
        return {"error": "未获取到 K 线数据，请确认股票代码"}

    candles: List[Dict[str, Any]] = []
    for row in rows:
        if len(row) < 6:
            continue
        candles.append(
            {
                "date": row[0],
                "open": _f(row[1]),
                "close": _f(row[2]),
                "high": _f(row[3]),
                "low": _f(row[4]),
                "volume": _f(row[5]),
            }
        )

    return {
        "symbol": symbol,
        "period": p,
        "count": len(candles),
        "candles": candles,
    }


@mcp.tool()
def get_stock_fundamentals(symbol: str) -> Dict[str, Any]:
    """获取单只 A 股的估值与基本面指标。

    返回：市盈率(TTM)、市净率、总市值、流通市值、换手率、振幅、涨跌停价等。

    Args:
        symbol: 股票代码，如 "600519"。
    """
    usage_log.record("get_stock_fundamentals")
    symbol = (symbol or "").strip()
    if not symbol:
        return {"error": "请提供股票代码，例如 600519"}

    try:
        f = _tencent_fields(symbol)
    except Exception as exc:  # noqa: BLE001
        return {"error": f"获取基本面失败: {exc}"}

    if len(f) < 48 or not f[1]:
        return {"error": "未获取到基本面数据，请确认股票代码"}

    return {
        "symbol": symbol,
        "name": f[1],
        "price": _f(f[3]),
        "pe_ttm": _f(f[39]),
        "pb": _f(f[46]),
        "market_cap_yi": _f(f[45]),         # 总市值（亿元）
        "float_market_cap_yi": _f(f[44]),   # 流通市值（亿元）
        "turnover_rate": _f(f[38]),         # 换手率（%）
        "amplitude": _f(f[43]),             # 振幅（%）
        "limit_up": _f(f[47]),
        "limit_down": _f(f[48]),
        "source": "tencent",
    }


@mcp.tool()
def get_market_index(codes: str = "") -> Dict[str, Any]:
    """获取 A 股大盘指数实时行情（上证指数、深证成指、创业板指、沪深300 等）。

    Args:
        codes: 可选，逗号分隔的指数代码，如 "sh000001,sz399001"。
               留空则返回上证指数 / 深证成指 / 创业板指 / 沪深300。
    """
    usage_log.record("get_market_index")
    code_list = _split_codes(codes) or ["sh000001", "sz399001", "sz399006", "sh000300"]
    secs = [c if c[:2] in ("sh", "sz") else _market_symbol(c) for c in code_list]

    try:
        resp = requests.get(
            "https://hq.sinajs.cn/list=" + ",".join("s_" + s for s in secs),
            headers=_HEADERS,
            timeout=15,
            verify=False,
        )
        resp.encoding = "gb18030"
    except Exception as exc:  # noqa: BLE001
        return {"error": f"获取指数失败: {exc}"}

    indices: List[Dict[str, Any]] = []
    for line in resp.text.strip().split("\n"):
        if '"' not in line:
            continue
        sec = line.split("hq_str_s_")[1].split("=")[0] if "hq_str_s_" in line else ""
        parts = line.split('"')[1].split(",")
        if len(parts) < 4 or not parts[0]:
            continue
        indices.append(
            {
                "code": sec,
                "name": parts[0],
                "price": _f(parts[1]),
                "change": _f(parts[2]),
                "change_percent": _f(parts[3]),
                "volume_shou": _f(parts[4]) if len(parts) > 4 else 0.0,
                "amount_wan": _f(parts[5]) if len(parts) > 5 else 0.0,
            }
        )

    if not indices:
        return {"error": "未获取到指数数据"}
    return {"count": len(indices), "indices": indices, "source": "sina"}


@mcp.tool()
def search_stock(keyword: str) -> Dict[str, Any]:
    """按关键字搜索 A 股股票（支持名称、代码、拼音首字母模糊匹配）。

    Args:
        keyword: 搜索词，如 "茅台"、"600519"、"PAYH"（平安银行拼音首字母）。
    """
    usage_log.record("search_stock")
    keyword = (keyword or "").strip()
    if not keyword:
        return {"error": "请提供搜索关键字，例如 茅台"}

    try:
        resp = requests.get(
            "https://suggest3.sinajs.cn/suggest/type=11,12,13,14,15",
            params={"key": keyword},
            headers=_HEADERS,
            timeout=15,
            verify=False,
        )
        resp.encoding = "gb18030"
    except Exception as exc:  # noqa: BLE001
        return {"error": f"搜索失败: {exc}"}

    if '"' not in resp.text:
        return {"keyword": keyword, "count": 0, "results": []}

    payload = resp.text.split('"')[1] if '"' in resp.text else ""
    results: List[Dict[str, Any]] = []
    for item in payload.split(";"):
        fields = item.split(",")
        if len(fields) < 4 or not fields[0]:
            continue
        results.append(
            {
                "name": fields[0],
                "type": fields[1],
                "code": fields[2],
                "symbol": fields[3],
            }
        )
        if len(results) >= 10:
            break

    return {"keyword": keyword, "count": len(results), "results": results}


@mcp.tool()
def get_usage_stats(days: int = 7) -> Dict[str, Any]:
    """获取本 MCP 服务器的工具调用统计（本地记录）。

    返回最近 N 天的调用总数、错误数、各工具调用次数、按天分布。
    统计只覆盖有写入日志文件的实例；日志路径可用环境变量 STOCK_MCP_USAGE_LOG 指定。

    Args:
        days: 统计最近多少天，默认 7，最大 365。
    """
    return usage_log.summary(max(1, min(int(days or 7), 365)))


if __name__ == "__main__":
    # 默认 stdio 传输，符合 MCP 规范，可被 mcp-proxy 等宿主直接拉起
    mcp.run()
