# System Resilience Improvements
# 系统韧性改进方案
# Created: 2026-03-17
# Author: OpenClaw Assistant (小爪)
# Purpose: 解决会话膨胀和死循环问题

## 📋 问题总结

### 症状
- 历史会话文件累积到 24MB
- 遇到障碍时进入死循环，不断重复发送消息
- 系统卡死，无法恢复

### 根本原因
1. **无会话边界**: 所有历史一直累积，无自动清理
2. **无失败隔离**: 错误状态污染整个会话
3. **无限重试**: 遇到障碍硬撑，不主动报告

---

## 🛠️ 解决方案

### 1. 会话生命周期管理 (HEARTBEAT.md)

```markdown
# HEARTBEAT.md - 系统健康监控

## 自检任务（每次心跳执行）

### 1. 会话健康检查
- 检查内存文件大小
- 如果超过阈值，自动归档并告警

### 2. 决策规则
- **文件 > 5MB**: 强制归档，开启新会话
- **消息堆积 > 10条未回复**: 静默等待
- **连续错误 > 3次**: 停止自动重试，报告用户

### 3. 长任务策略
- 复杂任务 → 使用 sessions_spawn 创建子会话
- 文件处理 → 流式读取，避免一次性加载
- 循环操作 → 设置最大迭代次数
```

### 2. 系统运行准则 (SYSTEM_GUIDELINES.md)

```markdown
# SYSTEM_GUIDELINES.md

## 🚨 硬性限制
| 指标 | 阈值 | 动作 |
|-----|------|------|
| 单文件大小 | 5MB | 强制归档 |
| 上下文消息数 | 30条 | 截断早期消息 |
| 会话时长 | 2小时 | 建议重置 |
| 连续错误 | 3次 | 停止+报告 |

## 🔄 任务执行模式
- 简单任务(<5分钟): 当前会话执行
- 复杂任务(>5分钟): 子会话隔离
- 危险操作: 必须二次确认

## 💡 第一性原理
1. 状态隔离 → 失败不扩散
2. 资源边界 → 防止无限膨胀
3. 快速失败 → 遇到问题立即报告
4. 用户主权 → 重要决策交还用户
```

### 3. 备份脚本 (scripts/backup-system.sh)

```bash
#!/bin/bash
WORKSPACE="$HOME/.openclaw/workspace"
BACKUP_DIR="$WORKSPACE/backups"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)

mkdir -p "$BACKUP_DIR"
tar czf "$BACKUP_DIR/system_backup_$TIMESTAMP.tar.gz" \
    -C "$WORKSPACE" \
    AGENTS.md SOUL.md SYSTEM_GUIDELINES.md \
    HEARTBEAT.md IDENTITY.md USER.md TOOLS.md memory/

# 保留最近10个备份
ls -t "$BACKUP_DIR"/system_backup_*.tar.gz | tail -n +11 | xargs rm -f
```

### 4. 回滚脚本 (scripts/rollback-system.sh)

```bash
#!/bin/bash
WORKSPACE="$HOME/.openclaw/workspace"
BACKUP_DIR="$WORKSPACE/backups"

if [ -z "$1" ]; then
    ls -lt "$BACKUP_DIR"/system_backup_*.tar.gz | head -10
    exit 1
fi

# 先备份当前状态（防止后悔）
CURRENT_BACKUP="$BACKUP_DIR/pre_rollback_$(date +%Y%m%d_%H%M%S).tar.gz"
tar czf "$CURRENT_BACKUP" -C "$WORKSPACE" .

# 执行回滚
cd "$WORKSPACE"
tar xzf "$1" --overwrite
```

---

## 📊 改进对比

| 维度 | 改进前 | 改进后 |
|-----|-------|-------|
| 会话大小 | 无限制，24MB+ | 5MB硬限制 |
| 错误处理 | 无限重试 | 3次后报告 |
| 失败隔离 | 无，污染全局 | 子会话隔离 |
| 消息纪律 | 死循环发送 | 堆积检测+静默 |
| 备份恢复 | 无 | 自动+手动脚本 |

---

## 🚀 使用指南

### 手动备份
```bash
cd ~/.openclaw/workspace
./scripts/backup-system.sh
```

### 查看备份
```bash
ls -lt ~/.openclaw/workspace/backups/
```

### 回滚系统
```bash
./scripts/rollback-system.sh
# 选择要恢复的备份文件
```

### 紧急重置（如果完全卡死）
```bash
# 1. 停止 OpenClaw
openclaw stop

# 2. 备份当前状态
cp -r ~/.openclaw/workspace ~/.openclaw/workspace.emergency.$(date +%s)

# 3. 清理大文件
rm ~/.openclaw/workspace/memory/*.md

# 4. 重启
openclaw start
```

---

## 📝 给Coding专家的说明

如果小爪再次出现异常，需要人工介入：

1. **检查日志**: `openclaw logs` 或 `~/.openclaw/logs/`
2. **查看会话大小**: `du -sh ~/.openclaw/workspace/memory/`
3. **使用回滚脚本恢复**: `./scripts/rollback-system.sh`
4. **检查 SYSTEM_GUIDELINES.md** 是否被修改

**关键文件位置**:
- 配置: `~/.openclaw/workspace/SYSTEM_GUIDELINES.md`
- 心跳: `~/.openclaw/workspace/HEARTBEAT.md`
- 备份: `~/.openclaw/workspace/backups/`
- 脚本: `~/.openclaw/workspace/scripts/`

---

## ✅ 验证清单

- [x] HEARTBEAT.md 已创建
- [x] SYSTEM_GUIDELINES.md 已创建
- [x] 备份脚本已创建并测试
- [x] 回滚脚本已创建并测试
- [x] 文件已保存到 workspace

**状态**: 已部署，等待验证
