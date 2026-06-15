#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
修复所有文章发布日期 + 文件 mtime
基于 git 第一次 commit 的时间确定每篇文章的发布日期
"""
import os
import re
import subprocess
import sys
from datetime import datetime

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)
BLOG_DIR = os.path.join(PROJECT_ROOT, 'blog')


def get_first_commit_date(filepath):
    """从 git 历史获取文件的第一次 commit 日期"""
    rel = os.path.relpath(filepath, PROJECT_ROOT)
    try:
        result = subprocess.run(
            ['git', 'log', '--all', '--diff-filter=A', '--format=%ai', '--', rel],
            cwd=PROJECT_ROOT,
            capture_output=True, text=True, timeout=10
        )
        if result.returncode == 0 and result.stdout.strip():
            # 第一次 commit 是最后一个（最老的）
            lines = result.stdout.strip().split('\n')
            first = lines[-1].strip()
            # 格式: 2026-05-07 10:30:45 +0800
            return first.split(' ')[0]  # 取日期部分
    except Exception as e:
        print(f"  ⚠ git log 失败: {e}")
    return None


def update_meta_date(filepath, date_str):
    """更新 HTML 文件中的 article:published_time meta 标签"""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    original = content

    # 1. 更新或插入 article:published_time meta 标签
    # 匹配: <meta property="article:published_time" content="..." />  或  og:article:published_time
    meta_patterns = [
        r'<meta\s+property="og:article:published_time"\s+content="[^"]*"\s*/?>',
        r'<meta\s+property="article:published_time"\s+content="[^"]*"\s*/?>',
    ]
    new_meta = f'<meta property="article:published_time" content="{date_str}" />'

    matched = False
    for pattern in meta_patterns:
        if re.search(pattern, content):
            content = re.sub(pattern, new_meta, content)
            matched = True
            break

    if not matched:
        # 插入到 article:author 之后
        author_pattern = r'(<meta\s+property="article:author"\s+content="[^"]*"\s*/>)'
        if re.search(author_pattern, content):
            content = re.sub(author_pattern, r'\1\n    ' + new_meta, content, count=1)
        else:
            # 插入到 <head> 末尾
            content = content.replace('</head>', '    ' + new_meta + '\n</head>', 1)

    # 2. 更新文章内的 📅 YYYY-MM-DD 显示（如果存在）
    emoji_pattern = r'📅\s*\d{4}-\d{2}-\d{2}'
    content_with_emoji_updated = re.sub(emoji_pattern, f'📅 {date_str}', content)

    if content_with_emoji_updated != content:
        content = content_with_emoji_updated

    if content != original:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        return True
    return False


def main():
    print("=" * 60)
    print("修复所有文章发布日期 + 文件 mtime")
    print("=" * 60)

    # 扫描所有 blog 文章
    articles = []
    for filename in sorted(os.listdir(BLOG_DIR)):
        if not filename.endswith('.html'):
            continue
        if filename == 'index.html' or filename.startswith('index-'):
            continue
        filepath = os.path.join(BLOG_DIR, filename)
        articles.append((filename, filepath))

    print(f"\n找到 {len(articles)} 篇文章")

    print("\n[1] 提取每篇文章的首次 commit 日期...")
    article_dates = {}
    for filename, filepath in articles:
        date = get_first_commit_date(filepath)
        if date:
            article_dates[filename] = date
        else:
            print(f"  ⚠ {filename}: 无法获取 git 日期")
            article_dates[filename] = '2026-05-07'  # fallback

    # 统计日期分布
    from collections import Counter
    date_counter = Counter(article_dates.values())
    print(f"\n    日期分布:")
    for d, c in sorted(date_counter.items()):
        print(f"      {d}: {c} 篇")

    print("\n[2] 更新每篇文章的 meta 日期...")
    updated = 0
    for filename, filepath in articles:
        date = article_dates[filename]
        if update_meta_date(filepath, date):
            updated += 1

    print(f"    ✓ 更新了 {updated} 个文件的 meta 日期")

    print("\n[3] 更新文件 mtime...")
    mtime_updated = 0
    for filename, filepath in articles:
        date = article_dates[filename]
        # mtime 设为该日期的中午 12:00
        mtime_str = f"{date} 12:00:00"
        try:
            # 使用 utime 直接设置
            ts = int(datetime.strptime(mtime_str, '%Y-%m-%d %H:%M:%S').timestamp())
            os.utime(filepath, (ts, ts))
            mtime_updated += 1
        except Exception as e:
            print(f"  ⚠ {filename}: mtime 更新失败 - {e}")

    print(f"    ✓ 更新了 {mtime_updated} 个文件的 mtime")

    print("\n" + "=" * 60)
    print("✓ 完成！")
    print("=" * 60)


if __name__ == "__main__":
    main()
