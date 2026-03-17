# Stock MCP Server

青龙 - 实时A股股票数据 MCP 服务器

## 功能

- 实时股票数据查询
- 支持A股市场
- MCP协议兼容
- Docker部署

## 快速开始

```bash
docker run -p 8000:8000 niuheilong/stock-mcp-server
```

## API

- `GET /` - 服务状态
- `GET /health` - 健康检查
- `GET /stock/{code}` - 股票数据

## 技术栈

- Python 3.11
- FastAPI
- Docker

## 许可证

MIT
