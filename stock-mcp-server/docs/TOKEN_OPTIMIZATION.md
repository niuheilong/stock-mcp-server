# 青龙 Token 优化策略
# 目标: 低成本 + 高效 + 准确

---

## 🎯 核心原则

1. **本地处理优先** - 能用代码解决就不用 LLM
2. **缓存复用** - 避免重复请求
3. **批量处理** - 减少调用次数
4. **精准提问** - 减少无效 Token

---

## 💰 成本对比

| 操作 | Token 消耗 | 成本等级 | 优化方案 |
|-----|-----------|---------|---------|
| Chrome MCP 抓取 | ~0 | 💚 免费 | 多用 |
| API 数据获取 | ~100 | 💛 低 | 缓存 |
| LLM 简单分析 | ~500 | 💛 低 | 批量 |
| LLM 深度分析 | ~2000 | ❤️ 高 | 按需 |
| 图片/文档分析 | ~3000+ | ❤️ 高 | 压缩 |

---

## 🚀 优化策略

### 1. 数据抓取层 (零成本)

```python
# ✅ 推荐: Chrome MCP 本地抓取
# 成本: 0 Token
# 效率: ⭐⭐⭐⭐⭐
chrome.execute_js("document.title")  # 免费

# ❌ 避免: 用 LLM 解析网页
# 成本: 2000+ Token
# 效率: ⭐⭐
```

**策略**:
- 股票数据 → Chrome MCP 抓取 (东方财富)
- 新闻资讯 → API 获取 (RSS/新闻API)
- 只有分析时才用 LLM

---

### 2. 缓存层 (减少 80% 重复请求)

```python
# 缓存配置
CACHE_TTL = {
    "stock_price": 60,      # 股价缓存 60 秒
    "stock_detail": 300,    # 详情缓存 5 分钟
    "news": 600,           # 新闻缓存 10 分钟
    "analysis": 3600,      # 分析结果缓存 1 小时
}
```

**策略**:
- 相同股票 1 分钟内不重复抓取
- 分析结果缓存，避免重复计算
- 使用 SQLite 本地存储

---

### 3. 批量处理层 (减少 70% 调用次数)

```python
# ❌ 低效: 逐个分析
for code in stocks:
    analyze_with_llm(code)  # 5次调用

# ✅ 高效: 批量分析
analyze_batch_with_llm(stocks)  # 1次调用
```

**策略**:
- 多只股票一起分析
- 合并相似请求
- 使用子会话并行处理

---

### 4. 精准提问层 (减少 50% 无效 Token)

```python
# ❌ 低效: 模糊提问
"分析这只股票"  # Token 浪费

# ✅ 高效: 精准提问
"华胜天成(sh600410): 价格27.50, 涨跌+3.38%, 
成交量放大, 板块军工电子+2.62%。
问: 明天走势预测? 支撑位?"  # 精准高效
```

**策略**:
- 提供结构化数据
- 明确问题边界
- 使用模板化提示词

---

## 📋 具体实施方案

### 方案 A: 实时数据抓取 (零成本)

```python
# chrome_mcp_optimized.py
import time
from functools import lru_cache

class OptimizedStockScraper:
    def __init__(self):
        self.cache = {}
        self.cache_time = {}
    
    @lru_cache(maxsize=128)
    def get_stock_basic(self, code):
        """获取基本信息 - 缓存 5 分钟"""
        return self._fetch_from_chrome(code)
    
    def get_stock_realtime(self, code):
        """获取实时数据 - 缓存 1 分钟"""
        now = time.time()
        if code in self.cache:
            if now - self.cache_time[code] < 60:
                return self.cache[code]
        
        data = self._fetch_from_chrome(code)
        self.cache[code] = data
        self.cache_time[code] = now
        return data
    
    def _fetch_from_chrome(self, code):
        """Chrome MCP 抓取 - 零 Token"""
        # ... 抓取代码 ...
        pass
```

### 方案 B: 智能分析触发 (按需使用 LLM)

```python
# 触发条件
ANALYSIS_TRIGGER = {
    "price_change": 5,      # 价格变动 > 5%
    "volume_spike": 3,      # 成交量放大 3 倍
    "news_alert": True,     # 重大新闻
    "user_request": True,   # 用户主动请求
}

def should_analyze(stock_data):
    """判断是否需要 LLM 分析"""
    if stock_data['change_percent'] > 5:
        return True, "价格大幅变动"
    if stock_data['volume_ratio'] > 3:
        return True, "成交量异常"
    return False, "无需分析"
```

### 方案 C: 批量 LLM 调用

```python
# 批量分析模板
BATCH_ANALYSIS_PROMPT = """
分析以下 {count} 只股票，每只给出: 趋势/支撑/阻力/建议

数据:
{stock_data_formatted}

要求:
1. 简洁回答，每只股票不超过 50 字
2. 使用结构化格式
3. 优先看技术指标
"""

def analyze_batch(stocks_data):
    """批量分析 - 1 次调用替代 N 次"""
    prompt = BATCH_ANALYSIS_PROMPT.format(
        count=len(stocks_data),
        stock_data_formatted=format_stocks(stocks_data)
    )
    return llm_call(prompt)  # 1 次调用
```

---

## 📊 预期效果

| 指标 | 优化前 | 优化后 | 节省 |
|-----|-------|-------|------|
| 单次股票分析 | 2000 Token | 200 Token | 90% |
| 日调用次数 | 100 次 | 20 次 | 80% |
| 月 Token 消耗 | 6M | 600K | 90% |
| 响应速度 | 5s | 1s | 80% |

---

## 🛠️ 实施计划

### Phase 1: 立即实施 (今天)
- [ ] 启用 Chrome MCP 缓存
- [ ] 实现批量分析
- [ ] 添加触发条件

### Phase 2: 本周完成
- [ ] SQLite 缓存持久化
- [ ] 智能分析调度
- [ ] Token 使用监控

### Phase 3: 持续优化
- [ ] 根据使用数据调整策略
- [ ] A/B 测试不同方案
- [ ] 自动化成本报告

---

## 💡 省钱技巧

1. **抓取用 Chrome MCP** (免费)
2. **缓存一切能缓存的** (减少重复)
3. **批量处理** (减少调用次数)
4. **精准提问** (减少无效 Token)
5. **本地计算** (能用代码不用 LLM)

---

*策略版本: v1.0*
*创建时间: 2026-03-18*
*目标: 成本降低 90%，效率提升 80%*
