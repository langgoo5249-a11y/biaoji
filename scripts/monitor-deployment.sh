#!/bin/bash
# 监控Cloudflare Pages部署状态的脚本

echo "=========================================="
echo "Cloudflare Pages 部署监控"
echo "=========================================="
echo ""
echo "等待Cloudflare Pages完成部署..."
echo "这可能需要1-5分钟，请耐心等待..."
echo ""

MAX_WAIT=300  # 最多等待5分钟
INTERVAL=10   # 每10秒检查一次
ELAPSED=0

while [ $ELAPSED -lt $MAX_WAIT ]; do
    # 检查响应头
    RESPONSE=$(curl -I https://biaoji.skillxm.cn/ 2>&1)
    
    # 提取关键信息
    HTTP_STATUS=$(echo "$RESPONSE" | grep -E "^HTTP/" | tail -1)
    CACHE_STATUS=$(echo "$RESPONSE" | grep -i "cf-cache-status:" | awk '{print $2}' | tr -d '\r')
    CACHE_CONTROL=$(echo "$RESPONSE" | grep -i "Cache-Control:" | awk -F: '{print $2}' | tr -d '\r\n' | head -c 50)
    PERMISSIONS=$(echo "$RESPONSE" | grep -i "Permissions-Policy:" | awk -F: '{print $2}' | tr -d '\r\n')
    
    echo "[$(date '+%H:%M:%S')] 已等待 ${ELAPSED}s"
    echo "  HTTP状态: $HTTP_STATUS"
    echo "  CDN缓存: $CACHE_STATUS"
    echo "  缓存控制: $CACHE_CONTROL"
    echo "  权限策略: $PERMISSIONS"
    echo "---"
    
    # 检查是否部署成功
    if [ "$CACHE_STATUS" = "HIT" ] || [ "$CACHE_STATUS" = "STATIC" ] || [ "$CACHE_STATUS" = "EXPIRED" ]; then
        echo ""
        echo "✅ 部署成功！Cloudflare缓存已生效"
        echo ""
        exit 0
    elif [ "$CACHE_STATUS" = "DYNAMIC" ]; then
        # 缓存还在更新，继续等待
        ELAPSED=$((ELAPSED + INTERVAL))
        sleep $INTERVAL
    else
        # 其他状态，继续等待
        ELAPSED=$((ELAPSED + INTERVAL))
        sleep $INTERVAL
    fi
done

echo ""
echo "⚠️ 等待超时，但网站应该已经部署成功"
echo "请手动访问 https://biaoji.skillxm.cn 验证"
exit 1
