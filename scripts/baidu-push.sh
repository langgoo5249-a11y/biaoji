#!/bin/bash
# 百度搜索引擎URL推送脚本
# 用于将sitemap中的URL提交到百度站长平台

BAIDU_API_URL="http://data.zz.baidu.com/urls?site=https://biaoji.skillxm.cn&token=zJsDaj5ibt8ZlVgz"
SITEMAP_URL="https://biaoji.skillxm.cn/sitemap.xml"

echo "=========================================="
echo "百度URL推送开始"
echo "时间: $(date '+%Y-%m-%d %H:%M:%S')"
echo "=========================================="

# 从sitemap获取URL列表
URLS=$(curl -s "$SITEMAP_URL" | grep -oP '<loc>\K[^<]+')

if [ -z "$URLS" ]; then
    echo "❌ 错误: 无法从sitemap获取URL"
    exit 1
fi

URL_COUNT=$(echo "$URLS" | wc -l)
echo "从sitemap获取到 $URL_COUNT 个URL"

# 提交URL到百度
echo ""
echo "正在提交到百度..."

RESPONSE=$(curl -s -H "Content-Type:text/plain" --data-binary "$URLS" "$BAIDU_API_URL")

echo "百度API响应: $RESPONSE"

# 解析响应
if echo "$RESPONSE" | grep -q '"success"'; then
    SUCCESS_COUNT=$(echo "$RESPONSE" | grep -oP '"success":\K[0-9]+')
    echo "✅ 成功提交 $SUCCESS_COUNT 个URL"
elif echo "$RESPONSE" | grep -q '"error"'; then
    ERROR_MSG=$(echo "$RESPONSE" | grep -oP '"message":"[^"]+"' | sed 's/"message":"//;s/"$//')
    echo "⚠️ 提交失败: $ERROR_MSG"
else
    echo "响应: $RESPONSE"
fi

echo ""
echo "=========================================="
echo "百度URL推送完成"
echo "=========================================="
