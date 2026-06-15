#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
注入头条自动推送JS到博客文章 <head> 区域
"""

import os

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)
BLOG_DIR = os.path.join(PROJECT_ROOT, 'blog')

TOUTIAO_PUSH_JS = '''    <!-- 头条自动推送 -->
    <script>
    (function(){
    var el = document.createElement("script");
    el.src = "https://lf1-cdn-tos.bytegoofy.com/goofy/ttzz/push.js?25338980a0c1c052717c0a92ce648c43b0665f4571a5b089a4b9e0a4c8b67e74d8c6aafbb6e83e7a78c9e7d28e6c5a9";
    el.id = "ttzz";
    var s = document.getElementsByTagName("script")[0];
    s.parentNode.insertBefore(el, s);
    })(window)
    </script>
'''

SKIP_FILES = {'index.html'}
INJECTED_MARKER = 'lf1-cdn-tos.bytegoofy.com/goofy/ttzz/push.js'


def inject_to_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    if INJECTED_MARKER in content:
        return False
    if '</head>' in content:
        new_content = content.replace('</head>', TOUTIAO_PUSH_JS + '</head>', 1)
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(new_content)
        return True
    return False


def main():
    injected = 0
    skipped = 0
    for filename in os.listdir(BLOG_DIR):
        if not filename.endswith('.html'):
            continue
        if filename in SKIP_FILES or filename.startswith('index-'):
            continue
        filepath = os.path.join(BLOG_DIR, filename)
        try:
            if inject_to_file(filepath):
                injected += 1
            else:
                skipped += 1
        except Exception as e:
            print(f"  ✗ {filename}: {e}")
    print(f"✓ 完成！注入 {injected} 个文件，跳过 {skipped} 个")


if __name__ == "__main__":
    main()
