# 🚀 Stock MCP Server

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![MCP](https://img.shields.io/badge/MCP-Protocol-green.svg)](https://modelcontextprotocol.io/)

> **全球首个 WebMCP 原生 A 股股票数据服务**

让 AI Agent 实时获取 A 股行情，支持新浪财经 + 腾讯财经双数据源。

## ✨ 特性

- 🚀 **实时股价** - 毫秒级获取 A 股实时行情
- 🔄 **双数据源** - 新浪财经 + 腾讯财经，自动故障转移
- 🔌 **WebMCP 协议** - 下一代 AI 交互标准
- 🆓 **完全免费** - 开源，可自建服务器
- 📊 **批量查询** - 支持多只股票同时获取
- 🔍 **智能搜索** - 支持股票名称、代码模糊搜索

## 🎯 使用场景

- AI 投资助手
- 量化交易系统
- 股票分析机器人
- 个人投资工具

## 🚀 快速开始

### 安装

```bash
git clone https://github.com/laoniu/stock-mcp-server.git
cd stock-mcp-server
pip install -r requirements.txt
```

### 启动服务器

```bash
python3 stock_mcp_server_v2.py
```

服务启动在 http://localhost:5001

### API 调用示例

**获取茅台实时股价：**
```bash
curl -X POST http://localhost:5001/mcp/call \
  -H "Content-Type: application/json" \
  -d '{
    "tool": "get_stock_price",
    "args": {"symbol": "600519", "source": "sina"}
  }'
```

**返回示例：**
```json
{
  "tool": "get_stock_price",
  "result": {
    "symbol": "600519",
    "name": "贵州茅台",
    "price": 1745.00,
    "change": 15.00,
    "change_percent": 0.87,
    "volume": 1234567,
    "source": "sina"
  }
}
```

## 📚 API 文档

### 可用工具

| 工具名 | 描述 | 参数 |
|--------|------|------|
| `get_stock_price` | 获取单只股票实时价格 | `symbol`, `source`(可选) |
| `get_stock_batch` | 批量获取多只股票 | `symbols` (数组) |
| `search_stock` | 搜索股票 | `keyword` |

### 数据源

- **sina** (默认) - 新浪财经，稳定快速
- **qq** - 腾讯财经，备用数据源

## 🔧 技术栈

- **FastAPI** - 高性能 Web 框架
- **WebMCP** - Model Context Protocol
- **新浪财经/腾讯财经 API** - 实时数据源

## 🤝 参与贡献

欢迎 Issue 和 PR！

### 待办事项

- [ ] K 线历史数据
- [ ] 板块/行业数据
- [ ] 更多数据源（Tushare、同花顺）
- [ ] Docker 部署
- [ ] WebSocket 实时推送

## 📄 许可证

MIT License - 详见 [LICENSE](LICENSE) 文件

## 🙏 致谢

- [Model Context Protocol](https://modelcontextprotocol.io/)
- [Awesome MCP Servers](https://github.com/punkpeye/awesome-mcp-servers)
- 新浪财经、腾讯财经提供数据支持

---

**让 AI 投资变得更简单！** 🚀

如果这个项目对你有帮助，请给个 ⭐ Star！
