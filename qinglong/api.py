"""Real A-share market data via Tencent Finance public endpoints.

All functions return plain dicts/lists and raise QinglongError on failure.
No fabricated data: if an upstream request fails, the error is surfaced.
"""

from __future__ import annotations

import json
import re
import time
from typing import Any, Dict, List, Optional

import requests

QUOTE_URL = "http://qt.gtimg.cn/q={symbols}"
KLINE_URL = "https://web.ifzq.gtimg.cn/appstock/app/fqkline/get"
SEARCH_URL = "https://smartbox.gtimg.cn/s3/"

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36"
    ),
    "Referer": "https://gu.qq.com/",
}

INDEX_CODES = {
    "sh000001": "上证指数",
    "sz399001": "深证成指",
    "sz399006": "创业板指",
    "sh000688": "科创50",
    "sh000300": "沪深300",
}

_PERIODS = {"day", "week", "month"}


class QinglongError(Exception):
    """Upstream data unavailable or symbol not found."""


def normalize_code(code: str) -> str:
    """Return a Tencent-style symbol such as ``sh600410`` / ``sz000001``."""
    raw = str(code).strip().lower().replace(" ", "")
    m = re.fullmatch(r"(\d{6})\.(sh|sz|bj)", raw)
    if m:
        return f"{m.group(2)}{m.group(1)}"
    if re.fullmatch(r"(sh|sz|bj)\d{6}", raw):
        return raw
    if re.fullmatch(r"\d{6}", raw):
        if raw[0] in "69":
            return "sh" + raw
        if raw[0] in "023":
            return "sz" + raw
        if raw[0] in "48":
            return "bj" + raw
    raise QinglongError(f"无法识别的股票代码: {code!r}，请使用 600410 / sh600410 / 600410.SH 这类格式")


def _get(url: str, **kwargs: Any) -> requests.Response:
    try:
        return requests.get(url, headers=HEADERS, timeout=10, **kwargs)
    except requests.RequestException as exc:
        raise QinglongError(f"数据源请求失败: {exc}") from exc


def _to_float(value: str) -> Optional[float]:
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _quote_raw(symbol: str) -> Dict[str, Any]:
    resp = _get(QUOTE_URL.format(symbols=symbol))
    resp.encoding = "gbk"
    match = re.search(r'v_%s="([^"]*)"' % re.escape(symbol), resp.text)
    if not match or not match.group(1):
        raise QinglongError(f"未找到 {symbol} 的行情数据，请确认代码是否正确")
    fields = match.group(1).split("~")
    if len(fields) < 40:
        raise QinglongError(f"{symbol} 行情字段不完整，可能已停牌或退市")

    def f(idx: int) -> Optional[float]:
        return _to_float(fields[idx]) if idx < len(fields) else None

    return {
        "symbol": symbol,
        "name": fields[1],
        "code": fields[2],
        "price": f(3),
        "prev_close": f(4),
        "open": f(5),
        "change": f(31),
        "change_percent": f(32),
        "high": f(33),
        "low": f(34),
        "volume_lots": f(6),
        "amount_10k_cny": f(37),
        "turnover_percent": f(38),
        "pe_ttm": f(39),
        "amplitude_percent": f(43),
        "market_cap_100m_cny": f(45),
        "pb": f(46),
        "limit_up": f(47) if len(fields) > 47 else None,
        "limit_down": f(48) if len(fields) > 48 else None,
        "quote_time": fields[30] if len(fields) > 30 else None,
        "currency": "CNY",
    }


def get_quote(code: str) -> Dict[str, Any]:
    """Real-time snapshot for one A-share ticker."""
    return _quote_raw(normalize_code(code))


def get_quotes(codes: List[str]) -> List[Dict[str, Any]]:
    """Real-time snapshots for up to 50 tickers (single upstream request)."""
    if not codes:
        raise QinglongError("codes 不能为空")
    if len(codes) > 50:
        raise QinglongError("单次最多查询 50 只股票")
    symbols = [normalize_code(c) for c in codes]
    resp = _get(QUOTE_URL.format(symbols=",".join(symbols)))
    resp.encoding = "gbk"
    out = []
    for sym in symbols:
        match = re.search(r'v_%s="([^"]*)"' % re.escape(sym), resp.text)
        if not match or not match.group(1):
            out.append({"symbol": sym, "error": "无数据"})
            continue
        out.append(_quote_raw(sym))
    return out


def get_kline(code: str, period: str = "day", count: int = 60, adjust: str = "qfq") -> Dict[str, Any]:
    """Historical OHLCV bars.

    period: day | week | month
    count: 1-320
    adjust: qfq (forward-adjusted) | hfq (backward) | none
    """
    if period not in _PERIODS:
        raise QinglongError(f"period 必须是 {sorted(_PERIODS)} 之一")
    count = max(1, min(int(count), 320))
    adjust = "" if adjust in ("none", "", None) else adjust
    if adjust not in ("qfq", "hfq", ""):
        raise QinglongError("adjust 必须是 qfq / hfq / none")

    symbol = normalize_code(code)
    params = {"param": f"{symbol},{period},,,{count},{adjust}"}
    resp = _get(KLINE_URL, params=params)
    try:
        payload = resp.json()
    except ValueError as exc:
        raise QinglongError("K线数据源返回了非 JSON 内容") from exc

    node = (payload.get("data") or {}).get(symbol) or {}
    key = f"{adjust}{period}" if adjust else period
    rows = node.get(key) or node.get(period) or []
    if not rows:
        raise QinglongError(f"未获取到 {symbol} 的 {period} K线数据")

    bars = []
    for row in rows:
        if len(row) < 6:
            continue
        bars.append(
            {
                "date": row[0],
                "open": _to_float(row[1]),
                "close": _to_float(row[2]),
                "high": _to_float(row[3]),
                "low": _to_float(row[4]),
                "volume_lots": _to_float(row[5]),
            }
        )
    return {
        "symbol": symbol,
        "period": period,
        "adjust": adjust or "none",
        "count": len(bars),
        "bars": bars,
    }


def search_stock(keyword: str, limit: int = 10) -> List[Dict[str, Any]]:
    """Fuzzy search A-share tickers by code, name or pinyin initials."""
    keyword = str(keyword).strip()
    if not keyword:
        raise QinglongError("keyword 不能为空")
    resp = _get(SEARCH_URL, params={"q": keyword, "t": "all"})
    resp.encoding = "gbk"
    match = re.search(r'v_hint="([^"]*)"', resp.text)
    if not match or not match.group(1):
        return []

    results = []
    for item in match.group(1).split("^"):
        parts = item.split("~")
        if len(parts) < 5 or parts[4] not in ("GP-A", "GP-B", "KCB", "CYB", "BJ"):
            continue
        name = parts[2]
        if "\\u" in name:
            try:
                name = json.loads(f'"{name}"')
            except ValueError:
                pass
        results.append(
            {
                "symbol": f"{parts[0]}{parts[1]}",
                "code": parts[1],
                "name": name,
                "pinyin": parts[3],
                "type": parts[4],
            }
        )
        if len(results) >= limit:
            break
    return results


def get_index_quotes() -> List[Dict[str, Any]]:
    """Major mainland index snapshots."""
    quotes = get_quotes(list(INDEX_CODES))
    for q in quotes:
        if "error" not in q:
            q["name"] = INDEX_CODES.get(q["symbol"], q["name"])
    return quotes


def health_check() -> Dict[str, Any]:
    """Verify the upstream quote endpoint is reachable."""
    started = time.time()
    get_quote("sh000001")
    return {"status": "healthy", "upstream": "qt.gtimg.cn", "latency_ms": round((time.time() - started) * 1000)}
