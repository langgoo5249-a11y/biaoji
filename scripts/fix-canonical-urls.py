#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
修复所有博客文章中的canonical标签、OG标签和Schema标签
统一使用clean URL（去掉.html后缀）
"""

import os
import re
from pathlib import Path

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)
BLOG_DIR = os.path.join(PROJECT_ROOT, 'blog')
SITE_URL = "https://example.com"

def fix_article_file(file_path):
    """修复单个文章文件中的URL"""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    filename = os.path.basename(file_path)
    if filename == 'index.html' or filename.startswith('index-'):
        return False  # 跳过索引文件
    
    clean_name = filename[:-5] if filename.endswith('.html') else filename
    old_full_url = f"{SITE_URL}/blog/{filename}"
    new_full_url = f"{SITE_URL}/blog/{clean_name}"
    
    modified = False
    
    # 直接替换所有出现的旧URL
    if old_full_url in content:
        content = content.replace(old_full_url, new_full_url)
        modified = True
    
    if modified:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        return True
    
    return False

def fix_index_file(file_path, is_blog_index=False):
    """修复首页或博客索引页"""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    modified = False
    
    # 修复文章链接，去掉.html后缀
    # 查找 href="/blog/xxx.html" 格式的链接
    def replace_link(match):
        nonlocal modified
        before = match.group(1)
        url = match.group(2)
        after = match.group(3)
        if url.endswith('.html') and url != 'index.html' and not url.startswith('index-'):
            clean_url = url[:-5]
            modified = True
            return f'{before}/blog/{clean_url}{after}'
        return match.group(0)
    
    content = re.sub(r'(href=")/blog/([^"]+\.html)(")', replace_link, content)
    
    if modified:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        return True
    
    return False

def main():
    """主函数"""
    print("=" * 60)
    print("博客文章URL修复工具")
    print("=" * 60)
    
    total_files = 0
    fixed_files = 0
    
    # 1. 修复博客文章
    print("\n正在修复博客文章...")
    if os.path.exists(BLOG_DIR):
        for filename in os.listdir(BLOG_DIR):
            if filename.endswith('.html') and filename != 'index.html' and not filename.startswith('index-'):
                file_path = os.path.join(BLOG_DIR, filename)
                total_files += 1
                if fix_article_file(file_path):
                    fixed_files += 1
                    print(f"  ✅ 修复: {filename}")
    
    # 2. 修复首页
    print("\n正在修复首页...")
    index_path = os.path.join(PROJECT_ROOT, 'index.html')
    if os.path.exists(index_path):
        if fix_index_file(index_path):
            fixed_files += 1
            print("  ✅ 修复: index.html")
    
    # 3. 修复博客索引页
    print("\n正在修复博客索引页...")
    blog_index_path = os.path.join(BLOG_DIR, 'index.html')
    if os.path.exists(blog_index_path):
        if fix_index_file(blog_index_path, is_blog_index=True):
            fixed_files += 1
            print("  ✅ 修复: blog/index.html")
    
    print(f"\n完成！共检查 {total_files + 2} 个文件，修复 {fixed_files} 个文件。")
    return 0

if __name__ == "__main__":
    exit(main())
