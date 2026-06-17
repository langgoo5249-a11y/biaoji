#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
一键发布文章脚本
功能：修复所有文章日期 + 重新生成博客列表 + 自动 git commit/push
用法：python3 scripts/publish.py [commit message]
示例：python3 scripts/publish.py "feat: 发布两篇新文章"
"""
import os
import sys
import subprocess

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)


def run_step(name, cmd, cwd=PROJECT_ROOT, check=True):
    print(f"\n▶ Step {name}")
    result = subprocess.run(cmd, shell=True, cwd=cwd, capture_output=False)
    if check and result.returncode != 0:
        print(f"✗ Step {name} 失败，退出")
        sys.exit(1)
    return result.returncode == 0


def main():
    commit_msg = sys.argv[1] if len(sys.argv) > 1 else "chore: 更新博客内容"

    print("=" * 60)
    print("一键发布文章")
    print("=" * 60)

    # Step 1: 修复所有文章日期（从git历史回填真实日期）
    run_step("修复文章日期", "python3 scripts/fix-article-dates.py")

    # Step 2: 重新生成博客列表（按mtime倒序排列）
    run_step("生成博客列表", "python3 scripts/fix-blog-index-duplicates.py")

    # Step 3: 检查是否有变更
    result = subprocess.run(
        "git status --porcelain | grep -E '^( M|M |A |D )' | wc -l",
        shell=True, cwd=PROJECT_ROOT, capture_output=True, text=True
    )
    changed = int(result.stdout.strip())
    if changed == 0:
        print("\n✓ 没有变更需要提交，退出")
        sys.exit(0)

    print(f"\n▶ Step 提交并推送（共 {changed} 个文件变更）")

    # Step 4: git add
    run_step("git add", "git add -A")

    # Step 5: git commit
    run_step("git commit", f'git commit -m "{commit_msg}"', check=False)

    # Step 6: git push
    run_step("git push", "git push origin main", check=False)

    print("\n" + "=" * 60)
    print("✓ 发布完成！")
    print("=" * 60)


if __name__ == "__main__":
    main()
