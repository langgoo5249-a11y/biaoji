#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
修复 blog/index.html 中重复的 article-card
通过重新执行 sync-blog-index.py 的核心逻辑，但用更严格的边界标记
"""

import os
import re
import sys

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)
BLOG_DIR = os.path.join(PROJECT_ROOT, 'blog')
INDEX_FILE = os.path.join(BLOG_DIR, 'index.html')

# 复用 sync-blog-index 的核心逻辑
sys.path.insert(0, SCRIPT_DIR)
import importlib.util
spec = importlib.util.spec_from_file_location("sync_blog_index", os.path.join(SCRIPT_DIR, "sync-blog-index.py"))
sync = importlib.util.module_from_spec(spec)
spec.loader.exec_module(sync)

print("=" * 60)
print("修复 blog/index.html 重复 article-card")
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
    info = sync.extract_article_info(filepath)
    if info:
        articles.append(info)

articles.sort(key=lambda x: x['date'], reverse=True)
print(f"    找到 {len(articles)} 篇文章")

# 2. 读取原文件
print("\n[2] 读取 blog/index.html...")
with open(INDEX_FILE, 'r', encoding='utf-8') as f:
    content = f.read()

# 3. 用明确的边界标记定位 article-grid
# 开始: <!-- Articles --><div><div class="article-grid">
# 结束: 真正的 </div></div> 后跟 <!-- Sidebar -->
start_marker = '<!-- Articles -->'
end_marker = '<!-- Sidebar -->'

start_pos = content.find(start_marker)
end_pos = content.find(end_marker)

if start_pos == -1 or end_pos == -1:
    print("    ✗ 未找到明确的边界标记")
    sys.exit(1)

# 在 [start_pos, end_pos] 范围内找 article-grid 的 </div></div>
# 实际上 article-grid 的结束是两个 </div>：
#   第一个 </div> 关闭 article-grid
#   第二个 </div> 关闭外层 wrapper
# 我们需要找到 article-grid 结束的那个 </div>
section = content[start_pos:end_pos]
last_div_in_section = section.rfind('</div>')
# 倒数第二个 </div> 才是 article-grid 结束
all_divs = [m.end() for m in re.finditer(r'</div>', section)]
if len(all_divs) < 2:
    print("    ✗ 找到的 </div> 数量不足")
    sys.exit(1)

# 倒数第一个 </div> 是外层 wrapper
# 倒数第二个 </div> 是 article-grid
article_grid_end = all_divs[-2]  # 在 section 中的相对位置

# 转换回 content 中的绝对位置
absolute_end = start_pos + article_grid_end

print(f"    文章区域: 字节 {start_pos} - {absolute_end} ({absolute_end - start_pos} 字节)")

# 4. 构造新内容
new_article_html = '\n'.join([sync.generate_article_card(art, i) for i, art in enumerate(articles)])

# 保留 <!-- Articles --><div><div class="article-grid"> 和最后的 </div></div>
header = '<!-- Articles -->\n        <div>\n            <div class="article-grid">\n'
# 找到 article-grid 之后的两个 </div> 的位置
# absolute_end 是 article-grid 关闭的 </div> 位置
# 后面是 wrapper 关闭 </div>，再后面是 <!-- Sidebar -->
footer_start = content[absolute_end:end_pos]
# footer_start 形如: "</div>\n        </div>\n\n        <!-- Sidebar -->"
# 我们要保留 Sidebar 注释，所以在 footer_start 末尾追加 '<!-- Sidebar -->'
footer_with_sidebar = footer_start + '<!-- Sidebar -->'
# 然后 content[end_pos + len('<!-- Sidebar -->'):] 是 Sidebar 之后的内容

new_content = content[:start_pos] + header + new_article_html + '\n            ' + footer_with_sidebar + content[end_pos + len('<!-- Sidebar -->'):]

# 5. 写回
print("\n[3] 写回修复后的 blog/index.html...")
with open(INDEX_FILE, 'w', encoding='utf-8') as f:
    f.write(new_content)

# 6. 验证
new_card_count = new_content.count('class="article-card"')
print(f"    修复后 article-card 数量: {new_card_count}")
print(f"    期望数量: {len(articles)}")

if new_card_count == len(articles):
    print("\n✓ 修复完成！")
else:
    print(f"\n⚠ 数量不匹配，请检查")

print("=" * 60)
