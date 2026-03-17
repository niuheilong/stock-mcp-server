# 青龙项目基因 - 备份与回滚机制

> 本文件是青龙项目的核心基因文档，定义了项目的备份、回滚和恢复机制。
> 任何对青龙项目的修改都应遵循此规范。

---

## 🧬 项目基因

### 核心原则
1. **安全第一** - 任何修改前必须先备份
2. **可回滚** - 所有变更都必须可撤销
3. **可追溯** - 所有操作都有记录
4. **自动化** - 关键操作脚本化

---

## 📦 备份机制

### 自动备份触发条件
- 服务启动前自动备份
- 重大版本更新前手动备份
- 每日定时备份（可选）

### 备份内容
```
qinglong_backup_YYYYMMDD_HHMMSS.tar.gz
├── server.py              # 主服务
├── capital_flow.py        # 资金流向
├── sector_analysis.py     # 板块分析
├── backtest.py           # 回测框架
├── alert_system.py       # 预警系统
├── requirements.txt      # 依赖
├── Dockerfile           # 容器配置
└── README.md            # 文档
```

### 备份脚本
```bash
# 手动备份
./qinglong-backup.sh [备份名称]

# 自动备份（带默认名称）
./qinglong-backup.sh
```

### 备份保留策略
- 保留最近20个备份
- 自动清理旧备份
- 重要版本永久保留

---

## 🔄 回滚机制

### 回滚触发条件
- 服务异常/崩溃
- 数据错误
- 功能回退需求

### 回滚步骤
```bash
# 1. 查看可用备份
./qinglong-rollback.sh

# 2. 执行回滚
./qinglong-rollback.sh backups/qinglong_backup_20260317_213815.tar.gz

# 3. 重启服务
python3 server.py
```

### 回滚安全机制
1. **预备份** - 回滚前自动备份当前状态
2. **可撤销** - 提供撤销回滚的命令
3. **验证** - 回滚后自动验证关键文件

---

## 🚀 部署流程

### 标准部署流程
```bash
# 1. 进入项目目录
cd stock-mcp-server

# 2. 运行部署工具
./qinglong-deploy.sh

# 3. 选择操作:
#    [1] 安装依赖
#    [2] 运行测试
#    [3] 备份项目
#    [4] 回滚项目
#    [5] 启动服务
#    [6] 查看状态
```

### 紧急恢复流程
```bash
# 如果服务完全无法启动:

# 1. 停止服务
pkill -f "python3 server.py"

# 2. 紧急备份当前状态（防止数据丢失）
cp -r . qinglong-emergency-$(date +%s)

# 3. 查看最新备份
ls -lt backups/

# 4. 回滚到稳定版本
./qinglong-rollback.sh backups/qinglong_backup_最新.tar.gz

# 5. 重启服务
python3 server.py
```

---

## 📋 版本管理

### 版本号规范
- **主版本** - 重大架构变更
- **次版本** - 功能模块新增
- **修订版本** - Bug修复/优化

### 版本历史
| 版本 | 日期 | 变更内容 | 备份文件 |
|-----|------|---------|---------|
| v4.4.0 | 2026-03-17 | 新增预警系统 | qinglong_backup_20260317_213815 |
| v4.3.0 | 2026-03-17 | 新增历史回测 | qinglong_backup_20260317_213348 |
| v4.2.0 | 2026-03-17 | 新增板块联动 | qinglong_backup_20260317_212827 |
| v4.1.0 | 2026-03-17 | 新增资金流向 | qinglong_backup_20260317_212122 |
| v4.0.0 | 2026-03-17 | 新增舆情情绪 | qinglong_backup_20260317_211924 |

---

## 🛡️ 数据安全

### 数据库备份
- 历史数据: `qinglong_history.db`
- 预警记录: 存储在内存，定期持久化
- 配置文件: 纳入版本控制

### 敏感信息
- API密钥: 存储在 `.env` 文件（不纳入版本控制）
- 日志文件: 定期清理

---

## 🔧 维护工具

### 工具清单
| 工具 | 用途 | 命令 |
|-----|------|------|
| qinglong-backup.sh | 备份项目 | `./qinglong-backup.sh` |
| qinglong-rollback.sh | 回滚项目 | `./qinglong-rollback.sh <文件>` |
| qinglong-deploy.sh | 部署工具 | `./qinglong-deploy.sh` |

### 快速命令
```bash
# 一键备份
./qinglong-backup.sh

# 一键回滚（交互式）
./qinglong-rollback.sh

# 查看状态
./qinglong-deploy.sh  # 然后选择 6
```

---

## 📞 故障处理

### 常见问题

**Q: 服务无法启动**
```bash
# 检查日志
tail -f logs/error.log

# 回滚到上一个稳定版本
./qinglong-rollback.sh
```

**Q: 数据异常**
```bash
# 备份当前数据
./qinglong-backup.sh corrupt_data

# 恢复数据库
cp backups/qinglong_history.db.bak qinglong_history.db
```

**Q: API返回错误**
```bash
# 检查API配置
cat API_CONFIG.md

# 测试单个模块
python3 capital_flow.py
```

---

## 📝 更新规范

### 更新前检查清单
- [ ] 已创建备份
- [ ] 已阅读 CHANGELOG
- [ ] 已测试新功能
- [ ] 已更新文档

### 更新后检查清单
- [ ] 服务正常启动
- [ ] API响应正常
- [ ] 数据无异常
- [ ] 已创建新备份

---

## 🎯 项目目标

### 核心目标
1. 提供准确的股票分析
2. 及时发现投资机会
3. 有效控制投资风险

### 技术目标
1. 高可用性 - 99.9% 正常运行时间
2. 低延迟 - API响应 < 500ms
3. 可扩展 - 模块化架构

---

*基因版本: v1.0*
*最后更新: 2026-03-17*
*维护者: 青龙开发团队*
