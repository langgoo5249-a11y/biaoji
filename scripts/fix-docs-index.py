#!/usr/bin/env python3
import os

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)
filepath = os.path.join(PROJECT_ROOT, 'docs', 'index.html')

with open(filepath, 'r') as f:
    content = f.read()

# Fix 1: Remove duplicate favicon links (lines 18-20)
old_dup = '''    <link rel="icon" type="image/x-icon" href="/favicon.ico">
    <link rel="icon" type="image/png" sizes="64x64" href="/images/favicon.png">
    <link rel="apple-touch-icon" sizes="180x180" href="/images/apple-touch-icon.png">
    
    <meta property="og:title"'''
new_clean = '''
    <meta property="og:title"'''
content = content.replace(old_dup, new_clean)

# Fix 2: Fix indentation on line 4
content = content.replace('        <link rel="icon"', '    <link rel="icon"')

# Fix 3: Fix twitter:image
content = content.replace(
    '<meta name="twitter:image" content="https://example.com/images/favicon.png">',
    '<meta name="twitter:image" content="https://example.com/images/og-cover.jpg">'
)

with open(filepath, 'w') as f:
    f.write(content)
print('docs/index.html fixed')