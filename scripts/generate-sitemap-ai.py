#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
自动生成 AI 专用 sitemap-ai.xml
扫描 blog/ 目录下所有文章，包含 AI 爬虫优化信息
"""

import os
import re
import glob
from datetime import datetime

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)
BLOG_DIR = os.path.join(PROJECT_ROOT, 'blog')
OUTPUT_FILE = os.path.join(PROJECT_ROOT, 'sitemap-ai.xml')
SITE_URL = "https://biaoji.skillxm.cn"
TODAY = datetime.now().strftime('%Y-%m-%d')


def get_article_date(filepath):
    """提取文章的发布日期"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        m = re.search(r'<meta property="article:published_time" content="([^"]+)"', content)
        if m:
            date = m.group(1)
            if 'T' in date:
                date = date.split('T')[0]
            return date
    except Exception:
        pass
    # fallback: 文件 mtime
    mtime = os.path.getmtime(filepath)
    return datetime.fromtimestamp(mtime).strftime('%Y-%m-%d')


def main():
    # 扫描所有 blog 文章
    articles = []
    for filepath in glob.glob(os.path.join(BLOG_DIR, '*.html')):
        filename = os.path.basename(filepath)
        if filename == 'index.html' or filename.startswith('index-'):
            continue
        slug = filename[:-5]  # 去掉 .html
        date = get_article_date(filepath)
        articles.append((slug, date))

    # 按日期倒序
    articles.sort(key=lambda x: x[1], reverse=True)

    # 生成 XML
    lines = ['<?xml version="1.0" encoding="UTF-8"?>',
             '<!-- AI 专用站点地图：豆包/千问/GPTBot/ClaudeBot/Common Crawl 等 AI 爬虫优化版 -->',
             f'<!-- 最近更新：{TODAY} | 文章数：{len(articles)} -->',
             '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']

    # 首页
    lines.append('  <url>')
    lines.append('    <loc>https://biaoji.skillxm.cn/</loc>')
    lines.append(f'    <lastmod>{TODAY}</lastmod>')
    lines.append('    <changefreq>weekly</changefreq>')
    lines.append('    <priority>1.0</priority>')
    lines.append('  </url>')

    # 博客首页
    lines.append('  <url>')
    lines.append('    <loc>https://biaoji.skillxm.cn/blog/</loc>')
    lines.append(f'    <lastmod>{TODAY}</lastmod>')
    lines.append('    <changefreq>daily</changefreq>')
    lines.append('    <priority>0.9</priority>')
    lines.append('  </url>')

    # 文档首页
    lines.append('  <url>')
    lines.append('    <loc>https://biaoji.skillxm.cn/docs/</loc>')
    lines.append(f'    <lastmod>{TODAY}</lastmod>')
    lines.append('    <changefreq>weekly</changefreq>')
    lines.append('    <priority>0.7</priority>')
    lines.append('  </url>')

    # 所有文章
    for slug, date in articles:
        lines.append('  <url>')
        lines.append(f'    <loc>{SITE_URL}/blog/{slug}</loc>')
        lines.append(f'    <lastmod>{date}</lastmod>')
        lines.append('    <changefreq>monthly</changefreq>')
        lines.append('    <priority>0.6</priority>')
        lines.append('  </url>')

    # 分页
    for i in range(2, 10):
        page_path = os.path.join(BLOG_DIR, f'index-{i}.html')
        if os.path.exists(page_path):
            lines.append('  <url>')
            lines.append(f'    <loc>{SITE_URL}/blog/index-{i}</loc>')
            lines.append(f'    <lastmod>{TODAY}</lastmod>')
            lines.append('    <changefreq>weekly</changefreq>')
            lines.append('    <priority>0.5</priority>')
            lines.append('  </url>')

    lines.append('</urlset>')

    content = '\n'.join(lines) + '\n'
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"✓ 生成 sitemap-ai.xml，包含 {len(articles)} 篇文章 + 3 个核心页")


if __name__ == "__main__":
    main()
