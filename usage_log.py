#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
轻量使用统计
============
把每次工具调用追加到本地 JSONL 日志，并可按天汇总。

- 日志路径：环境变量 STOCK_MCP_USAGE_LOG，默认 ~/.stock-mcp-server/usage.jsonl
- 隐私：只记「时间戳 + 工具名 + 是否成功」，**不记任何调用参数 / 用户身份**
- 健壮性：统计失败绝不影响工具主流程（全部 try/except 吞掉）
"""

import datetime as dt
import json
import os

_LOG_PATH = os.environ.get("STOCK_MCP_USAGE_LOG") or os.path.expanduser(
    "~/.stock-mcp-server/usage.jsonl"
)


def log_path() -> str:
    return _LOG_PATH


def record(tool: str, ok: bool = True) -> None:
    """记录一次工具调用（best-effort，永不抛错）。"""
    try:
        os.makedirs(os.path.dirname(_LOG_PATH), exist_ok=True)
        with open(_LOG_PATH, "a", encoding="utf-8") as f:
            f.write(
                json.dumps(
                    {
                        "ts": dt.datetime.now().isoformat(timespec="seconds"),
                        "tool": tool,
                        "ok": bool(ok),
                    },
                    ensure_ascii=False,
                )
                + "\n"
            )
    except Exception:  # noqa: BLE001
        pass


def summary(days: int = 7) -> dict:
    """汇总最近 N 天的调用情况。"""
    since = dt.datetime.now() - dt.timedelta(days=days)
    total = errors = 0
    by_tool: dict = {}
    by_day: dict = {}

    if os.path.exists(_LOG_PATH):
        with open(_LOG_PATH, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    rec = json.loads(line)
                    ts = dt.datetime.fromisoformat(rec["ts"])
                except Exception:  # noqa: BLE001
                    continue
                if ts < since:
                    continue
                tool = rec.get("tool", "?")
                total += 1
                by_tool[tool] = by_tool.get(tool, 0) + 1
                day = ts.date().isoformat()
                by_day[day] = by_day.get(day, 0) + 1
                if not rec.get("ok", True):
                    errors += 1

    return {
        "period_days": days,
        "log_file": _LOG_PATH,
        "total_calls": total,
        "errors": errors,
        "by_tool": dict(sorted(by_tool.items(), key=lambda kv: -kv[1])),
        "by_day": dict(sorted(by_day.items())),
    }
