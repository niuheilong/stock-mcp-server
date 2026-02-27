# Smart ROI Calculator 集成文档

## 概述

Smart ROI Calculator 借鉴 **bounty-hunter-skill** 的 Smart ROI 系统，为 Stock MCP Server 添加量化投资决策能力。

## 核心特性

### 🎯 Smart ROI 算法
```
ROI = (预期收益 × 成功概率) / (时间成本 + 资金成本 × 风险系数)
```

借鉴 bounty-hunter-skill 的自动决策逻辑，实现股票投资的量化评估。

### 📊 功能模块

| 模块 | 文件 | 功能 |
|------|------|------|
| 核心计算器 | `smart_roi_calculator.py` | ROI 计算引擎 |
| MCP 工具封装 | `smart_roi_integration.py` | API 接口定义 |
| 服务器集成 | `stock_mcp_server_enhanced.py` | 完整集成 |

## API 使用

### 1. 计算单只股票 ROI

```bash
curl -X POST http://localhost:5001/mcp/call \
  -H "Content-Type: application/json" \
  -d '{
    "tool": "calculate_stock_roi",
    "args": {
      "code": "002156",
      "name": "通富微电",
      "price": 52.01,
      "strategy": "趋势跟踪",
      "expected_return": 0.08,
      "probability": 0.75,
      "risk_level": "medium",
      "time_horizon": "short"
    }
  }'
```

**返回示例：**
```json
{
  "tool": "calculate_stock_roi",
  "result": {
    "success": true,
    "data": {
      "should_trade": true,
      "roi_score": 8.33,
      "expected_profit": 416.08,
      "total_cost": 49.98,
      "confidence": "极高",
      "rationale": "ROI优秀(8.33)；成功率较高(75%)；风险可控；短期见效",
      "recommendation": "【强烈推荐】通富微电(002156) ROI 8.3，建议重仓参与"
    }
  }
}
```

### 2. 批量分析关注列表

```bash
curl -X POST http://localhost:5001/mcp/call \
  -H "Content-Type: application/json" \
  -d '{
    "tool": "analyze_watchlist_roi",
    "args": {
      "watchlist": [
        {
          "code": "002156",
          "name": "通富微电",
          "price": 52.01,
          "strategy": "趋势跟踪",
          "expected_return": 0.08,
          "probability": 0.75,
          "risk_level": "medium"
        },
        {
          "code": "003029",
          "name": "金富科技",
          "price": 15.85,
          "strategy": "突破买入",
          "expected_return": 0.05,
          "probability": 0.70,
          "risk_level": "low"
        }
      ]
    }
  }'
```

## 参数说明

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| code | string | ✅ | 股票代码 |
| name | string | ✅ | 股票名称 |
| price | number | ✅ | 当前价格 |
| strategy | string | ✅ | 投资策略 |
| expected_return | number | ✅ | 预期收益率（如 0.05 表示 5%） |
| probability | number | ✅ | 成功概率（0-1） |
| risk_level | string | ✅ | 风险等级：low/medium/high |
| time_horizon | string | ❌ | 时间周期：short/medium/long（默认 medium） |

## ROI 决策逻辑

### 阈值配置
```python
MIN_ROI_THRESHOLD = 1.5      # 最低 ROI 150%
MIN_PROBABILITY = 0.6        # 最低成功率 60%
MAX_RISK_ACCEPTANCE = 0.3    # 最大可接受风险 30%
```

### 风险系数
```python
RISK_MULTIPLIERS = {
    "low": 1.0,
    "medium": 1.5,
    "high": 2.5
}
```

### 置信度等级
| 得分 | 等级 | 说明 |
|------|------|------|
| ≥ 3.0 | 极高 | 强烈推荐 |
| ≥ 2.0 | 高 | 推荐参与 |
| ≥ 1.5 | 中 | 可考虑 |
| < 1.5 | 低 | 观望 |

## 成本计算

### 时间成本
- 短期（short）：0.5 小时 × 50元/小时 = 25元
- 中期（medium）：2 小时 × 50元/小时 = 100元
- 长期（long）：5 小时 × 50元/小时 = 250元

### 资金成本（每手 100 股）
```
手续费 = 股价 × 100 × 0.03% × 2（买卖）
印花税 = 股价 × 100 × 0.1%（卖出）
总资金成本 = 手续费 + 印花税
```

## 实际应用场景

### 场景 1：自动晨报 ROI 筛选
```python
# 扫描所有持仓
for stock in holdings:
    roi = calculate_roi(stock)
    if roi['should_trade']:
        morning_report.add_opportunity(roi)
```

### 场景 2：实时交易提醒
```python
# 实时监控
if price_change > threshold:
    roi = calculate_roi(stock, new_probability)
    if roi['roi_score'] > 3.0:
        send_alert(roi['recommendation'])
```

### 场景 3：投资组合优化
```python
# 批量分析
results = analyze_batch(watchlist)
# 按 ROI 排序，选择前 N 名
best_opportunities = results[:5]
```

## 版本历史

- **v3.1.0** (2026-02-28)
  - ✅ 集成 Smart ROI Calculator
  - ✅ 添加 calculate_stock_roi 工具
  - ✅ 添加 analyze_watchlist_roi 工具
  - ✅ 借鉴 bounty-hunter-skill ROI 系统

## 致谢

本项目 Smart ROI 系统灵感来源于 **bounty-hunter-skill** 项目，感谢其开源的 Smart ROI 决策框架。

---

**Stock MCP Server v3.1.0 - 量化投资决策支持** 🚀
