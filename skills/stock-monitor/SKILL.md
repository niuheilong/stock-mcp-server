# stock-monitor - 青龙股票监控

青龙股票分析与监控系统 - 实时行情、技术分析、舆情情绪分析

## 功能

- 实时A股股票数据查询
- 技术分析 (MACD/KDJ/RSI)
- 舆情情绪分析
- 青龙综合评分
- 自选股批量监控

## 安装

```bash
# 进入项目目录
cd ~/projects/stock-mcp-server

# 安装依赖
pip install -r requirements.txt

# 启动服务
python server.py
```

## 使用

### 启动青龙服务
```bash
cd /Users/laoniu/.openclaw/workspace/stock-mcp-server
python server.py
```

### API调用示例

```bash
# 获取单只股票分析
curl http://localhost:8000/stock/sh600410

# 获取技术分析
curl http://localhost:8000/stock/sh600410/technical

# 获取舆情情绪分析
curl http://localhost:8000/stock/sh600410/sentiment

# 批量分析所有自选股
curl http://localhost:8000/batch/analysis
```

## 自选股列表

| 代码 | 名称 |
|-----|------|
| sh600410 | 华胜天成 |
| sh600620 | 天宸股份 |
| sh603986 | 兆易创新 |
| sh688525 | 佰维存储 |
| sz002261 | 拓维信息 |
| sz300428 | 立中集团 |
| sh688629 | 华丰科技 |

## 青龙评分体系

- 技术面: 30% (MACD/KDJ/RSI)
- 情绪面: 40% (新闻+社交+成交量)
- 基本面: 30% (PE/PB/涨跌幅)

评分等级:
- 80-100: 强烈推荐
- 60-79: 推荐
- 40-59: 中性
- 20-39: 谨慎
- 0-19: 回避

## 版本

v4.0.0 - 新增舆情情绪分析模块

## 作者

牛黑龙
