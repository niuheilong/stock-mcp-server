# 青龙 Stock MCP Server - API配置指南

本文档说明如何配置和扩展各种数据源API。

---

## 📊 当前集成的API

### 1. 腾讯财经API (已集成)
**用途**: 基础股票数据（价格、成交量、基本信息）

**端点**:
```
http://qt.gtimg.cn/q={code}
```

**代码格式**:
- 上证: `sh600410` → `sh600410`
- 深证: `sz002261` → `sz002261`

**数据字段** (参考 `server.py` 中的 `fetch_stock_data_tencent` 函数):
- 价格、涨跌幅、成交量、市值、PE/PB等

**限制**:
- 免费，无需认证
- 数据有延迟（约15分钟）
- 无历史数据

---

### 2. 东方财富API (已集成)
**用途**: 资金流向数据（主力、散户、北向资金）

**端点**:
```
http://push2.eastmoney.com/api/qt/stock/get?secid={prefix}.{code}&fields={fields}
```

**代码前缀**:
- 上证: `1` (如: `1.600410`)
- 深证: `0` (如: `0.002261`)

**数据字段** (参考 `capital_flow.py` 中的 `FIELDS` 字典):

| 字段代码 | 说明 | 字段代码 | 说明 |
|---------|------|---------|------|
| f43 | 最新价 | f136 | 主力净流入 |
| f44 | 开盘价 | f137 | 主力买入 |
| f45 | 最高价 | f138 | 主力卖出 |
| f46 | 最低价 | f139 | 散户净流入 |
| f47 | 成交量 | f140 | 散户买入 |
| f48 | 成交额 | f141 | 散户卖出 |
| f57 | 股票代码 | f142 | 大单净流入 |
| f58 | 股票名称 | f143 | 中单净流入 |
| f60 | 昨收 | f144 | 小单净流入 |
| f162 | 市盈率 | f178 | 主力历史流向(JSON) |
| f167 | 市净率 | f184 | 北向净流入 |
| f168 | 换手率 | f185 | 北向持股数量 |
| f116 | 总市值 | f186 | 北向持股占比 |
| f127 | 所属行业 | f187 | 融资余额 |
| f128 | 所属地区 | f188 | 融资买入 |
| f129 | 概念题材 | f189 | 融资偿还 |

**限制**:
- 免费，无需认证
- 可能有请求频率限制
- 字段含义可能随时间变化

---

## 🔧 可扩展的API

### 3. 新浪财经API (待集成)
**用途**: 实时行情、新闻、公告

**端点示例**:
```
https://hq.sinajs.cn/list=sh600410
https://finance.sina.com.cn/realstock/company/sh600410/nc.shtml
```

**集成步骤**:
1. 在 `server.py` 中添加 `fetch_stock_data_sina(code)` 函数
2. 解析返回的JavaScript格式数据
3. 统一转换为 `StockData` 模型

---

### 4. 雪球API (待集成)
**用途**: 社交媒体情绪、投资者讨论热度

**端点示例**:
```
https://stock.xueqiu.com/v5/stock/f10/cn/skratio.json?symbol=SH600410
https://stock.xueqiu.com/v5/stock/ten/volume.json?symbol=SH600410
```

**注意**:
- 需要Cookie/Token认证
- 需要反爬虫处理

**集成步骤**:
1. 注册雪球账号获取Cookie
2. 在 `sentiment.py` 中添加 `fetch_xueqiu_sentiment()` 函数
3. 设置请求头模拟浏览器

---

### 5. 同花顺API (待集成)
**用途**: 龙虎榜、机构调研、盈利预测

**端点示例**:
```
http://basic.10jqka.com.cn/api/stockph/lhbph/600410
http://basic.10jqka.com.cn/api/stockph/yyjgyj/600410
```

**注意**:
- 需要解析HTML
- 可能有反爬机制

---

### 6. 新闻舆情API (待集成)
**选项A: 阿里云市场 - 财经新闻API**
```
https://market.aliyun.com/products/57002003/cmapi022145.html
```
- 需要购买API Key
- 结构化新闻数据

**选项B: 聚合数据 - 新闻API**
```
https://www.juhe.cn/docs/api/id/235
```
- 免费额度有限
- 需要注册获取AppKey

**选项C: 自建爬虫**
- 新浪财经、东方财富新闻板块
- 需要处理反爬、清洗数据

**集成步骤**:
1. 选择API提供商
2. 在 `sentiment.py` 中添加 `fetch_news_api()` 函数
3. 替换现有的 `_mock_news_data()` 模拟数据

---

### 7. 北向资金详细API (待扩展)
**当前**: 东方财富提供持股占比和净流入

**扩展选项**:
```
https://datacenter-web.eastmoney.com/api/data/v1/get?reportName=RPT_MUTUAL_HOLD_STOCK&columns=ALL&filter=(SECURITY_CODE="600410")
```

**可获取数据**:
- 每日北向持股变化
- 北向资金行业分布
- 北向资金个股排名

---

## ⚙️ 配置文件

### 环境变量配置
创建 `.env` 文件:

```bash
# API密钥配置 (如需使用付费API)
SINA_API_KEY=your_key_here
XUEQIU_COOKIE=your_cookie_here
ALICLOUD_API_KEY=your_key_here
JUHE_API_KEY=your_key_here

# 请求频率限制 (秒)
REQUEST_INTERVAL=1
MAX_RETRIES=3

# 缓存配置
CACHE_ENABLED=true
CACHE_TTL=300

# 日志级别
LOG_LEVEL=INFO
```

### 代码中读取配置
```python
import os
from dotenv import load_dotenv

load_dotenv()

SINA_API_KEY = os.getenv("SINA_API_KEY")
REQUEST_INTERVAL = int(os.getenv("REQUEST_INTERVAL", "1"))
```

---

## 🛡️ 反爬虫策略

### 1. 请求频率控制
```python
import time
import random

def safe_request(url, headers=None):
    time.sleep(random.uniform(0.5, 1.5))  # 随机延迟
    return requests.get(url, headers=headers, timeout=10)
```

### 2. 请求头伪装
```python
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
    "Referer": "https://finance.sina.com.cn",
    "Accept": "application/json",
}
```

### 3. IP代理池 (高级)
```python
PROXY_POOL = [
    "http://proxy1.example.com:8080",
    "http://proxy2.example.com:8080",
]

def get_proxy():
    return random.choice(PROXY_POOL)
```

---

## 📈 数据缓存策略

### 内存缓存 (简单)
```python
from functools import lru_cache
import time

# 缓存5分钟
@lru_cache(maxsize=128)
def get_cached_stock_data(code, timestamp_bucket):
    return fetch_stock_data(code)

def get_stock_data_with_cache(code):
    # 按5分钟分桶
    timestamp_bucket = int(time.time() / 300)
    return get_cached_stock_data(code, timestamp_bucket)
```

### Redis缓存 (高级)
```python
import redis
import json

r = redis.Redis(host='localhost', port=6379, db=0)

def get_stock_data_redis(code):
    cache_key = f"stock:{code}"
    cached = r.get(cache_key)
    if cached:
        return json.loads(cached)
    
    data = fetch_stock_data(code)
    r.setex(cache_key, 300, json.dumps(data))  # 5分钟过期
    return data
```

---

## 🔗 相关文件

| 文件 | 说明 |
|-----|------|
| `server.py` | 主服务，腾讯API集成 |
| `capital_flow.py` | 资金流向，东方财富API |
| `sentiment.py` | 舆情分析 (待扩展) |
| `.env` | 环境变量配置 (需创建) |

---

## 📚 参考资源

- [东方财富API字段说明](https://github.com/akfamily/akshare)
- [腾讯财经API文档](https://qt.gtimg.cn/)
- [新浪财经API](https://finance.sina.com.cn/stock/)
- [雪球API](https://xueqiu.com/)

---

*最后更新: 2026-03-17*
*版本: v4.1.0*
