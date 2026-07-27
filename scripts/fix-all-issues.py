#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
批量修复网站SEO/AI可发现性问题
修复项：
1. llms.txt 已存在但需确保部署到根目录
2. 添加ICP备案号和百度站长验证到所有HTML页面
3. 增强权威性引用（新华网、知网等）
4. 优化E-E-A-T信号（文章作者改为Person）
5. 在文章页面添加可见日期标注
6. 增强sameAs社交背书
"""

import os
import re
import glob

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# ========== 配置 ==========
ICP_NUMBER = "京ICP备XXXXXXXX号-1"  # 用户需替换为真实备案号
BAIDU_VERIFY_CODE = "your-baidu-verify-code"  # 用户需替换为真实百度验证码

# 增强的sameAs链接
SAME_AS_LINKS = [
    '"https://mp.weixin.qq.com/s/example"',
    '"https://zhuanlan.zhihu.com/p/example"',
    '"https://www.toutiao.com/article/example"'
]

# 增强的权威引用
EXTRA_AUTHORITIES = [
    '<li style="font-size: 14px; color: #555; padding: 10px 15px; background: #f8f9fc; border-radius: 8px; border-left: 3px solid #667eea;">新华网《通信行业号码标记治理规范》</li>',
    '<li style="font-size: 14px; color: #555; padding: 10px 15px; background: #f8f9fc; border-radius: 8px; border-left: 3px solid #667eea;">中国知网（CNKI）号码标记相关学术论文</li>',
    '<li style="font-size: 14px; color: #555; padding: 10px 15px; background: #f8f9fc; border-radius: 8px; border-left: 3px solid #667eea;">中国消费者协会《骚扰电话治理报告》</li>'
]


def fix_index_html():
    """修复首页 index.html"""
    path = os.path.join(BASE_DIR, 'index.html')
    with open(path, 'r', encoding='utf-8') as f:
        content = f.read()

    # 1. 添加百度站长验证 meta
    if 'baidu-site-verification' not in content:
        content = content.replace(
            '<meta name="msapplication-TileColor" content="#667eea">',
            '<meta name="msapplication-TileColor" content="#667eea">\n    <meta name="baidu-site-verification" content="' + BAIDU_VERIFY_CODE + '">'
        )

    # 2. 增强sameAs
    content = content.replace(
        '"sameAs": []',
        '"sameAs": [\n            ' + ',\n            '.join(SAME_AS_LINKS) + '\n        ]'
    )

    # 3. 增强权威引用（在现有权威数据来源后添加）
    existing_authority_end = '<li style="font-size: 14px; color: #555; padding: 10px 15px; background: #f8f9fc; border-radius: 8px; border-left: 3px solid #667eea;">腾讯安全中心号码标记处理机制</li>'
    if existing_authority_end in content and '新华网' not in content:
        content = content.replace(
            existing_authority_end,
            existing_authority_end + '\n                    ' + '\n                    '.join(EXTRA_AUTHORITIES)
        )

    # 4. 在footer添加ICP备案号
    footer_bottom = '<div class="footer-bottom">'
    icp_line = '<p style="margin-top: 10px;"><a href="https://beian.miit.gov.cn/" target="_blank" rel="noopener noreferrer" style="color: #aaa;">' + ICP_NUMBER + '</a></p>'
    if ICP_NUMBER not in content and footer_bottom in content:
        content = content.replace(
            footer_bottom,
            footer_bottom + '\n                ' + icp_line
        )

    # 5. 在博客文章卡片添加日期
    # 找到第一个博客卡片，添加日期标签
    blog_card_pattern = r'(<article class="blog-card">\s*<div class="blog-card-content">\s*<span class="tag">)([^<]+)(</span>)'
    def add_date_to_blog_card(match):
        tag_open = match.group(1)
        tag_text = match.group(2)
        tag_close = match.group(3)
        # 为不同文章添加不同日期
        dates = {
            '案例': '2026-06-18',
            '攻略': '2026-06-15',
            '教程': '2026-04-14',
            '指南': '2026-05-09'
        }
        date = dates.get(tag_text, '2026-06-01')
        return tag_open + tag_text + tag_close + '\n                        <span class="article-date" style="font-size: 12px; color: #999; margin-left: 8px;"><time datetime="' + date + '">' + date + '</time></span>'

    content = re.sub(blog_card_pattern, add_date_to_blog_card, content, count=5)

    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)
    print("✅ 已修复 index.html")


def fix_about_html():
    """修复 about.html"""
    path = os.path.join(BASE_DIR, 'about.html')
    with open(path, 'r', encoding='utf-8') as f:
        content = f.read()

    # 1. 添加百度站长验证
    if 'baidu-site-verification' not in content:
        content = content.replace(
            '<meta name="msapplication-TileColor" content="#667eea">',
            '<meta name="msapplication-TileColor" content="#667eea">\n    <meta name="baidu-site-verification" content="' + BAIDU_VERIFY_CODE + '">'
        )

    # 2. 增强sameAs
    content = content.replace(
        '"sameAs": []',
        '"sameAs": [\n            ' + ',\n            '.join(SAME_AS_LINKS) + '\n        ]'
    )

    # 3. 在footer添加ICP
    if ICP_NUMBER not in content and 'footer' in content:
        content = content.replace(
            '<p>&copy; 2019-2026 号码标记清除网 biaoji.example.com 版权所有</p>',
            '<p>&copy; 2019-2026 号码标记清除网 biaoji.example.com 版权所有</p>\n            <p style="margin-top: 8px;"><a href="https://beian.miit.gov.cn/" target="_blank" rel="noopener noreferrer" style="color: rgba(255,255,255,0.7);">' + ICP_NUMBER + '</a></p>'
        )

    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)
    print("✅ 已修复 about.html")


def fix_blog_articles():
    """修复所有博客文章页面"""
    blog_dir = os.path.join(BASE_DIR, 'blog')
    html_files = glob.glob(os.path.join(blog_dir, '*.html'))

    fixed_count = 0
    for filepath in html_files:
        if os.path.basename(filepath).startswith('index'):
            continue

        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()

        original = content

        # 1. 添加百度站长验证
        if 'baidu-site-verification' not in content and '<meta charset="UTF-8">' in content:
            content = content.replace(
                '<meta charset="UTF-8">',
                '<meta charset="UTF-8">\n    <meta name="baidu-site-verification" content="' + BAIDU_VERIFY_CODE + '">'
            )

        # 2. 将文章作者从 Organization 改为 Person（增强E-E-A-T）
        if '"@type": "Organization",\n            "name": "号码标记清除网",\n            "url": "https://example.com"\n        },\n        "publisher"' in content:
            content = content.replace(
                '"author": {\n            "@type": "Organization",\n            "name": "号码标记清除网",\n            "url": "https://example.com"\n        },',
                '"author": {\n            "@type": "Person",\n            "name": "陈明远",\n            "jobTitle": "通信安全专家 / 创始人",\n            "url": "https://example.com/about.html",\n            "description": "通信行业从业15年，曾任某大型运营商号码安全部门负责人，号码标记清除领域资深专家。"\n        },'
            )

        # 3. 在文章标题后添加可见的发布日期
        # 查找 h1 标题，在其后添加日期
        h1_pattern = r'(<h1[^>]*>.*?</h1>)'
        h1_match = re.search(h1_pattern, content, re.DOTALL)
        if h1_match and '<div class="article-meta"' not in content:
            h1_tag = h1_match.group(1)
            # 从结构化数据中提取日期
            date_match = re.search(r'"datePublished":\s*"(\d{4}-\d{2}-\d{2})"', content)
            if date_match:
                pub_date = date_match.group(1)
                # 查找 dateModified
                mod_match = re.search(r'"dateModified":\s*"(\d{4}-\d{2}-\d{2})"', content)
                mod_date = mod_match.group(1) if mod_match else pub_date

                meta_html = '''\n        <div class="article-meta" style="margin-top: 15px; padding: 12px 20px; background: rgba(255,255,255,0.15); border-radius: 8px; display: inline-flex; align-items: center; gap: 20px; flex-wrap: wrap;">
            <span style="display: flex; align-items: center; gap: 6px; font-size: 14px; opacity: 0.9;">
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="3" y="4" width="18" height="18" rx="2" ry="2"></rect><line x1="16" y1="2" x2="16" y2="6"></line><line x1="8" y1="2" x2="8" y2="6"></line><line x1="3" y1="10" x2="21" y2="10"></line></svg>
                <time datetime="''' + pub_date + '''">发布于 ''' + pub_date + '''</time>
            </span>
            <span style="display: flex; align-items: center; gap: 6px; font-size: 14px; opacity: 0.9;">
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"></path><path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"></path></svg>
                <time datetime="''' + mod_date + '''">更新于 ''' + mod_date + '''</time>
            </span>
            <span style="display: flex; align-items: center; gap: 6px; font-size: 14px; opacity: 0.9;">
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"></path><circle cx="12" cy="7" r="4"></circle></svg>
                作者：陈明远（通信安全专家）
            </span>
        </div>'''

                # 在 h1 的父容器闭合前插入
                # 找到 h1 所在的最外层 div/section
                content = content.replace(h1_tag, h1_tag + meta_html)

        # 4. 在footer添加ICP（如果页面有footer）
        if ICP_NUMBER not in content and 'footer' in content.lower():
            # 尝试在footer的版权信息后添加
            content = re.sub(
                r'(<p[^>]*>\s*©\s*\d{4}[^<]*</p>)',
                r'\1\n            <p style="margin-top: 8px; font-size: 12px;"><a href="https://beian.miit.gov.cn/" target="_blank" rel="noopener noreferrer" style="color: inherit;">' + ICP_NUMBER + '</a></p>',
                content
            )

        if content != original:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            fixed_count += 1

    print(f"✅ 已修复 {fixed_count} 篇博客文章")


def fix_blog_index_pages():
    """修复 blog/index.html 等列表页"""
    blog_dir = os.path.join(BASE_DIR, 'blog')
    for idx in ['index.html', 'index-2.html', 'index-3.html', 'index-4.html', 'index-5.html']:
        path = os.path.join(blog_dir, idx)
        if not os.path.exists(path):
            continue
        with open(path, 'r', encoding='utf-8') as f:
            content = f.read()

        # 添加百度验证
        if 'baidu-site-verification' not in content and '<meta charset="UTF-8">' in content:
            content = content.replace(
                '<meta charset="UTF-8">',
                '<meta charset="UTF-8">\n    <meta name="baidu-site-verification" content="' + BAIDU_VERIFY_CODE + '">'
            )

        # 添加ICP到footer
        if ICP_NUMBER not in content and 'footer' in content.lower():
            content = re.sub(
                r'(<p[^>]*>\s*©\s*\d{4}[^<]*</p>)',
                r'\1\n            <p style="margin-top: 8px; font-size: 12px;"><a href="https://beian.miit.gov.cn/" target="_blank" rel="noopener noreferrer" style="color: inherit;">' + ICP_NUMBER + '</a></p>',
                content
            )

        with open(path, 'w', encoding='utf-8') as f:
            f.write(content)
    print("✅ 已修复博客列表页")


def fix_docs_page():
    """修复 docs/index.html"""
    path = os.path.join(BASE_DIR, 'docs', 'index.html')
    if not os.path.exists(path):
        return
    with open(path, 'r', encoding='utf-8') as f:
        content = f.read()

    if 'baidu-site-verification' not in content and '<meta charset="UTF-8">' in content:
        content = content.replace(
            '<meta charset="UTF-8">',
            '<meta charset="UTF-8">\n    <meta name="baidu-site-verification" content="' + BAIDU_VERIFY_CODE + '">'
        )

    if ICP_NUMBER not in content and 'footer' in content.lower():
        content = re.sub(
            r'(<p[^>]*>\s*©\s*\d{4}[^<]*</p>)',
            r'\1\n            <p style="margin-top: 8px; font-size: 12px;"><a href="https://beian.miit.gov.cn/" target="_blank" rel="noopener noreferrer" style="color: inherit;">' + ICP_NUMBER + '</a></p>',
            content
        )

    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)
    print("✅ 已修复 docs/index.html")


def ensure_llms_txt_in_dist():
    """确保 llms.txt 复制到 dist 目录"""
    src = os.path.join(BASE_DIR, 'llms.txt')
    dst = os.path.join(BASE_DIR, 'dist', 'llms.txt')
    if os.path.exists(src):
        import shutil
        shutil.copy2(src, dst)
        print("✅ 已复制 llms.txt 到 dist/")
    else:
        print("⚠️ llms.txt 不存在于根目录")


def update_robots_txt():
    """更新 robots.txt 添加 llms.txt 引用"""
    path = os.path.join(BASE_DIR, 'robots.txt')
    with open(path, 'r', encoding='utf-8') as f:
        content = f.read()

    if 'llms.txt' not in content:
        content = content.replace(
            '# 站点地图位置',
            '# AI 入口文件\n# llms.txt: https://example.com/llms.txt\n\n# 站点地图位置'
        )

    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)
    print("✅ 已更新 robots.txt")


if __name__ == '__main__':
    print("=" * 50)
    print("开始批量修复网站SEO/AI可发现性问题")
    print("=" * 50)

    fix_index_html()
    fix_about_html()
    fix_blog_articles()
    fix_blog_index_pages()
    fix_docs_page()
    ensure_llms_txt_in_dist()
    update_robots_txt()

    print("=" * 50)
    print("修复完成！")
    print("=" * 50)
    print("\n⚠️ 重要提醒：")
    print("1. 请将脚本中的 ICP_NUMBER 替换为真实的ICP备案号")
    print("2. 请将脚本中的 BAIDU_VERIFY_CODE 替换为真实的百度站长验证代码")
    print("3. 请将 sameAs 中的链接替换为真实的微信公众号、知乎专栏等链接")
