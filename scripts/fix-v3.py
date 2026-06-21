#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
V3修复：
1. 删除所有ICP备案号
2. 为图片添加width/height属性减少CLS
3. 为缺少<main>的页面添加<main>标签
"""

import os
import re
import glob

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def remove_icp_from_file(filepath):
    """删除文件中的ICP备案号"""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    original = content

    # 删除各种格式的ICP行
    patterns = [
        r'<p[^>]*style="[^"]*margin-top[^"]*"[^>]*>\s*<a href="https://beian\.miit\.gov\.cn/"[^>]*>京ICP备[^<]+</a>\s*</p>\n?',
        r'<p[^>]*>\s*<a href="https://beian\.miit\.gov\.cn/"[^>]*>京ICP备[^<]+</a>\s*</p>\n?',
        r'<p[^>]*>\s*<a href="https://beian\.miit\.gov\.cn/"[^>]*>[^<]*ICP[^<]+</a>\s*</p>\n?',
    ]
    for pattern in patterns:
        content = re.sub(pattern, '', content)

    # 同时删除baidu-site-verification中的占位符
    if 'your-baidu-verify-code' in content:
        content = re.sub(
            r'<meta name="baidu-site-verification" content="your-baidu-verify-code">\n?',
            '',
            content
        )

    if content != original:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        return True
    return False


def add_image_dimensions(filepath):
    """为图片添加width/height属性"""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    original = content

    # 查找没有width/height的img标签
    # 匹配 <img ... src="..." ...> 但没有width或height的
    def fix_img(match):
        full = match.group(0)
        if 'width=' in full or 'height=' in full:
            return full
        # 根据图片类型添加尺寸
        if 'favicon' in full or 'apple-touch-icon' in full:
            return full  # 跳过favicon
        if 'og-cover' in full:
            return full.replace('>', ' width="1200" height="630">')
        if 'haoma-biaoji' in full or 'hero' in full:
            return full.replace('>', ' width="800" height="450">')
        # 平台logo图片
        if any(p in full for p in ['360', 'tengxun', 'baidu', 'taidexiong', 'dianhuabang', 'sogou']):
            return full.replace('>', ' width="120" height="40">')
        # 默认尺寸
        return full.replace('>', ' width="400" height="300">')

    # 匹配没有width/height的img标签
    content = re.sub(r'<img\s+([^>]*)(?<!width=)(?<!height=)(?<!\s)>(?!\s*width)', fix_img, content)

    if content != original:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        return True
    return False


def add_main_tag(filepath):
    """为缺少<main>的页面添加<main>标签"""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    original = content

    # 如果已经有<main>，跳过
    if '<main' in content:
        return False

    # 在<body>后添加<main>
    if '<body>' in content:
        content = content.replace('<body>', '<body>\n    <main>')
        # 在第一个<footer>或</body>前闭合</main>
        if '<footer>' in content:
            content = content.replace('<footer>', '</main>\n    <footer>')
        else:
            content = content.replace('</body>', '</main>\n</body>')

        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        return True
    return False


def process_all_files():
    """处理所有HTML文件"""
    files = []
    files.append(os.path.join(BASE_DIR, 'index.html'))
    files.append(os.path.join(BASE_DIR, 'about.html'))
    files.append(os.path.join(BASE_DIR, 'docs', 'index.html'))
    files.append(os.path.join(BASE_DIR, 'dist', 'index.html'))
    files.extend(glob.glob(os.path.join(BASE_DIR, 'blog', '*.html')))
    files.extend(glob.glob(os.path.join(BASE_DIR, 'dist', 'blog', '*.html')))

    files = [f for f in files if os.path.exists(f)]

    icp_fixed = 0
    img_fixed = 0
    main_fixed = 0

    for f in files:
        if remove_icp_from_file(f):
            icp_fixed += 1
        if add_image_dimensions(f):
            img_fixed += 1
        if add_main_tag(f):
            main_fixed += 1

    print(f"✅ 删除ICP: {icp_fixed} 个文件")
    print(f"✅ 图片尺寸: {img_fixed} 个文件")
    print(f"✅ 添加main: {main_fixed} 个文件")


if __name__ == '__main__':
    print("=" * 50)
    print("V3修复：删除ICP + 图片尺寸 + main标签")
    print("=" * 50)
    process_all_files()
    print("=" * 50)
