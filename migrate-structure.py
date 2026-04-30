#!/usr/bin/env python3
"""
迁移脚本：将旧目录结构（按用户）迁移到新目录结构（按日期）

旧结构：x-收藏/handle/YYYY-MM-DD.md
新结构：x-收藏/YYYY-MM-DD/handle.md
"""

import json
import shutil
from pathlib import Path
from datetime import datetime

# 路径配置
CONTENT_DIR = Path.home() / "AI/hermes/input/learn/content"
X_DIR = CONTENT_DIR / "x-收藏"


def migrate():
    """执行迁移"""
    print("=" * 50)
    print("开始迁移目录结构")
    print("=" * 50)
    
    # 获取旧目录（按用户分的目录）
    old_dirs = []
    for d in X_DIR.iterdir():
        if d.is_dir() and not d.name.startswith(".") and not d.name.startswith("20"):
            old_dirs.append(d)
    
    print(f"发现 {len(old_dirs)} 个旧目录：")
    for d in old_dirs:
        print(f"  - {d.name}")
    
    # 迁移每个旧目录
    for old_dir in old_dirs:
        handle = old_dir.name
        print(f"\n处理 {handle}...")
        
        # 遍历旧目录中的文件
        for md_file in old_dir.glob("*.md"):
            # 从文件名提取日期
            date_str = md_file.stem  # 例如：2026-04-30
            
            # 创建新目录
            new_dir = X_DIR / date_str
            new_dir.mkdir(parents=True, exist_ok=True)
            
            # 读取旧文件内容
            with open(md_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 解析 JSON 内容
            try:
                # 提取 JSON 部分（跳过第一行标题）
                json_start = content.find('[')
                json_end = content.rfind(']') + 1
                if json_start >= 0 and json_end > json_start:
                    json_content = content[json_start:json_end]
                    tweets = json.loads(json_content)
                else:
                    tweets = []
            except:
                tweets = []
            
            # 写入新文件
            new_file = new_dir / f"{handle}.md"
            with open(new_file, 'w', encoding='utf-8') as f:
                f.write(f"# {handle} - {date_str}\n\n")
                f.write(f"共 {len(tweets)} 条推文\n\n")
                
                for tweet in tweets:
                    f.write(f"## {tweet.get('id', 'unknown')}\n\n")
                    f.write(f"{tweet.get('text', '')}\n\n")
                    f.write(f"- 👍 {tweet.get('likes', 0)} | 🔁 {tweet.get('retweets', 0)} | 💬 {tweet.get('replies', 0)} | 👁️ {tweet.get('views', 0)}\n")
                    f.write(f"- 🔗 {tweet.get('url', '')}\n\n")
                    f.write("---\n\n")
            
            print(f"  迁移 {md_file.name} -> {new_file}")
    
    # 更新每日汇总
    print("\n更新每日汇总...")
    for date_dir in X_DIR.iterdir():
        if date_dir.is_dir() and date_dir.name.startswith("20"):
            update_daily_summary(date_dir)
    
    # 更新总目录
    print("\n更新总目录...")
    update_index()
    
    # 删除旧目录
    print("\n删除旧目录...")
    for old_dir in old_dirs:
        shutil.rmtree(old_dir)
        print(f"  删除 {old_dir.name}")
    
    print("\n" + "=" * 50)
    print("迁移完成！")
    print("=" * 50)


def update_daily_summary(date_dir: Path):
    """更新每日汇总"""
    summary_file = date_dir / "summary.md"
    
    # 统计账号和推文数
    summaries = {}
    for md_file in date_dir.glob("*.md"):
        if md_file.name != "summary.md":
            handle = md_file.stem
            # 统计推文数量
            with open(md_file, 'r', encoding='utf-8') as f:
                content = f.read()
                tweet_count = content.count("## ")
                summaries[handle] = tweet_count
    
    # 写入汇总
    with open(summary_file, 'w', encoding='utf-8') as f:
        f.write(f"# 每日汇总 - {date_dir.name}\n\n")
        f.write(f"共抓取 {len(summaries)} 个账号\n\n")
        
        for account, count in sorted(summaries.items()):
            f.write(f"- **{account}**: {count} 条推文\n")
    
    print(f"  更新 {date_dir.name}/summary.md")


def update_index():
    """更新总目录"""
    index_file = X_DIR / "index.md"
    
    # 获取所有日期目录
    dates = sorted([d.name for d in X_DIR.iterdir() 
                   if d.is_dir() and d.name.startswith("20")])
    
    # 写入总目录
    with open(index_file, 'w', encoding='utf-8') as f:
        f.write("# X 收藏总目录\n\n")
        f.write(f"共 {len(dates)} 天的抓取记录\n\n")
        
        for date in dates:
            date_dir = X_DIR / date
            summary_file = date_dir / "summary.md"
            
            if summary_file.exists():
                with open(summary_file, 'r', encoding='utf-8') as sf:
                    lines = sf.readlines()
                    # 提取账号数量
                    account_count = 0
                    for line in lines:
                        if line.startswith("- **"):
                            account_count += 1
                    
                    f.write(f"## [{date}]({date}/)\n\n")
                    f.write(f"共 {account_count} 个账号\n\n")
            else:
                f.write(f"## [{date}]({date}/)\n\n")


if __name__ == "__main__":
    migrate()
