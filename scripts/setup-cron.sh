#!/bin/bash
# 号码标记清除网 - 自动内容发布定时任务设置脚本
# 设置每天自动生成1-2篇高质量文章

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WORKFLOW_SCRIPT="$SCRIPT_DIR/auto-content-workflow.py"
LOG_FILE="$SCRIPT_DIR/cron.log"

echo "=========================================="
echo "号码标记清除网 - 自动内容发布设置"
echo "=========================================="
echo ""

# 检查Python环境
echo "检查Python环境..."
if ! command -v python3 &> /dev/null; then
    echo "❌ 错误: 未找到Python3，请先安装Python3"
    exit 1
fi

echo "✅ Python3已安装: $(python3 --version)"
echo ""

# 检查工作流脚本
echo "检查工作流脚本..."
if [ ! -f "$WORKFLOW_SCRIPT" ]; then
    echo "❌ 错误: 未找到工作流脚本: $WORKFLOW_SCRIPT"
    exit 1
fi

echo "✅ 工作流脚本已找到"
echo ""

# 测试运行一次
echo "测试运行文章生成..."
cd "$SCRIPT_DIR/.."
python3 "$WORKFLOW_SCRIPT" --plan
if [ $? -eq 0 ]; then
    echo "✅ 测试运行成功"
else
    echo "❌ 测试运行失败，请检查脚本"
    exit 1
fi
echo ""

# 创建crontab条目
echo "设置定时任务..."
echo ""
echo "请选择发布频率:"
echo "  1) 每天1篇 (推荐)"
echo "  2) 每天2篇"
echo "  3) 每周5篇 (工作日)"
echo "  4) 自定义"
read -p "请输入选项 (1-4): " choice

case $choice in
    1)
        # 每天上午9点生成1篇
        CRON_EXPR="0 9 * * *"
        CRON_DESC="每天上午9:00"
        ;;
    2)
        # 每天上午9点和下午3点各生成1篇
        CRON_EXPR="0 9,15 * * *"
        CRON_DESC="每天上午9:00和下午15:00"
        ;;
    3)
        # 工作日每天1篇
        CRON_EXPR="0 9 * * 1-5"
        CRON_DESC="工作日(周一至周五)上午9:00"
        ;;
    4)
        echo ""
        echo "请输入自定义cron表达式 (例如: 0 9 * * * 表示每天9点)"
        echo "格式: 分 时 日 月 周"
        read -p "Cron表达式: " CRON_EXPR
        CRON_DESC="自定义: $CRON_EXPR"
        ;;
    *)
        echo "❌ 无效选项"
        exit 1
        ;;
esac

# 创建crontab条目
CRON_JOB="$CRON_EXPR cd $SCRIPT_DIR/.. && /usr/bin/python3 $WORKFLOW_SCRIPT --now >> $LOG_FILE 2>&1"

echo ""
echo "定时任务详情:"
echo "  执行时间: $CRON_DESC"
echo "  执行命令: $CRON_JOB"
echo "  日志文件: $LOG_FILE"
echo ""

# 检查是否已有相同的定时任务
if crontab -l 2>/dev/null | grep -q "$WORKFLOW_SCRIPT"; then
    echo "⚠️  检测到已存在相同的定时任务"
    read -p "是否覆盖? (y/n): " overwrite
    if [ "$overwrite" != "y" ]; then
        echo "已取消"
        exit 0
    fi
    # 删除旧的定时任务
    crontab -l 2>/dev/null | grep -v "$WORKFLOW_SCRIPT" | crontab -
fi

# 添加新的定时任务
(crontab -l 2>/dev/null; echo "$CRON_JOB") | crontab -

echo "✅ 定时任务已设置成功!"
echo ""

# 显示当前crontab
echo "当前定时任务列表:"
echo "----------------------------------------"
crontab -l | grep -E "(^#|$WORKFLOW_SCRIPT)" || echo "(无)"
echo "----------------------------------------"
echo ""

# 创建日志文件
touch "$LOG_FILE"

echo "其他可用命令:"
echo "  立即生成文章: python3 $WORKFLOW_SCRIPT --now"
echo "  查看生成日志: tail -f $LOG_FILE"
echo "  查看定时任务: crontab -l"
echo "  删除定时任务: crontab -l | grep -v '$WORKFLOW_SCRIPT' | crontab -"
echo ""
echo "=========================================="
echo "设置完成!"
echo "=========================================="
