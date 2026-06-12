#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
注入头条自动推送JS到博客文章 <head> 区域
当用户浏览页面时，页面链接会自动被头条蜘蛛爬取，提高页面收录率
"""

import os
import re

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)
BLOG_DIR = os.path.join(PROJECT_ROOT, 'blog')

# 头条自动推送 JS（用户提供的官方代码）
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

# 不需要注入的文件
SKIP_FILES = {
    'index.html',
}

# 已注入标记
INJECTED_MARKER = 'lf1-cdn-tos.bytegoofy.com/goofy/ttzz/push.js'


def inject_to_file(filepath):
    """注入头条 push JS 到 HTML 文件的 head 区域"""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # 已注入则跳过
    if INJECTED_MARKER in content:
        return False, '已注入'

    # 找到 </head> 位置，在它之前注入
    if '</head>' in content:
        new_content = content.replace('</head>', TOUTIAO_PUSH_JS + '</head>', 1)
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(new_content)
        return True, '已注入'
    return False, '未找到</head>'


def main():
    print("=" * 60)
    print("头条自动推送 JS 注入工具")
    print("=" * 60)

    injected = 0
    skipped = 0
    errors = 0

    for filename in os.listdir(BLOG_DIR):
        if not filename.endswith('.html'):
            continue
        if filename in SKIP_FILES or filename.startswith('index-'):
            continue
        filepath = os.path.join(BLOG_DIR, filename)
        try:
            ok, msg = inject_to_file(filepath)
            if ok:
                injected += 1
            else:
                skipped += 1
        except Exception as e:
            errors += 1
            print(f"  ✗ {filename}: {e}")

    print(f"\n✓ 完成！注入 {injected} 个文件，跳过 {skipped} 个，错误 {errors} 个")


if __name__ == "__main__":
    main()
