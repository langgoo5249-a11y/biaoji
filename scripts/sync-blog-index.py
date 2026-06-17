#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
自动同步blog/index.html中的文章列表
扫描 blog/ 目录下所有文章HTML文件，提取标题、描述、日期，生成最新的文章列表
"""

import os
import re
import json
from pathlib import Path
from datetime import datetime

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)
BLOG_DIR = os.path.join(PROJECT_ROOT, 'blog')
INDEX_FILE = os.path.join(BLOG_DIR, 'index.html')
SITE_URL = "https://biaoji.skillxm.cn"

# 分类标签映射(基于文件名关键词)
CATEGORY_MAP = {
    'qiye-': '企业服务',
    'baoxian-': '保险行业',
    'jinrong-': '金融行业',
    'jiaoyu-': '教育行业',
    'yiliao-': '医疗行业',
    'waimai-': '外卖快递',
    'canyin-': '外卖快递',
    'kuaidi-': '外卖快递',
    'fangchan-': '房产中介',
    '400-': '企业服务',
    'geren-': '个人用户',
    'haoma-': '综合指南',
    'dianhua-': '综合指南',
    'anquan-': '综合指南',
    'shensu-': '申诉教程',
    'qingchu-': '清除教程',
    'chaxun-': '查询教程',
    'tongji-': '数据统计',
    'fenxi-': '数据分析',
    'pingfen-': '数据分析',
    'yidong-': '运营商',
    'liantong-': '运营商',
    'yufang-': '预防指南',
    'fubiao-': '预防指南',
    'shijian-': '常见问题',
    'feiyong-': '常见问题',
    'chenggonglv-': '常见问题',
    'waiqi-': '外贸跨境',
    'kuajing-': '外贸跨境',
    'xuni-': '虚拟运营商',
    'wuyong-': '恶意标记',
    'wuqu-': '恶意标记',
    'weizhang-': '违法案例',
    'xinyongka-': '金融行业',
    'chongwu-': '生活服务',
    'meirong-': '生活服务',
    'caishui-': '企业服务',
    'yujia-': '生活服务',
    'liuxue-': '教育培训',
    'posji-': '收单支付',
    'hunqing-': '婚庆摄影',
    'lvshi-': '法律服务',
    'zhuangxiu-': '装修家居',
    'zhaopin-': '招聘猎头',
    'yimei-': '医美机构',
}

# 颜色渐变(8种)
GRADIENTS = [
    'gradient-1', 'gradient-2', 'gradient-3', 'gradient-4',
    'gradient-5', 'gradient-6', 'gradient-7', 'gradient-8',
    'gradient-9', 'gradient-10', 'gradient-11', 'gradient-12',
]

# SVG图标
ICONS = [
    '<svg viewBox="0 0 24 24"><path d="M19 3H5c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h14c1.1 0 2-.9 2-2V5c0-1.1-.9-2-2-2zM9 17H7v-7h2v7zm4 0h-2V7h2v10zm4 0h-2v-4h2v4z"/></svg>',  # 数据分析
    '<svg viewBox="0 0 24 24"><path d="M17 1.01L7 1c-1.1 0-2 .9-2 2v18c0 1.1.9 2 2 2h10c1.1 0 2-.9 2-2V3c0-1.1-.9-1.99-2-1.99zM17 19H7V5h10v14z"/></svg>',  # 手机
    '<svg viewBox="0 0 24 24"><path d="M12 1L3 5v6c0 5.55 3.84 10.74 9 12 5.16-1.26 9-6.45 9-12V5l-9-4zm-2 16l-4-4 1.41-1.41L10 14.17l6.59-6.59L18 9l-8 8z"/></svg>',  # 安全
    '<svg viewBox="0 0 24 24"><path d="M9 16.17L4.83 12l-1.42 1.41L9 19 21 7l-1.41-1.41z"/></svg>',  # 完成
    '<svg viewBox="0 0 24 24"><path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm1 17h-2v-2h2v2zm2.07-7.75l-.9.92C13.45 12.9 13 13.5 13 15h-2v-.5c0-1.1.45-2.1 1.17-2.83l1.24-1.26c.37-.36.59-.86.59-1.41 0-1.1-.9-2-2-2s-2 .9-2 2H8c0-2.21 1.79-4 4-4s4 1.79 4 4c0 .88-.36 1.68-.93 2.25z"/></svg>',  # 帮助
    '<svg viewBox="0 0 24 24"><path d="M20 4H4c-1.11 0-1.99.89-1.99 2L2 18c0 1.11.89 2 2 2h16c1.11 0 2-.89 2-2V6c0-1.11-.89-2-2-2zm0 14H4v-6h16v6zm0-10H4V6h16v2z"/></svg>',  # 文件
    '<svg viewBox="0 0 24 24"><path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-2 15l-5-5 1.41-1.41L10 14.17l7.59-7.59L19 8l-9 9z"/></svg>',  # 圆形勾
    '<svg viewBox="0 0 24 24"><path d="M12 2l3.09 6.26L22 9.27l-5 4.87 1.18 6.88L12 17.77l-6.18 3.25L7 14.14 2 9.27l6.91-1.01L12 2z"/></svg>',  # 星
    '<svg viewBox="0 0 24 24"><path d="M3 13h2v-2H3v2zm0 4h2v-2H3v2zm0-8h2V7H3v2zm4 4h14v-2H7v2zm0 4h14v-2H7v2zM7 7v2h14V7H7z"/></svg>',  # 列表
    '<svg viewBox="0 0 24 24"><path d="M16 11c1.66 0 2.99-1.34 2.99-3S17.66 5 16 5c-1.66 0-3 1.34-3 3s1.34 3 3 3zm-8 0c1.66 0 2.99-1.34 2.99-3S9.66 5 8 5C6.34 5 5 6.34 5 8s1.34 3 3 3zm0 2c-2.33 0-7 1.17-7 3.5V19h14v-2.5c0-2.33-4.67-3.5-7-3.5zm8 0c-.29 0-.62.02-.97.05 1.16.84 1.97 1.97 1.97 3.45V19h6v-2.5c0-2.33-4.67-3.5-7-3.5z"/></svg>',  # 团队
    '<svg viewBox="0 0 24 24"><path d="M19 3H5c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h14c1.1 0 2-.9 2-2V5c0-1.1-.9-2-2-2zM9 17H7v-7h2v7zm4 0h-2V7h2v10zm4 0h-2v-4h2v4z"/></svg>',  # 柱状图
    '<svg viewBox="0 0 24 24"><path d="M19 5v9h-5v5H5V5h14m0-2H5c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h11l6-6V5c0-1.1-.9-2-2-2z"/></svg>',  # 文件夹
]


def extract_article_info(filepath):
    """从HTML文件中提取文章信息"""
    filename = os.path.basename(filepath)
    if filename == 'index.html' or filename.startswith('index-'):
        return None

    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # 提取标题
    title_match = re.search(r'<title>([^<]+)</title>', content)
    title = title_match.group(1) if title_match else filename[:-5]
    # 去掉 " - 号码标记清除网" 后缀
    title = re.sub(r'\s*-\s*号码标记清除网\s*$', '', title)

    # 提取描述
    desc_match = re.search(r'<meta name="description" content="([^"]+)"', content)
    description = desc_match.group(1) if desc_match else ''

    # 提取发布日期
    date_match = re.search(r'<meta property="article:published_time" content="([^"]+)"', content)
    if not date_match:
        date_match = re.search(r'📅\s*(\d{4}-\d{2}-\d{2})', content)
    if not date_match:
        # 使用文件修改时间
        mtime = os.path.getmtime(filepath)
        date = datetime.fromtimestamp(mtime).strftime('%Y-%m-%d')
    else:
        date = date_match.group(1) if date_match else datetime.fromtimestamp(os.path.getmtime(filepath)).strftime('%Y-%m-%d')
        if 'T' in date:
            date = date.split('T')[0]

    # 提取分类标签
    category = '综合指南'  # 默认
    for prefix, cat in CATEGORY_MAP.items():
        if filename.startswith(prefix):
            category = cat
            break

    # 文件修改时间(用于排序)
    mtime = os.path.getmtime(filepath)

    return {
        'filename': filename[:-5],  # 去掉 .html
        'title': title,
        'description': description,
        'date': date,
        'category': category,
        'mtime': mtime,
        'url': f"/blog/{filename[:-5]}"
    }


def generate_article_card(article, index):
    """生成单篇文章的HTML卡片"""
    gradient = GRADIENTS[index % len(GRADIENTS)]
    icon = ICONS[index % len(ICONS)]

    return f'''                <!-- {index}. {article['title'][:30]} -->
                <article class="article-card">
                    <div class="article-thumb {gradient}"><div class="thumb-icon">{icon}</div></div>
                    <div class="article-body">
                        <span class="article-tag">{article['category']}</span>
                        <h2><a href="{article['url']}">{article['title']}</a></h2>
                        <p>{article['description'][:120]}{'...' if len(article['description']) > 120 else ''}</p>
                        <div class="article-meta">
                            <span>📅 {article['date']}</span>
                            <a href="{article['url']}" class="read-more">阅读全文 →</a>
                        </div>
                    </div>
                </article>
'''


def update_blog_index():
    """更新blog/index.html文件"""
    print("=" * 60)
    print("自动同步 blog/index.html 文章列表")
    print("=" * 60)

    # 1. 扫描所有文章
    print("\n[1] 扫描 blog/ 目录...")
    articles = []
    for filename in os.listdir(BLOG_DIR):
        if not filename.endswith('.html'):
            continue
        if filename == 'index.html' or filename.startswith('index-'):
            continue
        filepath = os.path.join(BLOG_DIR, filename)
        info = extract_article_info(filepath)
        if info:
            articles.append(info)

    # 2. 按发布日期倒序排序（使用文章实际日期而非文件 mtime）
    articles.sort(key=lambda x: x['date'], reverse=True)
    print(f"    找到 {len(articles)} 篇文章")

    # 3. 读取原blog/index.html
    print("\n[2] 读取 blog/index.html...")
    with open(INDEX_FILE, 'r', encoding='utf-8') as f:
        content = f.read()

    # 4. 生成新的文章列表HTML
    print("\n[3] 生成新的文章列表HTML...")
    new_article_html = '\n'.join([generate_article_card(art, i) for i, art in enumerate(articles)])

    # 5. 替换原文章列表区域
    # 用更可靠的边界标记:从 <!-- Articles --> 到 <!-- Sidebar -->
    # 然后取文章区域末尾的两个 </div> 中的第一个作为 article-grid 结束
    start_marker = '<!-- Articles -->'
    end_marker = '<!-- Sidebar -->'
    start_pos = content.find(start_marker)
    end_pos = content.find(end_marker)

    if start_pos == -1 or end_pos == -1:
        print("    ✗ 未找到明确的边界标记")
        return False

    # 在 [start_pos, end_pos] 范围内找 article-grid 结束位置（倒数第二个 </div>）
    section = content[start_pos:end_pos]
    all_divs = [m.end() for m in re.finditer(r'</div>', section)]
    if len(all_divs) < 2:
        print("    ✗ 找到的 </div> 数量不足")
        return False
    article_grid_end_in_section = all_divs[-2]

    # 构造新内容
    new_content_start = content[:start_pos]
    header = '<!-- Articles -->\n        <div>\n            <div class="article-grid">\n'
    # footer_section 包含 article-grid 关闭 </div> + wrapper 关闭 </div> + 中间空白
    # 末尾追加 Sidebar 注释，再拼接 Sidebar 之后的内容
    footer_section = content[start_pos + article_grid_end_in_section:end_pos]
    sidebar_comment = '<!-- Sidebar -->'
    new_content = (new_content_start + header + new_article_html + '\n            '
                   + footer_section + sidebar_comment
                   + content[end_pos + len(sidebar_comment):])
    print("    ✓ 找到文章列表区域并替换")

    # 6. 添加 ItemList 结构化数据
    print("\n[4] 添加 ItemList 结构化数据...")
    item_list_items = []
    for i, art in enumerate(articles[:20]):  # 只列前20个
        item_list_items.append(f'''            {{
                "@type": "ListItem",
                "position": {i+1},
                "name": "{art['title'][:60]}",
                "item": "https://biaoji.skillxm.cn{art['url']}"
            }}''')

    item_list_json = f'''    <script type="application/ld+json">
    {{
        "@context": "https://schema.org",
        "@type": "ItemList",
        "name": "号码标记教程文档列表",
        "itemListElement": [
{','.join(item_list_items)}
        ]
    }}
    </script>
'''

    if '"@type": "ItemList"' not in new_content:
        # 插入到</head>之前
        new_content = new_content.replace('</head>', item_list_json + '</head>')
        print("    ✓ 添加 ItemList 结构化数据")
    else:
        # 已存在则替换
        existing_pattern = re.compile(
            r'    <script type="application/ld\+json">\s*\{[^<]*"@type":\s*"ItemList"[^<]*</script>\s*',
            re.DOTALL
        )
        new_content = existing_pattern.sub(item_list_json, new_content)
        print("    ✓ 更新 ItemList 结构化数据")

    # 7. 写回文件
    print("\n[5] 写回 blog/index.html...")
    with open(INDEX_FILE, 'w', encoding='utf-8') as f:
        f.write(new_content)

    print("\n" + "=" * 60)
    print(f"✓ 完成！共同步 {len(articles)} 篇文章")
    print("=" * 60)
    return True


if __name__ == "__main__":
    update_blog_index()