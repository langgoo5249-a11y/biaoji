#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
站点地图自动生成脚本
根据项目中的HTML文件自动更新sitemap.xml
遵循Google Search Console的最佳实践
"""

import os
import sys
import datetime
from pathlib import Path
from typing import List, Dict

# 配置
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)
SITE_URL = "https://example.com"
SITEMAP_PATH = os.path.join(PROJECT_ROOT, "sitemap.xml")
BLOG_DIR = os.path.join(PROJECT_ROOT, "blog")
DOCS_DIR = os.path.join(PROJECT_ROOT, "docs")


def get_file_modified_time(file_path: str) -> str:
    """获取文件的最后修改时间，格式为ISO 8601"""
    try:
        mtime = os.path.getmtime(file_path)
        dt = datetime.datetime.fromtimestamp(mtime)
        return dt.date().isoformat()
    except Exception:
        return datetime.date.today().isoformat()


def find_html_files(directory: str, exclude_files: List[str] = None) -> List[str]:
    """查找目录中的所有HTML文件"""
    html_files = []
    exclude_files = exclude_files or []
    
    if os.path.exists(directory):
        for file in os.listdir(directory):
            if file.endswith(".html") and file not in exclude_files:
                html_files.append(os.path.join(directory, file))
    
    return html_files


def generate_sitemap() -> str:
    """生成完整的sitemap.xml内容"""
    urls = []
    
    # 1. 主页
    urls.append({
        "loc": f"{SITE_URL}/",
        "lastmod": datetime.date.today().isoformat(),
        "changefreq": "daily",
        "priority": "1.0"
    })
    
    # 2. docs页面
    if os.path.exists(DOCS_DIR):
        docs_index = os.path.join(DOCS_DIR, "index.html")
        if os.path.exists(docs_index):
            urls.append({
                "loc": f"{SITE_URL}/docs/",
                "lastmod": get_file_modified_time(docs_index),
                "changefreq": "weekly",
                "priority": "0.9"
            })
    
    # 3. blog目录
    blog_index = os.path.join(BLOG_DIR, "index.html")
    if os.path.exists(blog_index):
        urls.append({
            "loc": f"{SITE_URL}/blog/",
            "lastmod": get_file_modified_time(blog_index),
            "changefreq": "daily",
            "priority": "0.9"
        })
    
    # 4. 所有blog文章
    blog_html_files = find_html_files(BLOG_DIR, exclude_files=["index.html", "index-2.html", "index-3.html", "index-4.html", "index-5.html"])
    for file_path in sorted(blog_html_files, key=lambda x: -os.path.getmtime(x)):
        filename = os.path.basename(file_path)
        # 去掉.html后缀，使用clean URL
        clean_filename = filename[:-5] if filename.endswith('.html') else filename
        urls.append({
            "loc": f"{SITE_URL}/blog/{clean_filename}",
            "lastmod": get_file_modified_time(file_path),
            "changefreq": "monthly",
            "priority": "0.8"
        })
    
    # 5. 生成XML
    xml_content = ['<?xml version="1.0" encoding="UTF-8"?>']
    xml_content.append('<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">')
    
    for url in urls:
        xml_content.append('  <url>')
        xml_content.append(f'    <loc>{url["loc"]}</loc>')
        xml_content.append(f'    <lastmod>{url["lastmod"]}</lastmod>')
        xml_content.append(f'    <changefreq>{url["changefreq"]}</changefreq>')
        xml_content.append(f'    <priority>{url["priority"]}</priority>')
        xml_content.append('  </url>')
    
    xml_content.append('</urlset>')
    
    return '\n'.join(xml_content)


def main():
    """主函数"""
    print("=" * 60)
    print("站点地图自动生成器")
    print("=" * 60)
    
    # 生成sitemap
    print("\n正在生成站点地图...")
    sitemap_content = generate_sitemap()
    
    # 写入文件
    try:
        with open(SITEMAP_PATH, 'w', encoding='utf-8') as f:
            f.write(sitemap_content)
        
        print(f"✅ 站点地图已更新: {SITEMAP_PATH}")
        
        # 统计信息
        from xml.etree import ElementTree as ET
        root = ET.fromstring(sitemap_content)
        url_count = len(root.findall('.//{http://www.sitemaps.org/schemas/sitemap/0.9}url'))
        print(f"📊 包含 {url_count} 个URL")
        
        # 同时更新dist目录
        dist_sitemap = os.path.join(PROJECT_ROOT, "dist", "sitemap.xml")
        if os.path.exists(os.path.dirname(dist_sitemap)):
            with open(dist_sitemap, 'w', encoding='utf-8') as f:
                f.write(sitemap_content)
            print(f"✅ dist目录站点地图已同步更新")
        
        print("\n" + "=" * 60)
        print("完成！")
        print("=" * 60)
        return 0
        
    except Exception as e:
        print(f"❌ 错误: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
