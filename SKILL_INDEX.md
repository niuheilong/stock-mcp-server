# 小爪有效技能索引 v2.0
# 只包含实际可用和正在使用的技能
# 创建时间: 2026-03-18
# 更新方式: 技能变更时手动更新

## ✅ 有效技能 (已验证可用)

### 1. stock-monitor ⭐核心技能
- **位置**: `/Users/laoniu/.openclaw/workspace/skills/stock-monitor/`
- **状态**: ✅ 活跃使用
- **功能**: 青龙股票分析系统 - 实时行情、技术分析、资金流向、板块联动
- **版本**: v4.4.0
- **代码位置**: `/Users/laoniu/.openclaw/workspace/stock-mcp-server/`
- **使用方式**:
  ```bash
  cd /Users/laoniu/.openclaw/workspace/stock-mcp-server
  python server.py
  ```
- **API端点**: http://localhost:8000
- **核心模块**:
  - server.py - 主服务
  - capital_flow.py - 资金流向
  - sector_analysis.py - 板块分析
  - backtest.py - 回测框架
  - alert_system.py - 预警系统
  - resource_manager.py - 资源管理
  - browser_manager.py - 浏览器管理
  - health_monitor.py - 健康监控

### 2. self-improving-agent
- **位置**: `/Users/laoniu/.openclaw/workspace/skills/self-improving-agent/`
- **状态**: ✅ 已安装
- **功能**: 自动学习、错误检测、技能提取
- **使用**: 自动记录到 `.learnings/` 目录

### 3. skill-creator
- **位置**: `/Users/laoniu/.openclaw/workspace/skills/skill-creator/`
- **状态**: ✅ 已安装
- **功能**: 创建和打包新技能

## ❌ 已废弃/未使用技能

以下技能可以删除:
- ~~automation-workflows~~ - 未使用
- ~~find-skills~~ - 未使用  
- ~~skill-vetter-1-0-0~~ - 未使用

## 🔧 工具配置

### MCP Servers (已配置)
- **filesystem**: 文件系统访问
  - 工作区: `/Users/laoniu/.openclaw/workspace`
  - 下载: `/Users/laoniu/Downloads`

### Chrome DevTools MCP (已配置)
- **WebSocket URL**: `ws://localhost:9222/devtools/browser/...`
- **状态**: ✅ 运行中
- **功能**: 深度浏览器控制、数据抓取、自动化测试

### 内置工具 (OpenClaw)
- browser - 浏览器控制
- web_search - Brave搜索
- web_fetch - 网页抓取
- exec - 命令执行
- read/write/edit - 文件操作
- sessions_spawn - 子会话
- image - 图像分析
- pdf - PDF分析
- memory_search - 记忆搜索

### Chrome DevTools MCP ⭐核心工具
- **编号**: 01-001
- **位置**: `~/.openclaw/capabilities/01-浏览器自动化/01-001-Chrome-MCP.md`
- **状态**: ✅ 已配置并启用
- **功能**: 通过 Chrome DevTools Protocol 直接控制 Chrome 浏览器
- **WebSocket**: `ws://localhost:9222/devtools/browser/...`
- **Chrome 版本**: 147.0.7699.0
- **启动参数**: `--remote-debugging-port=9222 --enable-features=WebMCPTesting`
- **能力**:
  - ✅ 创建/关闭页面
  - ✅ 导航到 URL
  - ✅ 执行 JavaScript
  - ✅ 截图
  - ✅ 监听网络请求
- **使用场景**: 深度浏览器控制、数据抓取、自动化测试
- **配置日期**: 2026-03-16

### 其他浏览器工具
- **Playwright** (01-002): 自动化测试框架
- **Browser 工具** (01-003): OpenClaw 内置浏览器控制
- **Peekaboo** (01-004): macOS UI 自动化

## 📁 重要项目

### 青龙 Stock MCP Server
- **位置**: `/Users/laoniu/.openclaw/workspace/stock-mcp-server/`
- **版本**: v4.4.0
- **GitHub**: https://github.com/niuheilong/stock-mcp-server
- **本地版本库**: `/Users/laoniu/牛黑龙的股票行情/青龙项目版本库/`

## 🚀 快速启动

### 启动青龙服务
```bash
cd /Users/laoniu/.openclaw/workspace/stock-mcp-server
python server.py
```

### 分析股票
```python
from server import QingLongEngine
engine = QingLongEngine()
report = engine.analyze_stock('sh600410')
```

### 健康检查
```bash
cd /Users/laoniu/.openclaw/workspace/stock-mcp-server
python health_check.py
```

### 资源清理
```bash
cd /Users/laoniu/.openclaw/workspace/stock-mcp-server
./qinglong-resource.sh
```

### Chrome MCP 工作流
```bash
# 部署管理 (菜单式)
./chrome-mcp-deploy.sh

# 手动备份
./chrome-mcp-backup.sh

# 手动回滚
./chrome-mcp-rollback.sh backups/chrome-mcp/chrome-mcp-backup_xxx.tar.gz

# 运行工作流
python3 chrome_mcp_workflow.py

# 生成分析报告
python3 chrome_mcp_analyzer.py
```

### 数据获取策略 ⭐
| 时间段 | 数据类型 | 说明 | 数据源 |
|-------|---------|------|--------|
| 9:30-15:00 | 实时行情 | 每5分钟抓取一次 | Chrome MCP / 腾讯API |
| 15:00-9:30 | 收盘数据 | 使用当日收盘数据 | 腾讯财经API (优先) |
| 周末/节假日 | 历史数据 | 使用最近交易日数据 | 本地缓存 / 腾讯API |

**策略**: 优先实时，盘后使用收盘数据，确保数据连续性

### 腾讯财经 API 快速抓取 ⭐
```bash
# 单只股票查询
curl -s "http://qt.gtimg.cn/q=sz301396" | iconv -f gbk -t utf-8

# 返回字段说明 (以~分隔):
# 3:股票代码 4:收盘价 5:开盘价 6:最高价 7:最低价
# 33:成交量 34:成交额 35:换手率 36:总市值

# 多只股票查询
curl -s "http://qt.gtimg.cn/q=sh600410,sz002261,sz301396" | iconv -f gbk -t utf-8
```

**优点**:
- ✅ 零 Token 消耗
- ✅ 数据实时准确
- ✅ 盘后仍可获取收盘数据
- ✅ 支持批量查询

**适用场景**:
- 盘后获取收盘价
- 批量查询多只股票
- 快速验证数据

## 💰 成本优先策略 ⭐⭐⭐

### 核心原则
**成本 > 效率 > 功能** - 在保证准确的前提下，优先选择零成本方案

### 成本对比
| 操作 | 传统方式 | 优化方案 | 节省 |
|-----|---------|---------|------|
| 数据抓取 | 1,500 Token | Chrome MCP (0) | 100% |
| 行情获取 | 500 Token | 腾讯API (0) | 100% |
| 深度分析 | 3,000 Token | 精准调用 (~200) | 93% |
| **单次分析** | **5,000+ Token** | **~200 Token** | **96%** |

### 实战案例：锦浪科技深度分析
```
数据源                    Token消耗    效果
─────────────────────────────────────────────
Chrome MCP 抓取研报       0            ✅ 10+篇研报
腾讯API 获取行情          0            ✅ 实时数据
Google 搜索资讯           0            ✅ 最新资讯
LLM 综合分析              ~200         ✅ 深度报告
─────────────────────────────────────────────
总计                      ~200         ✅ 完整分析
传统方式                  5,000+       ❌ 高成本
```

### 执行优先级
1. **零成本工具** (优先)
   - Chrome MCP - 浏览器抓取
   - 腾讯/东方财富 API - 行情数据
   - 本地缓存 - 历史数据

2. **低成本工具** (次选)
   - Web搜索 - 资讯获取
   - 批量LLM调用 - 多股分析

3. **高成本工具** (最后)
   - 单股深度LLM分析
   - 复杂推理任务

### 成本监控
```python
# 每次分析记录成本
cost_log = {
    "timestamp": "2026-03-18 20:20",
    "stock": "锦浪科技",
    "chrome_mcp": 0,
    "tencent_api": 0,
    "llm_analysis": 200,
    "total": 200,
    "saved": 4800  # 相比传统方式
}
```

**目标**: 单次分析 < 500 Token，月消耗 < 10K Token

## 📦 技能管理备份

### 当前技能列表（5个）

#### 核心技能
- `stock-monitor` ⭐ - 青龙股票监控（核心项目）
- `self-improving-agent` - 自我进化
- `skill-creator` - 技能创建

#### 新安装技能（2026-03-18）
- `agent-browser-core` - 浏览器自动化（Rust+Node.js，零Token）
- `nano-pdf` - PDF自然语言编辑

#### 已删除技能
- ~~`openclaw-tavily-search`~~ - 需付费API Key
- ~~`find-skills`~~ - 功能与clawhub重复
- ~~`automation-workflows`~~ - 未使用
- ~~`skill-vetter-1-0-0`~~ - 未使用

### 备份机制
```bash
# 备份当前技能状态
ls skills/ > skills-backups/skills_backup_$(date +%Y%m%d_%H%M%S).txt

# 回滚技能（如需）
./skills-rollback.sh skills-backups/skills_backup_xxx.txt
```

### 安装新技能流程
```bash
# 1. 备份当前状态
ls skills/ > skills-backups/skills_backup_before_<skill>_$(date +%Y%m%d_%H%M%S).txt

# 2. 搜索技能
clawhub search <keyword>

# 3. 查看详情
clawhub inspect <skill-name>

# 4. 安装技能
clawhub install <skill-name>

# 5. 测试验证
# - 阅读 SKILL.md
# - 测试基本功能
# - 检查是否需要配置

# 6. 如异常，执行回滚
./skills-rollback.sh skills-backups/skills_backup_xxx.txt
```

### 实战案例：安装 agent-browser-core
```bash
# 2026-03-18 安装记录
# 1. 备份
ls skills/ > skills-backups/skills_backup_before_tavily_20260318_214441.txt

# 2. 搜索
clawhub search browser

# 3. 尝试安装 tavily-search（发现需付费）
clawhub install openclaw-tavily-search
# 结果：需要 TAVILY_API_KEY（付费）

# 4. 删除，改安装 agent-browser-core
rm -rf skills/openclaw-tavily-search
clawhub install agent-browser-core
# 结果：✅ 成功，零Token，功能正常

# 5. 验证
ls skills/agent-browser-core/
cat skills/agent-browser-core/SKILL.md
```

## 🛡️ 防卡壳机制 ⭐⭐⭐

### 核心标准
**预防 > 治疗** - 定期清理，防止资源累积导致卡壳

### 监控阈值
| 指标 | 阈值 | 动作 | 依据 |
|-----|------|------|------|
| **Python对象数** | > 10,000 | 强制垃圾回收 | 正常 < 8,000，超过10K可能累积 |
| **浏览器页面数** | > 5个 | 关闭多余页面 | 每个页面占用 50-100MB |
| **工作区大小** | > **10MB** | 清理缓存/日志 | 当前 2.6MB，正常 < 5MB |
| **运行时间** | > 2小时 | 建议重启 | 防止上下文膨胀 |
| **内存使用** | > 80% | 释放资源 | 系统稳定阈值 |

**说明**: 工作区100MB标准过高，根据实际调整为10MB
- 当前工作区: 2.6MB (健康)
- 警告阈值: 5MB
- 清理阈值: 10MB
- 历史问题: 24MB (曾卡壳)

### 主动排查机制 ⭐⭐⭐

**每次任务后自动执行**:
```python
任务完成 → 资源检查 → 超标? → 立即清理 → 确认释放
              ↓否
           正常，记录状态
```

**自动执行脚本**:
```python
# 每次任务后自动运行
import gc
import os
import subprocess
import requests

def auto_cleanup():
    need_cleanup = False
    
    # 1. 检查Python对象
    gc.collect()
    obj_count = len(gc.get_objects())
    if obj_count > 10000:
        print(f'🔴 Python对象过多: {obj_count:,}')
        need_cleanup = True
    
    # 2. 检查工作区大小
    result = subprocess.run(['du', '-sm', '.'], capture_output=True, text=True)
    size_mb = int(result.stdout.split()[0])
    if size_mb > 10:
        print(f'🔴 工作区过大: {size_mb}MB')
        need_cleanup = True
    
    # 3. 检查Chrome页面
    try:
        resp = requests.get('http://localhost:9222/json/list', timeout=2)
        pages = len(resp.json())
        if pages > 5:
            print(f'🔴 Chrome页面过多: {pages}')
            os.system('pkill -f "Chrome Canary.*9222"')
    except:
        pass
    
    # 4. 执行清理
    if need_cleanup:
        gc.collect()
        print('✅ 已清理')
    
    return not need_cleanup

# 任务后调用
auto_cleanup()
```

**执行原则**:
- 不等待问题发生，提前预防
- 超标立即清理，不过夜
- 每次任务后自动检查
- 主动汇报状态

### 自动清理脚本
```bash
# 健康检查 + 自动清理
python3 health_check.py

# 手动强制清理
python3 -c "
import gc
import os

# 1. 垃圾回收
gc.collect()

# 2. 清理缓存
import shutil
for f in ['/tmp/openclaw_*', '/tmp/tmp*']:
    import glob
    for p in glob.glob(f):
        try: os.remove(p) if os.path.isfile(p) else shutil.rmtree(p)
        except: pass

# 3. 报告状态
print(f'Python对象: {len(gc.get_objects()):,}')
print('✅ 清理完成')
"

# 关闭浏览器
pkill -f "Chrome Canary.*9222"
```

### 定时任务建议
```cron
# 每30分钟检查
*/30 * * * * cd ~/.openclaw/workspace/stock-mcp-server && python3 health_check.py >> logs/health.log 2>&1

# 每2小时清理
0 */2 * * * cd ~/.openclaw/workspace/stock-mcp-server && python3 -c "import gc; gc.collect()"

# 每天凌晨备份
0 0 * * * cd ~/.openclaw/workspace/stock-mcp-server && ./qinglong-backup.sh
```

### 卡壳应急处理
```bash
# 1. 立即停止所有任务
pkill -f "python3.*server.py"
pkill -f "Chrome Canary"

# 2. 紧急备份
cp -r ~/.openclaw/workspace ~/.openclaw/workspace.emergency.$(date +%s)

# 3. 清理大文件
find ~/.openclaw/workspace/memory -name "*.md" -size +1M -delete

# 4. 重启
openclaw restart
```

### 实战检查清单
- [ ] Python对象 < 10,000
- [ ] 浏览器页面 < 5个
- [ ] 工作区 < 100MB
- [ ] 运行时间 < 2小时
- [ ] 内存使用 < 80%

**状态**: 🟢 健康 / 🟡 警告 / 🔴 危险

## 📝 记忆重建清单

每次启动后:
1. ✅ 读取此文件 (SKILL_INDEX.md)
2. ✅ 确认 skills/ 目录状态
3. ✅ 验证工具可用性
4. ✅ 加载项目上下文
5. ✅ **执行健康检查** ⭐新增
6. ✅ **清理过期资源** ⭐新增

## 🗑️ 清理建议

建议删除以下未使用技能目录:
- `/Users/laoniu/.openclaw/workspace/skills/automation-workflows/`
- `/Users/laoniu/.openclaw/workspace/skills/find-skills/`
- `/Users/laoniu/.openclaw/workspace/skills/skill-vetter-1-0-0/`

---

---

## 📋 青龙能力编号系统

完整能力清单见: `~/.openclaw/capabilities/README.md`

### 01-浏览器自动化 (4个)
| 编号 | 名称 | 状态 |
|-----|------|------|
| 01-001 | Chrome MCP控制 | ✅ |
| 01-002 | Playwright | ✅ |
| 01-003 | Browser工具 | ✅ |
| 01-004 | Peekaboo | ✅ |

### 02-数据采集 (4个)
| 编号 | 名称 | 状态 |
|-----|------|------|
| 02-001 | Firecrawl | ✅ |
| 02-002 | Jina AI Reader | ✅ |
| 02-003 | API调用 | ✅ |
| 02-004 | Scrapling | ❌ |

### 03-金融分析 (4个)
| 编号 | 名称 | 状态 |
|-----|------|------|
| 03-001 | 妙想资讯搜索 | ✅ |
| 03-002 | 妙想金融数据 | ✅ |
| 03-003 | 妙想智能选股 | ✅ |
| 03-004 | 妙想自选股管理 | ✅ |

---

## 🛡️ 备份回滚机制

### Chrome MCP 工作流备份
- **备份脚本**: `chrome-mcp-backup.sh`
- **回滚脚本**: `chrome-mcp-rollback.sh`
- **部署工具**: `chrome-mcp-deploy.sh`
- **备份位置**: `backups/chrome-mcp/`
- **保留数量**: 最近20个备份

### 青龙项目备份
- **系统备份**: `qinglong-backup.sh`
- **系统回滚**: `qinglong-rollback.sh`
- **资源管理**: `qinglong-resource.sh`
- **备份位置**: `backups/`

---

*最后更新: 2026-03-18 17:59*
*维护者: 小爪*
