#!/usr/bin/env python3
"""
Daily Summary — 每日汇总脚本
汇总当天所有抓取结果，生成每日报告
"""

import json
import sqlite3
from datetime import datetime, timedelta
from pathlib import Path

# 路径配置
BASE_DIR = Path(__file__).parent.parent.parent
INPUT_DIR = BASE_DIR / "input"
LEARN_DIR = INPUT_DIR / "learn"
DB_PATH = LEARN_DIR / "learning.db"
SUMMARY_DIR = INPUT_DIR / "每日汇总"


def generate_daily_summary():
    """生成每日汇总"""
    
    # 确保目录存在
    SUMMARY_DIR.mkdir(parents=True, exist_ok=True)
    
    # 获取今天的日期
    today = datetime.now().strftime("%Y-%m-%d")
    
    # 连接数据库
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # 获取今天的抓取历史
    cursor.execute('''
        SELECT account, fetch_time, has_new_content, tweets_count, replies_count, engagement_score
        FROM fetch_history
        WHERE DATE(fetch_time) = ?
        ORDER BY fetch_time
    ''', (today,))
    
    fetches = cursor.fetchall()
    
    # 获取今天的用户反馈
    cursor.execute('''
        SELECT account, feedback_type, feedback_time, reason
        FROM user_feedback
        WHERE DATE(feedback_time) = ?
        ORDER BY feedback_time
    ''', (today,))
    
    feedbacks = cursor.fetchall()
    
    # 统计数据
    total_fetches = len(fetches)
    total_accounts = len(set(f[0] for f in fetches))
    total_tweets = sum(f[3] for f in fetches)
    total_replies = sum(f[4] for f in fetches)
    total_engagement = sum(f[5] for f in fetches)
    
    new_content_count = sum(1 for f in fetches if f[2])
    
    # 生成报告
    report = f"""
# 每日汇总 — {today}

> 智能抓取调度系统
> 生成时间：{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

---

## 抓取统计

| 指标 | 数值 |
|------|------|
| 抓取次数 | {total_fetches} |
| 抓取账号数 | {total_accounts} |
| 推文总数 | {total_tweets} |
| 评论总数 | {total_replies} |
| 互动总分 | {total_engagement:.1f} |
| 有新内容次数 | {new_content_count} |
| 新内容率 | {new_content_count / total_fetches * 100:.1f}% |

---

## 抓取详情

| 时间 | 账号 | 新内容 | 推文 | 评论 | 互动分 |
|------|------|--------|------|------|--------|
"""
    
    for fetch in fetches:
        account, fetch_time, has_new, tweets, replies, engagement = fetch
        has_new_str = "✅" if has_new else "❌"
        report += f"| {fetch_time} | @{account} | {has_new_str} | {tweets} | {replies} | {engagement:.1f} |\n"
    
    report += f"""
---

## 用户反馈

| 时间 | 账号 | 类型 | 原因 |
|------|------|------|------|
"""
    
    for feedback in feedbacks:
        account, feedback_type, feedback_time, reason = feedback
        report += f"| {feedback_time} | @{account} | {feedback_type} | {reason} |\n"
    
    if not feedbacks:
        report += "| - | - | - | 暂无反馈 |\n"
    
    report += f"""
---

## 学习进展

### 活跃时段学习

| 账号 | 最活跃时段 | 置信度 |
|------|-----------|--------|
"""
    
    # 获取活跃时段统计
    cursor.execute('''
        SELECT account, hour, probability
        FROM active_hours_stats
        WHERE probability > 0.5
        ORDER BY account, probability DESC
    ''')
    
    active_hours = cursor.fetchall()
    
    # 按账号分组
    account_hours = {}
    for account, hour, probability in active_hours:
        if account not in account_hours:
            account_hours[account] = []
        account_hours[account].append((hour, probability))
    
    for account, hours in account_hours.items():
        if hours:
            best_hour, best_prob = hours[0]
            report += f"| @{account} | {best_hour}:00 | {best_prob:.1%} |\n"
    
    if not account_hours:
        report += "| - | - | - |\n"
    
    report += f"""
### 更新频率学习

| 账号 | 最可能频率 | 概率 |
|------|-----------|------|
"""
    
    # 获取更新频率统计
    cursor.execute('''
        SELECT account, frequency_type, probability
        FROM update_frequency_stats
        WHERE probability > 0.3
        ORDER BY account, probability DESC
    ''')
    
    frequencies = cursor.fetchall()
    
    # 按账号分组
    account_freqs = {}
    for account, freq_type, probability in frequencies:
        if account not in account_freqs:
            account_freqs[account] = []
        account_freqs[account].append((freq_type, probability))
    
    for account, freqs in account_freqs.items():
        if freqs:
            best_freq, best_prob = freqs[0]
            report += f"| @{account} | {best_freq} | {best_prob:.1%} |\n"
    
    if not account_freqs:
        report += "| - | - | - |\n"
    
    report += f"""
---

## 明日计划

### 建议抓取账号

基于学习结果，建议明天重点关注以下账号：

"""
    
    # 获取高优先级账号
    cursor.execute('''
        SELECT account, priority, frequency
        FROM account_profiles
        WHERE priority >= 2 AND status = 'active'
        ORDER BY priority DESC, frequency DESC
        LIMIT 5
    ''')
    
    top_accounts = cursor.fetchall()
    
    for i, (account, priority, frequency) in enumerate(top_accounts, 1):
        report += f"{i}. **@{account}** (优先级：{'⭐' * priority}，频率：{frequency})\n"
    
    report += f"""
---

*本报告由智能抓取调度系统自动生成*
"""
    
    # 保存报告
    report_path = SUMMARY_DIR / f"{today}.md"
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write(report)
    
    # 关闭数据库连接
    conn.close()
    
    print(f"✅ 每日汇总生成完成: {report_path}")
    
    return report_path


def main():
    """主函数"""
    print("=========================================")
    print("每日汇总生成")
    print("=========================================")
    print()
    
    # 生成每日汇总
    report_path = generate_daily_summary()
    
    print()
    print("=========================================")
    print("生成完成")
    print("=========================================")
    print()
    print(f"报告位置: {report_path}")
    print()


if __name__ == "__main__":
    main()
