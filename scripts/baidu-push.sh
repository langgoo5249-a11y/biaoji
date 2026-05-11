#!/bin/bash
# 百度搜索引擎URL推送脚本

BAIDU_API_URL="http://data.zz.baidu.com/urls?site=https://biaoji.skillxm.cn&token=zJsDaj5ibt8ZlVgz"

echo "=========================================="
echo "百度URL推送开始"
echo "时间: $(date '+%Y-%m-%d %H:%M:%S')"
echo "=========================================="

# 收集所有sitemap中的URL
ALL_URLS=""

for sitemap in "sitemap-pages.xml" "sitemap-blog.xml"; do
    SM_URL="https://biaoji.skillxm.cn/${sitemap}"
    URLS=$(curl -s "$SM_URL" | grep -oP '<loc>\K[^<]+')
    if [ -n "$URLS" ]; then
        ALL_URLS="${ALL_URLS}
${URLS}"
    fi
done

if [ -z "$ALL_URLS" ]; then
    echo "❌ 错误: 无法从sitemap获取URL"
    exit 1
fi

ALL_URLS=$(echo "$ALL_URLS" | tr -s '\n' | grep -v '^$')
URL_COUNT=$(echo "$ALL_URLS" | wc -l)
echo "从sitemap获取到 $URL_COUNT 个URL"

# 提交URL到百度
echo "正在提交到百度..."
RESPONSE=$(echo "$ALL_URLS" | curl -s -H "Content-Type:text/plain" --data-binary @- "$BAIDU_API_URL")

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
