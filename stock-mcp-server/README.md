# 青龙 Stock MCP Server v4.4.0

[![Version](https://img.shields.io/badge/version-v4.4.0--FINAL-blue.svg)](https://github.com/niuheilong/stock-mcp-server/releases/tag/v4.4.0-FINAL)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Docker](https://img.shields.io/badge/Docker-Hub-2496ED?logo=docker&logoColor=white)](https://hub.docker.com/r/niuheilong/stock-mcp-server)
[![Python](https://img.shields.io/badge/Python-3.11+-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![MCP](https://img.shields.io/badge/MCP-Protocol-orange)](https://modelcontextprotocol.io/)
[![Glama](https://img.shields.io/badge/Glama.ai-Listed-6366f1)](https://glama.ai/mcp/servers/@niuheilong/stock-mcp-server)

实时A股股票数据 + 技术分析 + Chrome DevTools MCP + Token优化

> 🎯 **当前版本**: v4.4.0 FINAL (已固化)  
> 📖 [版本说明](VERSION_FINAL.md) | [版本选择指南](docs/VERSION_GUIDE.md) | [Token优化](docs/TOKEN_OPTIMIZATION.md)

## 🐉 功能特性

- ✅ **实时行情** - 腾讯财经API实时数据
- ✅ **技术分析** - MACD / KDJ / RSI / 均线趋势
- ✅ **舆情情绪分析** - 新闻情绪 + 社交媒体情绪 + 成交量情绪
- ✅ **资金流向分析** - 主力/散户/北向资金/大单动向
- ✅ **板块联动分析** - 板块热度 + 龙头识别 + 个股联动
- ✅ **历史回测** - 数据存储 + 胜率统计 + 评分验证
- ✅ **预警系统** - 价格/情绪/资金流向/板块异动预警 ⭐新增
- ✅ **青龙评分** - 综合多维度智能评分 (0-100)
- ✅ **自选股监控** - 7只核心股票持续跟踪

## 📊 自选股列表

| 代码 | 名称 | 市场 |
|-----|------|------|
| sh600410 | 华胜天成 | 上证 |
| sh600620 | 天宸股份 | 上证 |
| sh603986 | 兆易创新 | 上证 |
| sh688525 | 佰维存储 | 科创板 |
| sz002261 | 拓维信息 | 深证 |
| sz300428 | 立中集团 | 创业板 |
| sh688629 | 华丰科技 | 科创板 |

## 🚀 快速开始

### Docker运行（推荐）
```bash
# 从 Docker Hub 拉取并运行
docker run -d \
  --name stock-mcp-server \
  -p 8000:8000 \
  --restart unless-stopped \
  niuheilong/stock-mcp-server:latest
```

或者本地构建：
```bash
docker build -t qinglong-stock .
docker run -p 8000:8000 qinglong-stock
```

### 本地运行
```bash
pip install -r requirements.txt
python server.py
```

## 📡 API接口

### 基础接口
- `GET /` - 服务状态
- `GET /health` - 健康检查
- `GET /watchlist` - 自选股列表

### 股票分析
- `GET /stock/{code}` - 完整分析报告
- `GET /stock/{code}/data` - 基础数据
- `GET /stock/{code}/technical` - 技术分析
- `GET /stock/{code}/sentiment` - 舆情情绪分析
- `GET /stock/{code}/capitalflow` - 资金流向分析
- `GET /stock/{code}/sector` - 板块联动分析

### 板块分析
- `GET /sectors/hot` - 热门板块排名
- `GET /sectors/{sector_code}/stocks` - 板块成分股

### 历史回测
- `POST /history/save/{code}` - 保存分析到历史记录
- `GET /history/{code}` - 获取历史分析记录
- `GET /backtest/{code}` - 获取回测报告

### 预警系统 ⭐新增
- `GET /alerts/rules` - 获取预警规则列表
- `POST /alerts/rules` - 创建预警规则
- `DELETE /alerts/rules/{rule_id}` - 删除预警规则
- `GET /alerts/events` - 获取预警事件历史
- `POST /alerts/check/{code}` - 手动检查预警

### 批量分析
- `GET /batch/analysis` - 批量分析所有自选股并排序

## 📈 青龙评分体系 v4.4

| 维度 | 权重 | 说明 |
|-----|------|------|
| 技术面 | 20% | MACD/KDJ/RSI/趋势 |
| 情绪面 | 25% | 新闻+社交+成交量情绪 |
| 资金流向 | 25% | 主力/散户/北向资金 |
| 板块联动 | 20% | 板块热度/龙头/跟风 |
| 基本面 | 10% | PE/PB/涨跌幅 |

### 评分等级
- **80-100**: 强烈推荐
- **60-79**: 推荐
- **40-59**: 中性
- **20-39**: 谨慎
- **0-19**: 回避

## 🔔 预警系统

### 预警类型
- **价格变动** - 涨跌幅突破阈值
- **价格突破** - 达到指定价格
- **成交量异动** - 成交量异常放大
- **情绪极值** - 情绪指数过高/过低
- **资金流向背离** - 资金与价格背离
- **板块龙头** - 成为板块领涨股
- **评分变化** - 青龙评分大幅变化
- **技术信号** - RSI超买超卖等

### 预警等级
- **ℹ️ 提示** (INFO) - 一般信息
- **⚠️ 警告** (WARNING) - 需要关注
- **🚨 严重** (CRITICAL) - 立即处理

### 使用方法
```bash
# 1. 创建预警规则
curl -X POST http://localhost:8000/alerts/rules \
  -H "Content-Type: application/json" \
  -d '{
    "id": "price_up_5",
    "name": "价格上涨5%",
    "code": "sh600410",
    "alert_type": "price_change",
    "level": "warning",
    "threshold_value": 5.0,
    "threshold_direction": "above"
  }'

# 2. 查看预警规则
curl http://localhost:8000/alerts/rules

# 3. 手动检查预警
curl -X POST http://localhost:8000/alerts/check/sh600410

# 4. 查看预警事件历史
curl http://localhost:8000/alerts/events
```

## 📊 历史回测框架

### 数据存储
- **SQLite数据库** - 轻量级本地存储
- **自动归档** - 每次分析自动保存
- **字段完整** - 价格、评分、资金流向、板块信息

### 回测指标
- **胜率统计** - 1日/3日/5日/10日胜率
- **平均收益** - 各周期平均收益率
- **最大回撤** - 各周期最大回撤
- **评分准确性** - 评分与实际收益相关性
- **建议有效性** - 不同建议类型的胜率

## 🏭 板块联动分析

### 分析维度
- **板块热度** - 行业板块涨跌幅排名
- **龙头识别** - 板块内领涨股识别
- **跟风分析** - 识别跟风股和滞后股
- **相关性评分** - 个股与板块联动强度

## 💰 资金流向分析

### 分析维度
- **主力资金** - 主力净流入/流出金额和占比
- **散户资金** - 散户净流入/流出 (反向指标)
- **大单动向** - 大单/中单/小单分布
- **北向资金** - 沪深港通持股和流向
- **融资融券** - 融资余额变化

## 🧠 舆情情绪分析

### 情绪等级
- **极度恐慌** (0-20) - 或是布局良机
- **恐慌** (20-40) - 可能存在错杀机会
- **中性** (40-60) - 观望为主
- **贪婪** (60-80) - 保持理性
- **极度贪婪** (80-100) - 警惕回调风险

## 🎯 产品版本

| 版本 | 价格 | 适用人群 | 功能亮点 |
|-----|------|---------|---------|
| [玩票版](docs/VERSION_GUIDE.md) | 免费 | 小白/学习者 | 基础查询+技术分析 |
| **[基础版](docs/VERSION_GUIDE.md)** ⭐当前 | 免费 | 普通散户 | +资金流向+板块分析 |
| [订阅版](docs/VERSION_GUIDE.md) | ¥29/月 | 活跃投资者 | +实时数据+新闻舆情+预警 |
| [专业版](docs/VERSION_GUIDE.md) | ¥199/月 | 专业投资者 | +Level-2+量化回测+API |
| [定制版](docs/VERSION_GUIDE.md) | 定制 | 机构/券商 | 私有化+定制开发 |

👉 [如何选择适合你的版本？](docs/VERSION_GUIDE.md)

## 📝 更新日志

### v4.4.0 (2026-03-17) ⭐当前版本
- ✅ **新增预警系统** - 多维度实时监控
- ✅ **新增8种预警类型** - 价格/情绪/资金/板块
- ✅ **新增3级预警等级** - INFO/WARNING/CRITICAL
- ✅ **新增预警API端点** - `/alerts/*`
- ✅ **新增冷却时间机制** - 防止重复预警

### v4.3.0 (2026-03-17)
- ✅ 新增历史回测框架 - SQLite数据存储
- ✅ 新增回测计算引擎 - 胜率/收益/回撤统计
- ✅ 新增评分验证 - 验证青龙评分准确性

### v4.2.0 (2026-03-17)
- ✅ 新增板块联动分析模块
- ✅ 新增板块热度排名
- ✅ 新增龙头识别

### v4.1.0 (2026-03-17)
- ✅ 新增资金流向分析模块
- ✅ 新增北向资金监控
- ✅ 新增主力资金分析

### v4.0.0 (2026-03-17)
- ✅ 新增舆情情绪分析模块
- ✅ 新增青龙综合评分系统

## 🔮 未来计划

- [ ] WebSocket实时推送
- [ ] 概念板块分析
- [ ] 地区板块分析
- [ ] 邮件/短信通知
- [ ] 定时任务调度

## 📄 许可证

MIT
