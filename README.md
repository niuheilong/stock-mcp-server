# 📈 Stock MCP Server - 青龙

[![Docker](https://img.shields.io/badge/docker-ready-blue.svg)](https://hub.docker.com/r/niuheilong/stock-mcp-server)
[![Python](https://img.shields.io/badge/python-3.11-green.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-009688.svg)](https://fastapi.tiangolo.com/)
[![License](https://img.shields.io/badge/license-MIT-yellow.svg)](LICENSE)

> 🐉 **青龙** - 实时A股股票数据 MCP 服务器

基于 MCP (Model Context Protocol) 协议的股票数据服务，为 AI 助手提供实时、准确的 A 股市场数据。

## ✨ 核心功能

- 📊 **实时行情** - 股票实时价格、涨跌幅、成交量
- 📈 **K线数据** - 日K、周K、月K历史数据
- 💰 **财务指标** - PE、PB、市值、营收等关键指标
- 🏢 **板块资金** - 行业资金流向、龙头股追踪
- 🔍 **智能搜索** - 股票代码、名称模糊搜索
- 🎯 **数据验证** - 多源数据交叉验证，确保准确性

## 🚀 快速开始

### Docker 部署（推荐）

```bash
docker run -d \
  --name stock-mcp-server \
  -p 8000:8000 \
  --restart unless-stopped \
  niuheilong/stock-mcp-server:latest
```

### 本地运行

```bash
# 克隆仓库
git clone https://github.com/niuheilong/stock-mcp-server.git
cd stock-mcp-server

# 安装依赖
pip install -r requirements.txt

# 启动服务
python main.py
```

## 📡 MCP 工具列表

| 工具名称 | 功能描述 | 示例 |
|---------|---------|------|
| `get_stock_price` | 获取股票实时价格 | `000001` (平安银行) |
| `get_stock_kline` | 获取K线数据 | `000001`, `day`, `30` |
| `get_stock_financial` | 获取财务指标 | `000001` |
| `get_sector_fund_flow` | 获取板块资金流向 | `industry` |
| `search_stock` | 搜索股票 | `平安` |

## 🔌 接入 Claude/Cursor

### Claude Desktop 配置

编辑 `~/Library/Application Support/Claude/claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "stock": {
      "command": "docker",
      "args": [
        "run",
        "-i",
        "--rm",
        "-p", "8000:8000",
        "niuheilong/stock-mcp-server:latest"
      ]
    }
  }
}
```

### Cursor 配置

在 Cursor Settings > MCP 中添加：

```
Name: stock
Type: stdio
Command: docker run -i --rm -p 8000:8000 niuheilong/stock-mcp-server:latest
```

## 💡 使用示例

**查询股票实时数据：**
```
用户：分析一下贵州茅台
AI：我来获取贵州茅台(600519)的实时数据...

当前价格：1,680.00 元
涨跌幅：+2.35% (+38.50元)
成交量：12.5万手
成交额：21.0亿元
PE(TTM)：28.5
总市值：2.11万亿
```

**查询板块资金流向：**
```
用户：今天哪些板块资金流入最多？
AI：我来查询今日板块资金流向...

1. 半导体：+45.2亿 💰
2. 新能源：+38.7亿 💰
3. 医药生物：+22.1亿 💰
```

## 🏗️ 架构设计

```
┌─────────────────┐
│   MCP Client    │  <- Claude/Cursor/其他AI
│  (AI Assistant) │
└────────┬────────┘
         │ MCP Protocol
         ▼
┌─────────────────┐
│  Stock MCP      │  <- 本服务
│  Server         │
└────────┬────────┘
         │ HTTP/WebSocket
         ▼
┌─────────────────┐
│  Data Sources   │  <- 腾讯/东方财富/新浪
│  (Multi-Source) │     多源数据交叉验证
└─────────────────┘
```

## 🎯 数据准确性保障

- ✅ **多源验证** - 同时从腾讯、东方财富、新浪获取数据
- ✅ **实时更新** - 交易时间实时同步交易所数据
- ✅ **异常检测** - 自动识别并剔除异常数据
- ✅ **缓存策略** - 合理缓存，平衡实时性与稳定性

## 📝 更新日志

### v1.0.0 (2026-03-19)
- 🎉 首次发布
- ✅ 支持实时股票数据查询
- ✅ 支持K线数据获取
- ✅ 支持财务指标查询
- ✅ 支持板块资金流向
- ✅ Docker 一键部署

## 🤝 贡献指南

欢迎提交 Issue 和 PR！

1. Fork 本仓库
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 创建 Pull Request

## 📄 许可证

MIT License - 详见 [LICENSE](LICENSE) 文件

## 🙏 鸣谢

- [MCP Protocol](https://modelcontextprotocol.io/) - 模型上下文协议
- [FastAPI](https://fastapi.tiangolo.com/) - 高性能Web框架
- [Docker](https://www.docker.com/) - 容器化部署

---

⭐ **如果这个项目对你有帮助，请点个 Star 支持一下！**

📧 有问题或建议？欢迎提交 [Issue](https://github.com/niuheilong/stock-mcp-server/issues)

🐉 **青龙 - 让 AI 更懂中国股市**
