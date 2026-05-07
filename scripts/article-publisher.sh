#!/bin/bash
# 文章发布脚本 - 生成文章并推送到GitHub

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$SCRIPT_DIR/.."
WORKFLOW_SCRIPT="$SCRIPT_DIR/auto-content-workflow.py"
LOG_FILE="$SCRIPT_DIR/publish.log"

# 日志函数
log() {
    local timestamp=$(date "+%Y-%m-%d %H:%M:%S")
    echo "[$timestamp] $1" | tee -a "$LOG_FILE"
}

log "=========================================="
log "开始执行文章发布流程"
log "=========================================="

# 1. 生成文章
log "步骤1: 生成新文章..."
cd "$PROJECT_ROOT"
python3 "$WORKFLOW_SCRIPT" --now

if [ $? -ne 0 ]; then
    log "❌ 文章生成失败"
    exit 1
fi

log "✅ 文章生成完成"

# 2. 检查是否有新文件
log "步骤2: 检查新生成的文章..."
NEW_FILES=$(git status --porcelain | grep "^?? blog/" | wc -l)

if [ "$NEW_FILES" -eq 0 ]; then
    log "⚠️ 没有新文章需要提交"
    exit 0
fi

log "发现 $NEW_FILES 篇新文章"

# 3. 更新sitemap.xml（可选）
log "步骤3: 更新站点地图..."
# 这里可以添加自动更新sitemap的逻辑
# python3 "$SCRIPT_DIR/update-sitemap.py"

# 4. Git提交
log "步骤4: 提交到Git..."
git add blog/
git add sitemap.xml 2>/dev/null || true

# 生成提交信息
DATE=$(date "+%Y-%m-%d")
ARTICLES=$(git status --porcelain | grep "^?? blog/" | sed 's/^?? blog\///' | sed 's/\.html$//' | tr '\n' ', ' | sed 's/, $//')

COMMIT_MSG="content: $DATE 自动发布新文章

新增文章:
- $ARTICLES

由自动内容工作流生成"

git commit -m "$COMMIT_MSG"
log "✅ Git提交完成"

# 5. 推送到GitHub
log "步骤5: 推送到GitHub..."
git push origin main

if [ $? -eq 0 ]; then
    log "✅ 推送成功"
else
    log "❌ 推送失败"
    exit 1
fi

log "=========================================="
log "文章发布流程完成"
log "=========================================="

# 6. 发送通知（可选）
# 可以集成钉钉、企业微信等Webhook
# curl -X POST ...

exit 0
