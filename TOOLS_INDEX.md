# 青龙工具库 - 通用能力索引
## 创建时间: 2026-03-26
## 用途: 存储可复用的通用工具和能力

---

## 🔧 通用工具列表

### 1. AntiCrawler - 反爬能力 ⭐⭐⭐

**位置**: `anti_crawler.py`

**功能**:
- User-Agent 轮换
- 请求头模拟
- 随机延迟
- 自动重试
- 会话管理

**适用场景**:
- 网页数据抓取
- API 请求防封
- 爬虫项目
- 任何需要模拟浏览器的请求

**使用方法**:
```python
from anti_crawler import get_anti_crawler, fetch_with_protection

# 方式1: 使用全局实例
crawler = get_anti_crawler()
response = crawler.get("https://example.com")

# 方式2: 便捷函数
response = fetch_with_protection("https://example.com")

# 方式3: 自定义参数
crawler = get_anti_crawler(min_delay=1.0, max_delay=3.0)
```

**配置参数**:
- `min_delay`: 最小延迟（默认0.5秒）
- `max_delay`: 最大延迟（默认2.0秒）

---

### 2. SmartCache - 智能缓存 ⏳ (开发中)

**位置**: `smart_cache.py` (待创建)

**功能**:
- 交易时间自动判断
- 动态 TTL 调整
- 多级缓存（内存+文件）

**适用场景**:
- 股票数据缓存
- 实时数据缓存
- 需要根据时间调整缓存策略的场景

---

### 3. SmartDataFetcher - 智能数据获取 ⏳ (已创建)

**位置**: `smart_data_fetcher.py`

**功能**:
- 多数据源优先级管理
- 自动故障转移
- 交易时间判断

**适用场景**:
- 股票数据获取
- 多数据源融合
- 高可用数据服务

---

## 📋 工具使用规范

### 添加新工具
1. 在 `tools/` 目录创建新文件
2. 添加到此索引文档
3. 编写使用示例
4. 提交到 Git

### 工具设计原则
1. **单一职责** - 每个工具只做一件事
2. **可配置** - 提供配置参数
3. **可测试** - 包含测试代码
4. **文档化** - 清晰的文档说明

---

## 🚀 快速开始

```python
# 导入通用工具
from anti_crawler import get_anti_crawler
from smart_data_fetcher import SmartDataFetcher

# 使用工具
crawler = get_anti_crawler()
fetcher = SmartDataFetcher()
```

---

## 📝 更新日志

### 2026-03-26
- ✅ 创建 AntiCrawler 反爬工具
- ✅ 创建 SmartDataFetcher 智能获取器
- ✅ 创建工具索引文档
