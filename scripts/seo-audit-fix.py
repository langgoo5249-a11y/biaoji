#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
全站SEO/GEO审计批量修复脚本
修复内容：
1. 分页页面(index-2~5) - 改为noindex，修复canonical
2. 所有页面添加Twitter Card
3. 博客文章统一og:image为og-cover.jpg
4. 博客文章添加BreadcrumbList
5. 完善Article Schema
6. 修复docs/index.html
"""

import os
import re
import html
from datetime import date

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)
BLOG_DIR = os.path.join(PROJECT_ROOT, 'blog')
DOCS_DIR = os.path.join(PROJECT_ROOT, 'docs')
SITE_URL = "https://biaoji.skillxm.cn"
SITE_NAME = "号码标记清除网"
TODAY = date.today().isoformat()

# ============================================================
# 1. 修复分页页面
# ============================================================
def fix_pagination_pages():
    """修复 index-2 到 index-5 的SEO问题"""
    print("\n" + "=" * 60)
    print("1. 修复分页页面")
    print("=" * 60)
    fixed = 0
    for i in range(2, 6):
        filepath = os.path.join(BLOG_DIR, f'index-{i}.html')
        if not os.path.exists(filepath):
            continue
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()

        page_url = f"{SITE_URL}/blog/index-{i}"

        # 修改 robots: index → noindex
        content = content.replace(
            '<meta name="robots" content="index, follow">',
            '<meta name="robots" content="noindex, follow">'
        )

        # 修复 canonical
        content = re.sub(
            r'<link rel="canonical" href="https://biaoji\.skillxm\.cn/blog/">',
            f'<link rel="canonical" href="{page_url}">',
            content
        )

        # 修复 og:url
        content = re.sub(
            r'<meta property="og:url" content="https://biaoji\.skillxm\.cn/blog/">',
            f'<meta property="og:url" content="{page_url}">',
            content
        )

        # 修复 og:title (去掉 "第N页 - " 前缀的冗余)
        content = re.sub(
            r'<meta property="og:title" content="[^"]+">',
            f'<meta property="og:title" content="第{i}页 - 号码标记教程文档 - {SITE_NAME}">',
            content
        )

        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        fixed += 1
        print(f"  ✅ 修复: blog/index-{i}.html (noindex, canonical={page_url})")
    print(f"  共修复 {fixed} 个分页页面")

# ============================================================
# 2. 添加Twitter Card
# ============================================================
def add_twitter_card(content):
    """在og:image之后添加Twitter Card"""
    twitter_card = '''    
    <!-- Twitter Card -->
    <meta name="twitter:card" content="summary_large_image">
    <meta name="twitter:site" content="@biaojiwang">
    <meta name="twitter:title" content="TITLE_PLACEHOLDER">
    <meta name="twitter:description" content="DESC_PLACEHOLDER">
    <meta name="twitter:image" content="IMG_PLACEHOLDER">'''
    return twitter_card

def get_twitter_card_with_title(content):
    """从现有OG标签提取title和description"""
    title_match = re.search(r'<meta property="og:title" content="([^"]+)">', content)
    desc_match = re.search(r'<meta property="og:description" content="([^"]+)">', content)
    img_match = re.search(r'<meta property="og:image" content="([^"]+)">', content)
    
    title = title_match.group(1) if title_match else SITE_NAME
    desc = desc_match.group(1) if desc_match else ""
    img = img_match.group(1) if img_match else f"{SITE_URL}/images/og-cover.jpg"
    
    return f'''    
    <!-- Twitter Card -->
    <meta name="twitter:card" content="summary_large_image">
    <meta name="twitter:title" content="{title}">
    <meta name="twitter:description" content="{desc}">
    <meta name="twitter:image" content="{img}">'''

# ============================================================
# 3. 获取文章标题描述
# ============================================================
def get_article_meta(content):
    """从HTML中提取文章的title和description"""
    title_match = re.search(r'<title>([^<]+)</title>', content)
    desc_match = re.search(r'<meta name="description" content="([^"]+)"', content)
    title = title_match.group(1) if title_match else ""
    desc = desc_match.group(1) if desc_match else ""
    return title, desc

# ============================================================
# 4. 生成BreadcrumbList
# ============================================================
def get_breadcrumb_json(article_title):
    return f'''    <!-- 结构化数据 - BreadcrumbList -->
    <script type="application/ld+json">
    {{
        "@context": "https://schema.org",
        "@type": "BreadcrumbList",
        "itemListElement": [
            {{
                "@type": "ListItem",
                "position": 1,
                "name": "首页",
                "item": "{SITE_URL}/"
            }},
            {{
                "@type": "ListItem",
                "position": 2,
                "name": "教程文档",
                "item": "{SITE_URL}/blog/"
            }},
            {{
                "@type": "ListItem",
                "position": 3,
                "name": "{article_title}"
            }}
        ]
    }}
    </script>'''

# ============================================================
# 5. 修复博客文章
# ============================================================
def fix_blog_articles():
    """批量修复所有博客文章"""
    print("\n" + "=" * 60)
    print("2. 修复博客文章 (Twitter Card + og:image + BreadcrumbList + Schema)")
    print("=" * 60)
    
    fixed_count = 0
    for filename in sorted(os.listdir(BLOG_DIR)):
        if not filename.endswith('.html'):
            continue
        if filename.startswith('index-') or filename == 'index.html':
            continue
        
        filepath = os.path.join(BLOG_DIR, filename)
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        clean_name = filename[:-5]
        article_title, article_desc = get_article_meta(content)
        short_title = article_title.replace(f" - {SITE_NAME}", "").strip()
        modified = False
        fixes = []
        
        # 4a. 修复 og:image (favicon.png → og-cover.jpg)
        if 'og:image" content="https://biaoji.skillxm.cn/images/favicon.png"' in content:
            content = content.replace(
                'og:image" content="https://biaoji.skillxm.cn/images/favicon.png"',
                'og:image" content="https://biaoji.skillxm.cn/images/og-cover.jpg"'
            )
            modified = True
            fixes.append("og:image→og-cover.jpg")
        
        # 4b. 添加 Twitter Card (如果不存在)
        if 'twitter:card' not in content:
            twitter_html = get_twitter_card_with_title(content)
            # 插入到 og:image 行之后
            og_image_match = re.search(r'<meta property="og:image".*?>', content)
            if og_image_match:
                insert_pos = og_image_match.end()
                content = content[:insert_pos] + twitter_html + content[insert_pos:]
                modified = True
                fixes.append("Twitter Card")
        
        # 4c. 添加 BreadcrumbList (如果不存在)
        if 'BreadcrumbList' not in content:
            breadcrumb = get_breadcrumb_json(short_title)
            # 插入到 Article schema 结束标签之前
            schema_end = content.find('</script>', content.find('"@type": "Article"'))
            if schema_end > 0:
                # 在下一个 <script 或 <style 之前插入
                content = content[:schema_end + 9] + '\n\n' + breadcrumb + '\n' + content[schema_end + 9:]
                modified = True
                fixes.append("BreadcrumbList")
        
        # 4d. 完善 Article Schema - 添加 articleSection
        if '"@type": "Article"' in content and '"articleSection"' not in content:
            # 从keywords提取分类
            kw_match = re.search(r'<meta name="keywords" content="([^"]+)"', content)
            if kw_match:
                first_kw = kw_match.group(1).split(',')[0].strip()
                # 在 datePublished 之前插入 articleSection
                content = content.replace(
                    '"datePublished"',
                    f'"articleSection": "{first_kw}",\n        "datePublished"'
                )
                modified = True
                fixes.append("articleSection")
        
        if modified:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            fixed_count += 1
            print(f"  ✅ {filename}: {', '.join(fixes)}")
    
    print(f"  共修复 {fixed_count} 篇博客文章")

# ============================================================
# 6. 修复首页
# ============================================================
def fix_homepage():
    """修复首页"""
    print("\n" + "=" * 60)
    print("3. 修复首页")
    print("=" * 60)
    
    filepath = os.path.join(PROJECT_ROOT, 'index.html')
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    modified = False
    fixes = []
    
    if 'twitter:card' not in content:
        twitter_html = get_twitter_card_with_title(content)
        og_image_match = re.search(r'<meta property="og:image".*?>', content)
        if og_image_match:
            insert_pos = og_image_match.end()
            content = content[:insert_pos] + twitter_html + content[insert_pos:]
            modified = True
            fixes.append("Twitter Card")
    
    if modified:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"  ✅ index.html: {', '.join(fixes)}")
    else:
        print("  ⏭️  已是最新，无需修复")

# ============================================================
# 7. 修复博客首页
# ============================================================
def fix_blog_index():
    """修复博客首页"""
    print("\n" + "=" * 60)
    print("4. 修复博客首页")
    print("=" * 60)
    
    filepath = os.path.join(BLOG_DIR, 'index.html')
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    modified = False
    fixes = []
    
    if 'twitter:card' not in content:
        twitter_html = get_twitter_card_with_title(content)
        og_image_match = re.search(r'<meta property="og:image".*?>', content)
        if og_image_match:
            insert_pos = og_image_match.end()
            content = content[:insert_pos] + twitter_html + content[insert_pos:]
            modified = True
            fixes.append("Twitter Card")
    
    if modified:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"  ✅ blog/index.html: {', '.join(fixes)}")
    else:
        print("  ⏭️  已是最新，无需修复")

# ============================================================
# 8. 修复docs/index.html
# ============================================================
def fix_docs_index():
    """修复docs/index.html"""
    print("\n" + "=" * 60)
    print("5. 修复 docs/index.html")
    print("=" * 60)
    
    filepath = os.path.join(DOCS_DIR, 'index.html')
    if not os.path.exists(filepath):
        print("  ⚠️  docs/index.html 不存在")
        return
    
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    modified = False
    fixes = []
    
    # 8a. 移动 favicon/apple-touch-icon 到 head 顶部
    favicon_links = '''    <link rel="icon" type="image/x-icon" href="/favicon.ico">
    <link rel="icon" type="image/png" sizes="64x64" href="/images/favicon.png">
    <link rel="apple-touch-icon" sizes="180x180" href="/images/apple-touch-icon.png">
'''
    if '<link rel="icon" type="image/x-icon"' not in content[:200]:
        # 在 <meta charset 之前插入
        content = content.replace('<meta charset="UTF-8">', favicon_links + '    <meta charset="UTF-8">')
        modified = True
        fixes.append("favicon links")
    
    # 8b. 添加 theme-color
    if 'theme-color' not in content:
        content = content.replace(
            '<meta charset="UTF-8">',
            '<meta charset="UTF-8">\n    <meta name="theme-color" content="#667eea">'
        )
        modified = True
        fixes.append("theme-color")
    
    # 8c. 添加 Twitter Card
    if 'twitter:card' not in content:
        twitter_html = get_twitter_card_with_title(content)
        og_image_match = re.search(r'<meta property="og:image".*?>', content)
        if og_image_match:
            insert_pos = og_image_match.end()
            content = content[:insert_pos] + twitter_html + content[insert_pos:]
            modified = True
            fixes.append("Twitter Card")
    
    # 8d. 修复 og:image
    if 'og:image" content="https://biaoji.skillxm.cn/images/favicon.png"' in content:
        content = content.replace(
            'og:image" content="https://biaoji.skillxm.cn/images/favicon.png"',
            'og:image" content="https://biaoji.skillxm.cn/images/og-cover.jpg"'
        )
        modified = True
        fixes.append("og:image→og-cover.jpg")
    
    # 8e. 添加 robots 标签优化
    if 'max-snippet' not in content:
        content = content.replace(
            '<meta name="robots" content="index, follow">',
            '<meta name="robots" content="index, follow, max-snippet:-1, max-image-preview:large">'
        )
        modified = True
        fixes.append("robots扩展")
    
    if modified:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"  ✅ docs/index.html: {', '.join(fixes)}")
    else:
        print("  ⏭️  已是最新，无需修复")

# ============================================================
# Main
# ============================================================
def main():
    print("=" * 60)
    print("全站SEO/GEO审计批量修复")
    print(f"日期: {TODAY}")
    print("=" * 60)
    
    fix_pagination_pages()
    fix_blog_articles()
    fix_homepage()
    fix_blog_index()
    fix_docs_index()
    
    print("\n" + "=" * 60)
    print("全部修复完成！")
    print("=" * 60)

if __name__ == "__main__":
    main()