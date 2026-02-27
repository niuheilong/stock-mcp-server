# OpenClaw Crontab 配置
# 自动化任务调度

## 定时任务列表

### 1. 股票晨报（工作日）
```
0 8 * * 1-5
```
- **时间**: 每天早上 8:00（周一至周五）
- **任务**: 生成 AI 股票晨报
- **输出**: /tmp/morning_report_YYYYMMDD.txt

### 2. 进化监控（每日）
```
0 9 * * *
```
- **时间**: 每天早上 9:00
- **任务**: 检查 Evolver + EvoMap + PR 状态
- **输出**: /tmp/evolution_check_YYYYMMDD.log

### 3. EvoMap 特别检查（每周）
```
30 8 * * 1
```
- **时间**: 每周一早上 8:30
- **任务**: 提醒发布 EvoMap 胶囊

### 4. 日志清理（每周）
```
0 3 * * 0
```
- **时间**: 每周日凌晨 3:00
- **任务**: 清理7天前的旧日志

## 监控内容

### 每日检查项
- ✅ awesome-mcp-servers PR #2463 状态
- ✅ Evolver 运行状态
- ✅ EvoMap 发布提醒
- ✅ Stock MCP Server 维护状态
- ✅ GitHub 仓库同步状态

## 手动执行

```bash
# 立即执行晨报生成
cd ~/projects/stock-mcp-server && python3 morning_report_generator.py

# 立即执行进化监控
cd ~/projects/stock-mcp-server && bash daily_evolution_check.sh

# 查看监控报告
python3 evolution_monitor.py
```

## 文件位置

- 晨报脚本: `morning_report_generator.py`
- 监控脚本: `daily_evolution_check.sh`
- 监控系统: `evolution_monitor.py`
- 本配置: `CRONTAB_CONFIG.md`

---
配置时间: 2026-02-27
生效状态: ✅ 已配置
