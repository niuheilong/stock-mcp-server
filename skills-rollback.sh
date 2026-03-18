#!/bin/bash
# OpenClaw 技能回滚脚本
# 使用方法: ./skills-rollback.sh [备份文件]

BACKUP_DIR="/Users/laoniu/.openclaw/workspace/skills-backups"
SKILLS_DIR="/Users/laoniu/.openclaw/workspace/skills"

echo "🐉 OpenClaw 技能回滚工具"
echo "========================"
echo ""

# 显示可用备份
if [ -z "$1" ]; then
    echo "📋 可用备份:"
    ls -lt ${BACKUP_DIR}/skills_backup_*.txt 2>/dev/null | head -5 | nl
    echo ""
    echo "Usage: $0 <备份文件>"
    echo "Example: $0 skills_backup_20260318_214500.txt"
    exit 1
fi

BACKUP_FILE="$1"

if [ ! -f "$BACKUP_FILE" ]; then
    echo "❌ 备份文件不存在: $BACKUP_FILE"
    exit 1
fi

echo "⚠️  即将回滚到: $(basename $BACKUP_FILE)"
echo "⏳ 3秒后开始..."
sleep 3

# 备份当前状态（防止后悔）
CURRENT_BACKUP="${BACKUP_DIR}/pre_rollback_$(date +%Y%m%d_%H%M%S).txt"
ls "$SKILLS_DIR" > "$CURRENT_BACKUP"
echo "💾 当前状态已保存: $(basename $CURRENT_BACKUP)"

# 读取备份的技能列表
echo ""
echo "🔄 回滚技能..."
while IFS= read -r skill; do
    # 跳过注释和空行
    [[ "$skill" =~ ^# ]] && continue
    [[ -z "$skill" ]] && continue
    
    if [ -d "$SKILLS_DIR/$skill" ]; then
        echo "  ✅ $skill 已存在"
    else
        echo "  ⚠️  $skill 需要重新安装"
        # 这里可以自动安装，或记录待安装列表
    fi
done < "$BACKUP_FILE"

echo ""
echo "✅ 回滚检查完成"
echo ""
echo "📝 如需完全恢复，请手动安装缺失的技能:"
grep -v "^#" "$BACKUP_FILE" | grep -v "^$" | while read skill; do
    if [ ! -d "$SKILLS_DIR/$skill" ]; then
        echo "   clawhub install $skill"
    fi
done

echo ""
echo "🔧 撤销回滚: $0 $CURRENT_BACKUP"
