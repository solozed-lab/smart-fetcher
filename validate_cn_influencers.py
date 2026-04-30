#!/usr/bin/env python3
"""
CN Influencer Validation — 中文大佬验证脚本
验证中文大佬的内容质量
"""

import json
import sqlite3
import subprocess
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any

# 路径配置
BASE_DIR = Path(__file__).parent.parent.parent
INPUT_DIR = BASE_DIR / "input"
LEARN_DIR = INPUT_DIR / "learn"
DB_PATH = LEARN_DIR / "learning.db"
PROFILES_PATH = LEARN_DIR / "account-profiles.json"


def fetch_account_tweets(account: str, limit: int = 10) -> List[Dict[str, Any]]:
    """获取账号的推文"""
    try:
        cmd = f'autocli twitter search "from:{account}" --limit {limit} --format json'
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=30)
        
        # autocli sometimes returns non-zero exit code with valid JSON in stdout
        output = result.stdout.strip()
        if output:
            data = json.loads(output)
            if data:
                return data
    except Exception as e:
        print(f"Error fetching tweets for {account}: {e}")
    
    return []


def analyze_tweets(tweets: List[Dict[str, Any]]) -> Dict[str, Any]:
    """分析推文内容"""
    if not tweets:
        return {
            'count': 0,
            'avg_likes': 0,
            'avg_retweets': 0,
            'avg_replies': 0,
            'key_topics': [],
            'quality_score': 0
        }
    
    total_likes = sum(t.get('likes', 0) for t in tweets)
    total_retweets = sum(t.get('retweets', 0) for t in tweets)
    total_replies = sum(t.get('replies', 0) for t in tweets)
    
    avg_likes = total_likes / len(tweets)
    avg_retweets = total_retweets / len(tweets)
    avg_replies = total_replies / len(tweets)
    
    # 提取关键话题
    topics = {}
    for tweet in tweets:
        text = tweet.get('text', '').lower()
        keywords = ['ai', 'agent', 'llm', 'model', 'tool', 'workflow', 'prompt', '编程', '开发', '产品']
        for keyword in keywords:
            if keyword in text:
                topics[keyword] = topics.get(keyword, 0) + 1
    
    # 计算质量分数
    # 质量分数 = 平均互动 / 100（标准化到 0-1）
    quality_score = min(1.0, (avg_likes + avg_retweets * 2 + avg_replies) / 1000)
    
    return {
        'count': len(tweets),
        'avg_likes': avg_likes,
        'avg_retweets': avg_retweets,
        'avg_replies': avg_replies,
        'key_topics': sorted(topics.items(), key=lambda x: x[1], reverse=True)[:5],
        'quality_score': quality_score
    }


def validate_cn_influencer(account: str) -> Dict[str, Any]:
    """验证中文大佬"""
    print(f"验证 @{account}...")
    
    # 获取推文
    tweets = fetch_account_tweets(account, limit=10)
    
    if not tweets:
        return {
            'account': account,
            'status': 'error',
            'error': '无法获取推文',
            'quality_score': 0
        }
    
    # 分析推文
    analysis = analyze_tweets(tweets)
    
    # 确定状态
    if analysis['quality_score'] >= 0.7:
        status = 'high_quality'
    elif analysis['quality_score'] >= 0.3:
        status = 'medium_quality'
    else:
        status = 'low_quality'
    
    return {
        'account': account,
        'status': status,
        'analysis': analysis,
        'quality_score': analysis['quality_score'],
        'tweets_sample': tweets[:3]  # 保存前 3 条推文作为样本
    }


def update_account_status(account: str, status: str, quality_score: float):
    """更新账号状态"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # 更新账号画像
    cursor.execute('''
        UPDATE account_profiles
        SET status = ?, updated_at = ?
        WHERE account = ?
    ''', (status, datetime.now().isoformat(), account))
    
    # 记录验证结果
    cursor.execute('''
        INSERT INTO user_feedback (account, feedback_type, feedback_time, reason)
        VALUES (?, ?, ?, ?)
    ''', (account, 'validation', datetime.now().isoformat(), 
          f"质量分数: {quality_score:.2f}, 状态: {status}"))
    
    conn.commit()
    conn.close()


def generate_validation_report(results: List[Dict[str, Any]]):
    """生成验证报告"""
    today = datetime.now().strftime("%Y-%m-%d")
    report_path = INPUT_DIR / "中文大佬验证" / f"{today}.md"
    
    # 确保目录存在
    report_path.parent.mkdir(parents=True, exist_ok=True)
    
    # 生成报告
    report = f"""
# 中文大佬验证报告 — {today}

> 智能抓取调度系统
> 生成时间：{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

---

## 验证统计

| 指标 | 数值 |
|------|------|
| 验证账号数 | {len(results)} |
| 高质量账号 | {sum(1 for r in results if r.get('status') == 'high_quality')} |
| 中质量账号 | {sum(1 for r in results if r.get('status') == 'medium_quality')} |
| 低质量账号 | {sum(1 for r in results if r.get('status') == 'low_quality')} |
| 验证失败 | {sum(1 for r in results if r.get('status') == 'error')} |

---

## 验证详情

| 账号 | 状态 | 质量分数 | 平均点赞 | 平均转发 | 关键话题 |
|------|------|----------|----------|----------|----------|
"""
    
    for result in results:
        account = result.get('account', '')
        status = result.get('status', 'unknown')
        quality_score = result.get('quality_score', 0)
        analysis = result.get('analysis', {})
        
        avg_likes = analysis.get('avg_likes', 0)
        avg_retweets = analysis.get('avg_retweets', 0)
        key_topics = analysis.get('key_topics', [])
        topics_str = ', '.join([t[0] for t in key_topics[:3]])
        
        status_emoji = {
            'high_quality': '🟢',
            'medium_quality': '🟡',
            'low_quality': '🔴',
            'error': '⚫'
        }.get(status, '❓')
        
        report += f"| @{account} | {status_emoji} {status} | {quality_score:.2f} | {avg_likes:.1f} | {avg_retweets:.1f} | {topics_str} |\n"
    
    report += f"""
---

## 推荐操作

### 高质量账号（建议提升优先级）

"""
    
    high_quality = [r for r in results if r.get('status') == 'high_quality']
    if high_quality:
        for result in high_quality:
            account = result.get('account', '')
            report += f"- **@{account}**: 内容质量高，建议提升优先级\n"
    else:
        report += "- 暂无\n"
    
    report += f"""
### 低质量账号（建议降低优先级或移除）

"""
    
    low_quality = [r for r in results if r.get('status') == 'low_quality']
    if low_quality:
        for result in low_quality:
            account = result.get('account', '')
            report += f"- **@{account}**: 内容质量低，建议降低优先级或移除\n"
    else:
        report += "- 暂无\n"
    
    report += f"""
---

*本报告由智能抓取调度系统自动生成*
"""
    
    # 保存报告
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write(report)
    
    print(f"✅ 验证报告生成完成: {report_path}")


def main():
    """主函数"""
    print("=========================================")
    print("中文大佬验证")
    print("=========================================")
    print()
    
    # 加载账号画像
    with open(PROFILES_PATH, 'r', encoding='utf-8') as f:
        profiles = json.load(f)
    
    # 获取待验证的中文大佬
    cn_influencers = []
    for account, profile in profiles.get('accounts', {}).items():
        if profile.get('category') == 'cn_influencer' and profile.get('status') == 'pending':
            cn_influencers.append(account)
    
    # 每天验证 2-3 个
    import random
    selected = random.sample(cn_influencers, min(3, len(cn_influencers)))
    
    print(f"验证账号: {selected}")
    print()
    
    # 验证每个账号
    results = []
    for account in selected:
        result = validate_cn_influencer(account)
        results.append(result)
        
        # 更新账号状态
        if result.get('status') != 'error':
            update_account_status(account, result['status'], result['quality_score'])
        
        print(f"  ✓ @{account}: {result.get('status', 'unknown')} (质量分数: {result.get('quality_score', 0):.2f})")
    
    # 生成验证报告
    generate_validation_report(results)
    
    print()
    print("=========================================")
    print("验证完成")
    print("=========================================")


if __name__ == "__main__":
    main()
