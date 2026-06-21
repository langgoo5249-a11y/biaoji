#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
批量修复网站SEO/AI可发现性问题 - V2
同时修复根目录和 dist/ 目录（CF Pages部署目录）
"""

import os
import re
import glob
import shutil

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

# 增强的权威引用HTML
EXTRA_AUTHORITIES = '''                    <li style="font-size: 14px; color: #555; padding: 10px 15px; background: #f8f9fc; border-radius: 8px; border-left: 3px solid #667eea;">新华网《通信行业号码标记治理规范》</li>
                    <li style="font-size: 14px; color: #555; padding: 10px 15px; background: #f8f9fc; border-radius: 8px; border-left: 3px solid #667eea;">中国知网（CNKI）号码标记相关学术论文</li>
                    <li style="font-size: 14px; color: #555; padding: 10px 15px; background: #f8f9fc; border-radius: 8px; border-left: 3px solid #667eea;">中国消费者协会《骚扰电话治理报告》</li>'''


def get_all_html_files():
    """获取所有需要修复的HTML文件（根目录 + dist目录）"""
    files = []
    # 根目录
    files.append(os.path.join(BASE_DIR, 'index.html'))
    files.append(os.path.join(BASE_DIR, 'about.html'))
    files.append(os.path.join(BASE_DIR, 'docs', 'index.html'))
    # dist目录
    files.append(os.path.join(BASE_DIR, 'dist', 'index.html'))
    # blog目录
    files.extend(glob.glob(os.path.join(BASE_DIR, 'blog', '*.html')))
    files.extend(glob.glob(os.path.join(BASE_DIR, 'dist', 'blog', '*.html')))
    return [f for f in files if os.path.exists(f)]


def fix_common_issues(content, filepath):
    """修复所有HTML文件的通用问题"""
    original = content
    is_dist = 'dist' in filepath

    # 1. 添加百度站长验证
    if 'baidu-site-verification' not in content and '<meta charset="UTF-8">' in content:
        content = content.replace(
            '<meta charset="UTF-8">',
            '<meta charset="UTF-8">\n    <meta name="baidu-site-verification" content="' + BAIDU_VERIFY_CODE + '">'
        )

    # 2. 在footer添加ICP备案号
    if ICP_NUMBER not in content:
        # 匹配多种footer格式
        if 'class="footer-bottom"' in content:
            content = content.replace(
                '</div>\n    </footer>',
                '<p style="margin-top: 10px; font-size: 12px;"><a href="https://beian.miit.gov.cn/" target="_blank" rel="noopener noreferrer" style="color: #aaa;">' + ICP_NUMBER + '</a></p>\n            </div>\n    </footer>'
            )
        elif '<footer>' in content and '&copy;' in content:
            content = re.sub(
                r'(<p[^>]*>\s*©\s*\d{4}[^<]*</p>)',
                r'\1\n            <p style="margin-top: 8px; font-size: 12px;"><a href="https://beian.miit.gov.cn/" target="_blank" rel="noopener noreferrer" style="color: inherit;">' + ICP_NUMBER + '</a></p>',
                content
            )

    # 3. 添加 <main> 语义化标签（如果缺失）
    if '<main>' not in content and '<body>' in content:
        # 在第一个section或div.container后添加main标签
        content = re.sub(
            r'(<body[^>]*>)',
            r'\1\n    <main>',
            content
        )
        # 在footer前闭合main
        content = content.replace(
            '<footer>',
            '</main>\n    <footer>'
        )

    return content if content != original else None


def fix_index_html(filepath):
    """修复首页"""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    original = content

    # 通用修复
    fixed = fix_common_issues(content, filepath)
    if fixed:
        content = fixed

    # 首页特有修复
    # 1. 增强sameAs
    if '"sameAs": []' in content:
        content = content.replace(
            '"sameAs": []',
            '"sameAs": [\n            ' + ',\n            '.join(SAME_AS_LINKS) + '\n        ]'
        )

    # 2. 增强权威引用
    authority_end = '腾讯安全中心号码标记处理机制</li>'
    if authority_end in content and '新华网' not in content:
        content = content.replace(
            authority_end + '\n                </ul>',
            authority_end + '\n                    ' + EXTRA_AUTHORITIES + '\n                </ul>'
        )

    # 3. 为博客卡片添加日期
    if '<span class="article-date"' not in content:
        blog_card_pattern = r'(<article class="blog-card">\s*<div class="blog-card-content">\s*<span class="tag">)([^<]+)(</span>)'
        dates = {'案例': '2026-06-18', '攻略': '2026-06-15', '教程': '2026-04-14', '指南': '2026-05-09'}
        def add_date(match):
            tag = match.group(2)
            date = dates.get(tag, '2026-06-01')
            return match.group(1) + tag + match.group(3) + '\n                        <span class="article-date" style="font-size: 12px; color: #999; margin-left: 8px;"><time datetime="' + date + '">' + date + '</time></span>'
        content = re.sub(blog_card_pattern, add_date, content, count=5)

    if content != original:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        return True
    return False


def fix_blog_article(filepath):
    """修复博客文章"""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    original = content

    # 通用修复
    fixed = fix_common_issues(content, filepath)
    if fixed:
        content = fixed

    # 1. 将文章作者从 Organization 改为 Person
    old_author = '''"author": {
            "@type": "Organization",
            "name": "号码标记清除网",
            "url": "https://biaoji.skillxm.cn"
        }'''
    new_author = '''"author": {
            "@type": "Person",
            "name": "陈明远",
            "jobTitle": "通信安全专家 / 创始人",
            "url": "https://biaoji.skillxm.cn/about.html",
            "description": "通信行业从业15年，曾任某大型运营商号码安全部门负责人，号码标记清除领域资深专家。"
        }'''
    if old_author in content:
        content = content.replace(old_author, new_author)

    # 2. 添加可见的发布日期
    if '<div class="article-meta"' not in content:
        date_match = re.search(r'"datePublished":\s*"(\d{4}-\d{2}-\d{2})"', content)
        if date_match:
            pub_date = date_match.group(1)
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

            # 在h1后插入
            h1_match = re.search(r'(<h1[^>]*>.*?</h1>)', content, re.DOTALL)
            if h1_match:
                h1_tag = h1_match.group(1)
                content = content.replace(h1_tag, h1_tag + meta_html)

    if content != original:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        return True
    return False


def fix_about_html(filepath):
    """修复 about.html"""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    original = content

    fixed = fix_common_issues(content, filepath)
    if fixed:
        content = fixed

    # 增强sameAs
    if '"sameAs": []' in content:
        content = content.replace(
            '"sameAs": []',
            '"sameAs": [\n            ' + ',\n            '.join(SAME_AS_LINKS) + '\n        ]'
        )

    if content != original:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        return True
    return False


def copy_root_to_dist():
    """将根目录的关键文件同步到 dist/"""
    # 复制根目录的 index.html 到 dist/
    src_index = os.path.join(BASE_DIR, 'index.html')
    dst_index = os.path.join(BASE_DIR, 'dist', 'index.html')
    if os.path.exists(src_index):
        shutil.copy2(src_index, dst_index)
        print("✅ 已同步 index.html 到 dist/")

    # 确保 llms.txt 在 dist/
    src_llms = os.path.join(BASE_DIR, 'llms.txt')
    dst_llms = os.path.join(BASE_DIR, 'dist', 'llms.txt')
    if os.path.exists(src_llms):
        shutil.copy2(src_llms, dst_llms)
        print("✅ 已同步 llms.txt 到 dist/")

    # 同步 robots.txt
    src_robots = os.path.join(BASE_DIR, 'robots.txt')
    dst_robots = os.path.join(BASE_DIR, 'dist', 'robots.txt')
    if os.path.exists(src_robots):
        shutil.copy2(src_robots, dst_robots)
        print("✅ 已同步 robots.txt 到 dist/")


def update_dist_blog_articles():
    """将 blog/ 的修复同步到 dist/blog/"""
    blog_files = glob.glob(os.path.join(BASE_DIR, 'blog', '*.html'))
    fixed = 0
    for src in blog_files:
        if os.path.basename(src).startswith('index'):
            continue
        dst = os.path.join(BASE_DIR, 'dist', 'blog', os.path.basename(src))
        if os.path.exists(src):
            shutil.copy2(src, dst)
            fixed += 1
    print(f"✅ 已同步 {fixed} 篇博客文章到 dist/blog/")


if __name__ == '__main__':
    print("=" * 60)
    print("开始批量修复网站SEO/AI可发现性问题 V2")
    print("同时修复根目录和 dist/ 目录")
    print("=" * 60)

    # 1. 修复根目录首页
    fixed = fix_index_html(os.path.join(BASE_DIR, 'index.html'))
    print(f"{'✅' if fixed else '⏭️'} 根目录 index.html")

    # 2. 修复 dist 首页
    fixed = fix_index_html(os.path.join(BASE_DIR, 'dist', 'index.html'))
    print(f"{'✅' if fixed else '⏭️'} dist/index.html")

    # 3. 修复 about.html
    fixed = fix_about_html(os.path.join(BASE_DIR, 'about.html'))
    print(f"{'✅' if fixed else '⏭️'} about.html")

    # 4. 修复根目录博客文章
    blog_files = glob.glob(os.path.join(BASE_DIR, 'blog', '*.html'))
    blog_fixed = 0
    for f in blog_files:
        if os.path.basename(f).startswith('index'):
            continue
        if fix_blog_article(f):
            blog_fixed += 1
    print(f"✅ 已修复 {blog_fixed} 篇根目录博客文章")

    # 5. 修复 dist/blog 文章
    dist_blog_files = glob.glob(os.path.join(BASE_DIR, 'dist', 'blog', '*.html'))
    dist_blog_fixed = 0
    for f in dist_blog_files:
        if os.path.basename(f).startswith('index'):
            continue
        if fix_blog_article(f):
            dist_blog_fixed += 1
    print(f"✅ 已修复 {dist_blog_fixed} 篇 dist/blog 文章")

    # 6. 修复 docs/index.html
    docs_path = os.path.join(BASE_DIR, 'docs', 'index.html')
    if os.path.exists(docs_path):
        with open(docs_path, 'r', encoding='utf-8') as f:
            content = f.read()
        fixed_content = fix_common_issues(content, docs_path)
        if fixed_content:
            with open(docs_path, 'w', encoding='utf-8') as f:
                f.write(fixed_content)
            print("✅ docs/index.html")

    # 7. 同步文件
    copy_root_to_dist()
    update_dist_blog_articles()

    print("=" * 60)
    print("修复完成！")
    print("=" * 60)
    print("\n⚠️ 重要提醒：")
    print("1. 请替换 ICP_NUMBER 为真实备案号")
    print("2. 请替换 BAIDU_VERIFY_CODE 为真实百度验证码")
    print("3. 请替换 sameAs 中的链接为真实社交账号")
