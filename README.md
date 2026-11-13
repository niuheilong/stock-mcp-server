# 🐉 Qinglong — Real-time A-share data MCP server

[![License](https://img.shields.io/badge/license-MIT-yellow.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.10+-green.svg)](https://www.python.org/)
[![MCP](https://img.shields.io/badge/MCP-compatible-orange.svg)](https://modelcontextprotocol.io/)

Give any MCP-capable AI agent — Claude Code, Cursor, Codex CLI, VS Code, Windsurf,
Cline, Zed — live access to mainland China A-share market data.

**Chinese version below · [中文说明](#中文说明)**

## What it does

| Tool | Returns |
|---|---|
| `get_stock_quote` | Real-time snapshot: price, change %, high/low, volume, amount, turnover, PE, PB, market cap, limit-up/down |
| `get_stock_quotes` | Snapshots for up to 50 tickers in one call |
| `get_stock_kline` | Daily / weekly / monthly OHLCV bars, forward- or backward-adjusted, 1–320 bars |
| `search_stock` | Look up tickers by code, Chinese name or pinyin initials (`平安`, `600519`, `payh`) |
| `get_market_indices` | SSE Composite, SZSE Component, ChiNext, STAR 50, CSI 300 |
| `check_data_source` | Upstream reachability / latency check |

Data comes from Tencent Finance's public quote endpoints, delayed by seconds. There is
**no fabricated data**: if an upstream call fails, the tool returns an error instead of
inventing numbers.

## Install

Requirements: Python 3.10+ and [uv](https://docs.astral.sh/uv/).

```bash
# run straight from GitHub, no checkout needed
uvx --from git+https://github.com/niuheilong/stock-mcp-server qinglong-mcp
```

Or install locally:

```bash
git clone https://github.com/niuheilong/stock-mcp-server.git
cd stock-mcp-server
uv sync          # or: pip install -e .
qinglong-mcp
```

## Connect your agent

### Claude Code

```bash
claude mcp add qinglong -- uvx --from git+https://github.com/niuheilong/stock-mcp-server qinglong-mcp
```

### Cursor / Windsurf / Cline / VS Code (`.mcp.json` or MCP settings)

```json
{
  "mcpServers": {
    "qinglong": {
      "command": "uvx",
      "args": ["--from", "git+https://github.com/niuheilong/stock-mcp-server", "qinglong-mcp"]
    }
  }
}
```

### Claude Desktop (`claude_desktop_config.json`)

```json
{
  "mcpServers": {
    "qinglong": {
      "command": "uvx",
      "args": ["--from", "git+https://github.com/niuheilong/stock-mcp-server", "qinglong-mcp"]
    }
  }
}
```

### HTTP mode (shared server)

```bash
docker build -t qinglong-mcp .
docker run -p 8000:8000 qinglong-mcp
# endpoint: http://localhost:8000/mcp
```

## Example

> **User:** How is Kweichow Moutai doing today?

```
get_stock_quote("600519")
→ price 1,680.00 CNY, +2.35% (+38.50), high 1,692.00, low 1,641.10
  volume 125,000 lots, amount 2.10B CNY, turnover 0.42%
  PE(TTM) 28.5, PB 8.1, market cap 21,100亿 CNY
```

> **User:** Show me the last 5 trading days for 华胜天成.

```
get_stock_kline("600410", period="day", count=5)
→ 2026-11-13  open 13.40  close 14.30  high 14.30  low 12.88  volume 1,789,255 lots
  ...
```

## Ticker formats

All of these are accepted: `600410`, `sh600410`, `600410.SH`.
Shanghai starts with 6, Shenzhen with 0/2/3, Beijing with 4/8.

## Data source & limitations

- Source: `qt.gtimg.cn` and `web.ifzq.gtimg.cn` (Tencent Finance), public endpoints.
- Quotes are real-time-ish but not exchange-grade; treat them as research data.
- Beijing Stock Exchange coverage depends on the upstream endpoint.
- Not affiliated with Tencent. For research and educational use only.
- **This is not investment advice.**

## Development

```bash
uv sync
uv run python -c "from qinglong import api; print(api.get_quote('600519'))"
uv run python -m qinglong.server          # stdio
uv run python -m qinglong.server --transport http --port 8000
```

## License

MIT — see [LICENSE](LICENSE).

---

## 中文说明

**青龙**：给 AI 助手提供实时 A 股数据的 MCP 服务器。

- 实时行情、多股批量快照、日/周/月 K 线（前复权/后复权）、股票搜索、大盘指数
- 只使用真实上游数据，**不做任何模拟或推算**：取不到数据就报错，不编造
- 数据源为腾讯财经公开接口，有秒级延迟，仅供研究，不构成投资建议

```bash
claude mcp add qinglong -- uvx --from git+https://github.com/niuheilong/stock-mcp-server qinglong-mcp
```

如果这个项目对你有帮助，欢迎点个 Star ⭐
