#!/bin/bash
# 百度搜索引擎URL推送脚本

BAIDU_API_URL="http://data.zz.baidu.com/urls?site=https://biaoji.skillxm.cn&token=zJsDaj5ibt8ZlVgz"

echo "=========================================="
echo "百度URL推送开始"
echo "时间: $(date '+%Y-%m-%d %H:%M:%S')"
echo "=========================================="

# 从sitemap获取URL
URLS=$(curl -s "https://biaoji.skillxm.cn/sitemap.xml" | grep -oP '<loc>\K[^<]+')

if [ -z "$URLS" ]; then
    echo "❌ 错误: 无法从sitemap获取URL"
    exit 1
fi

URL_COUNT=$(echo "$URLS" | wc -l)
echo "从sitemap获取到 $URL_COUNT 个URL"

# 提交URL到百度
echo "正在提交到百度..."
RESPONSE=$(echo "$URLS" | curl -s -H "Content-Type:text/plain" --data-binary @- "$BAIDU_API_URL")

echo "百度API响应: $RESPONSE"

if echo "$RESPONSE" | grep -q '"success"'; then
    SUCCESS=$(echo "$RESPONSE" | grep -oP '"success":\K[0-9]+')
    REMAIN=$(echo "$RESPONSE" | grep -oP '"remain":\K[0-9]+')
    echo "✅ 成功提交 $SUCCESS 个URL，剩余配额 $REMAIN"
elif echo "$RESPONSE" | grep -q '"error"'; then
    MSG=$(echo "$RESPONSE" | grep -oP '"message":"[^"]+"' | sed 's/"message":"//;s/"$//')
    echo "⚠️ 提交失败: $MSG"
fi

echo "=========================================="
echo "百度URL推送完成"
echo "=========================================="
