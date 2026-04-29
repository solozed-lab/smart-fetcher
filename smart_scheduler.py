#!/usr/bin/env python3
"""
Smart Scheduler — 智能抓取调度系统
根据账号习惯动态调整抓取时间，像真人一样刷推特

用法:
    python3 smart_scheduler.py                    # 执行一次智能抓取
    python3 smart_scheduler.py --type scheduled   # 指定抓取类型
    python3 smart_scheduler.py --accounts karpathy,AndrewYNg  # 指定账号
    python3 smart_scheduler.py --show-profiles    # 查看账号画像
    python3 smart_scheduler.py --update-profiles  # 更新账号画像
    python3 smart_scheduler.py --analyze          # 分析账号内容
    python3 smart_scheduler.py --compare karpathy,AndrewYNg  # 对比博主
    python3 smart_scheduler.py --with-replies     # 包含评论区内容
    python3 smart_scheduler.py --adaptive         # 自适应模式（根据学习结果决策）
"""

import json
import yaml
import random
import subprocess
import sys
import os
import sqlite3
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Any, Optional

# 路径配置
BASE_DIR = Path(__file__).parent.parent.parent
INPUT_DIR = BASE_DIR / "input"
LEARN_DIR = INPUT_DIR / "learn"
CONFIG_PATH = LEARN_DIR / "config.yaml"
PROFILES_PATH = LEARN_DIR / "account-profiles.json"
DB_PATH = LEARN_DIR / "learning.db"
LOG_DIR = LEARN_DIR / "fetch-logs"


class SmartScheduler:
    """智能抓取调度器"""
    
    def __init__(self):
        self.config = self._load_config()
        self.profiles = self._load_profiles()
        self.current_hour = datetime.now().hour
    
    def _load_config(self) -> Dict[str, Any]:
        """加载配置文件"""
        try:
            with open(CONFIG_PATH, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f)
        except Exception as e:
            print(f"Error loading config: {e}")
            return {}
    
    def _load_profiles(self) -> Dict[str, Any]:
        """加载账号画像"""
        try:
            with open(PROFILES_PATH, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return data.get('accounts', {})
        except Exception as e:
            print(f"Error loading profiles: {e}")
            return {}
    
    def _save_profiles(self):
        """保存账号画像"""
        try:
            data = {
                "version": "1.0",
                "last_updated": datetime.now().isoformat(),
                "accounts": self.profiles
            }
            with open(PROFILES_PATH, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Error saving profiles: {e}")
    
    def _log_fetch(self, accounts: List[str], fetch_type: str, 
                   success_count: int, error_count: int, notes: str = ""):
        """记录抓取日志"""
        try:
            # 生成日志文件名（按日期）
            today = datetime.now().strftime("%Y-%m-%d")
            log_file = LOG_DIR / f"{today}.json"
            
            # 确保目录存在
            log_file.parent.mkdir(parents=True, exist_ok=True)
            
            # 读取现有日志
            logs = []
            if log_file.exists():
                with open(log_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    logs = data.get('logs', [])
            
            # 添加新日志
            log_entry = {
                "timestamp": datetime.now().isoformat(),
                "accounts_fetched": accounts,
                "fetch_type": fetch_type,
                "duration_seconds": 0,  # TODO: 记录实际耗时
                "success_count": success_count,
                "error_count": error_count,
                "notes": notes
            }
            logs.append(log_entry)
            
            # 保存日志
            data = {
                "version": "1.0",
                "date": today,
                "logs": logs
            }
            with open(log_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Error logging fetch: {e}")
    
    def should_execute_now(self) -> bool:
        """根据学习结果决定是否现在执行"""
        
        # 查询学习结果：这个时段有多少账号活跃？
        try:
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT COUNT(*) as active_count
                FROM active_hours_stats
                WHERE hour = ? AND probability > 0.5
            ''', (self.current_hour,))
            
            result = cursor.fetchone()
            active_count = result[0] if result else 0
            
            conn.close()
            
            # 如果有 3 个以上账号在这个时段活跃，执行抓取
            return active_count >= 3
        except Exception as e:
            print(f"Error checking active hours: {e}")
            return True  # 默认执行
    
    def get_adaptive_count(self) -> int:
        """根据学习结果动态调整抓取数量"""
        
        # 查询最近 24 小时的抓取结果
        try:
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT AVG(tweets_count) as avg_tweets
                FROM fetch_history
                WHERE fetch_time >= datetime('now', '-24 hours')
            ''')
            
            result = cursor.fetchone()
            avg_tweets = result[0] if result and result[0] else 5
            
            conn.close()
            
            # 根据平均推文数量调整抓取数量
            if avg_tweets > 20:  # 内容很多
                return 3  # 减少抓取数量
            elif avg_tweets < 5:  # 内容很少
                return 8  # 增加抓取数量
            else:
                return 5  # 默认数量
        except Exception as e:
            print(f"Error getting adaptive count: {e}")
            return 5  # 默认数量
    
    def get_adaptive_interval(self) -> int:
        """根据学习结果动态调整抓取间隔（分钟）"""
        
        # 查询最近抓取的成功率
        try:
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT 
                    COUNT(*) as total,
                    SUM(CASE WHEN has_new_content = 1 THEN 1 ELSE 0 END) as has_new
                FROM fetch_history
                WHERE fetch_time >= datetime('now', '-24 hours')
            ''')
            
            result = cursor.fetchone()
            total = result[0] if result else 0
            has_new = result[1] if result else 0
            
            conn.close()
            
            # 根据成功率调整间隔
            if total == 0:
                return 60  # 默认 60 分钟
            
            success_rate = has_new / total
            
            if success_rate > 0.7:  # 成功率高
                return 30  # 缩短间隔
            elif success_rate < 0.3:  # 成功率低
                return 120  # 延长间隔
            else:
                return 60  # 默认间隔
        except Exception as e:
            print(f"Error getting adaptive interval: {e}")
            return 60  # 默认间隔
    
    def calculate_account_priority(self, account: str) -> float:
        """计算账号的抓取优先级"""
        profile = self.profiles.get(account, {})
        if not profile:
            return 0.0
        
        # 基础优先级权重
        priority = profile.get('priority', 1)
        priority_weight = self.config.get('scheduler', {}).get('priority_weights', {}).get(priority, 0.5)
        
        # 更新频率权重
        frequency = profile.get('frequency', 'medium')
        frequency_weights = {'high': 1.0, 'medium': 0.7, 'low': 0.4, 'occasional': 0.2}
        frequency_weight = frequency_weights.get(frequency, 0.5)
        
        # 最后更新时间权重（越久未更新，权重越高）
        last_updated = profile.get('last_updated', '')
        if last_updated:
            try:
                last_update_time = datetime.fromisoformat(last_updated)
                hours_since_update = (datetime.now() - last_update_time).total_seconds() / 3600
                # 超过 24 小时未更新，权重增加
                time_weight = min(1.0, hours_since_update / 24)
            except:
                time_weight = 0.5
        else:
            time_weight = 0.5
        
        # 活跃时段权重
        active_hours = profile.get('active_hours', [])
        if self.current_hour in active_hours:
            active_weight = 1.0
        else:
            active_weight = 0.3
        
        # 综合优先级
        total_priority = (
            priority_weight * 0.4 +
            frequency_weight * 0.3 +
            time_weight * 0.2 +
            active_weight * 0.1
        )
        
        return total_priority
    
    def select_accounts(self, count: int = 5, 
                       category: Optional[str] = None) -> List[str]:
        """选择要抓取的账号"""
        # 筛选账号
        candidates = []
        for account, profile in self.profiles.items():
            # 分类筛选
            if category and profile.get('category') != category:
                continue
            
            # 状态筛选
            if profile.get('status') not in ['active', 'pending']:
                continue
            
            candidates.append(account)
        
        # 计算优先级
        account_priorities = []
        for account in candidates:
            priority = self.calculate_account_priority(account)
            account_priorities.append((account, priority))
        
        # 按优先级排序
        account_priorities.sort(key=lambda x: x[1], reverse=True)
        
        # 选择 top N
        selected = [account for account, _ in account_priorities[:count]]
        
        return selected
    
    def fetch_account(self, account: str, with_replies: bool = False) -> Dict[str, Any]:
        """抓取单个账号"""
        result = {
            "account": account,
            "success": False,
            "tweets": [],
            "replies": [],
            "error": None
        }
        
        try:
            # 使用 autocli 抓取推文
            cmd = f'autocli twitter profile {account} --format json'
            profile_result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=15)
            
            if profile_result.returncode == 0:
                profile_data = json.loads(profile_result.stdout)
                if profile_data and len(profile_data) > 0:
                    result["profile"] = profile_data[0]
            
            # 抓取最近推文（使用 search 命令）
            cmd = f'autocli twitter search "from:{account}" --limit 5 --format json'
            tweets_result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=15)
            
            if tweets_result.returncode == 0:
                tweets_data = json.loads(tweets_result.stdout)
                result["tweets"] = tweets_data
            
            # 抓取评论区内容（如果启用）
            if with_replies:
                # 只抓取前 1 条推文的评论，取前 10 条评论
                # 评论区抓取比较慢，减少数量避免超时
                if result["tweets"]:
                    tweet = result["tweets"][0]
                    tweet_url = tweet.get("url", "")
                    if tweet_url:
                        # 从 URL 中提取 tweet_id
                        tweet_id = tweet_url.split("/")[-1]
                        replies = self.fetch_replies(tweet_id, limit=10)
                        if replies:
                            result["replies"].extend(replies)
            
            result["success"] = True
            
            # 更新画像中的最后更新时间
            if account in self.profiles:
                self.profiles[account]['last_updated'] = datetime.now().isoformat()
            
        except Exception as e:
            result["error"] = str(e)
            print(f"Error fetching {account}: {e}")
        
        return result
    
    def fetch_replies(self, tweet_id: str, limit: int = 15) -> List[Dict[str, Any]]:
        """抓取推文的评论区（默认前 15 条有代表性的评论）"""
        replies = []
        try:
            # 使用 autocli 抓取推文详情（包含评论）
            # thread 命令比较慢，增加超时时间到 30 秒
            cmd = f'autocli twitter thread {tweet_id} --format json'
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0:
                data = json.loads(result.stdout)
                if data and len(data) > 0:
                    # 第一条是原推文，后面的是评论
                    all_replies = data[1:] if len(data) > 1 else []
                    
                    # 按互动数据排序，取前 N 条有代表性的
                    # 排序逻辑：likes + retweets * 2（转发权重更高）
                    for reply in all_replies:
                        reply['_score'] = reply.get('likes', 0) + reply.get('retweets', 0) * 2
                    
                    sorted_replies = sorted(all_replies, key=lambda x: x.get('_score', 0), reverse=True)
                    replies = sorted_replies[:limit]
                    
                    # 移除临时的 _score 字段
                    for reply in replies:
                        reply.pop('_score', None)
        except subprocess.TimeoutExpired:
            print(f"Timeout fetching replies for tweet {tweet_id}")
        except Exception as e:
            print(f"Error fetching replies for tweet {tweet_id}: {e}")
        
        return replies
    
    def run_adaptive_fetch(self, with_replies: bool = False):
        """执行自适应抓取"""
        print(f"[{datetime.now().isoformat()}] Starting adaptive fetch...")
        
        # 检查是否应该现在执行
        if not self.should_execute_now():
            print(f"跳过执行：当前时段（{self.current_hour}:00）活跃账号不足")
            return
        
        # 获取自适应抓取数量
        count = self.get_adaptive_count()
        print(f"自适应抓取数量: {count}")
        
        # 获取自适应抓取间隔
        interval = self.get_adaptive_interval()
        print(f"自适应抓取间隔: {interval} 分钟")
        
        # 选择账号
        accounts = self.select_accounts(count)
        print(f"Selected accounts: {accounts}")
        
        # 执行抓取
        success_count = 0
        error_count = 0
        results = []
        
        for account in accounts:
            print(f"Fetching {account}...")
            result = self.fetch_account(account, with_replies)
            results.append(result)
            
            if result["success"]:
                success_count += 1
                print(f"  ✓ Fetched {len(result['tweets'])} tweets, {len(result['replies'])} replies")
            else:
                error_count += 1
                print(f"  ✗ Error: {result['error']}")
            
            # 随机延迟（10-15分钟）
            delay = random.randint(600, 900)
            print(f"Waiting {delay} seconds before next fetch...")
            # 注意：实际执行时需要 sleep，这里只是演示
            # time.sleep(delay)
        
        # 记录日志
        self._log_fetch(accounts, "adaptive", success_count, error_count, 
                       f"interval={interval}min")
        
        # 保存画像
        self._save_profiles()
        
        # 保存抓取结果
        self._save_fetch_results(results)
        
        print(f"Fetch completed: {success_count} success, {error_count} errors")
        
        return results
    
    def run_scheduled_fetch(self, count: int = 5, with_replies: bool = False):
        """执行定时抓取"""
        print(f"[{datetime.now().isoformat()}] Starting scheduled fetch...")
        
        # 选择账号
        accounts = self.select_accounts(count)
        print(f"Selected accounts: {accounts}")
        
        # 执行抓取
        success_count = 0
        error_count = 0
        results = []
        
        for account in accounts:
            print(f"Fetching {account}...")
            result = self.fetch_account(account, with_replies)
            results.append(result)
            
            if result["success"]:
                success_count += 1
                print(f"  ✓ Fetched {len(result['tweets'])} tweets, {len(result['replies'])} replies")
            else:
                error_count += 1
                print(f"  ✗ Error: {result['error']}")
            
            # 随机延迟（10-15分钟）
            delay = random.randint(600, 900)
            print(f"Waiting {delay} seconds before next fetch...")
            # 注意：实际执行时需要 sleep，这里只是演示
            # time.sleep(delay)
        
        # 记录日志
        self._log_fetch(accounts, "scheduled", success_count, error_count, 
                       f"with_replies={with_replies}")
        
        # 保存画像
        self._save_profiles()
        
        # 保存抓取结果
        self._save_fetch_results(results)
        
        print(f"Fetch completed: {success_count} success, {error_count} errors")
        
        return results
    
    def run_manual_fetch(self, accounts: List[str], with_replies: bool = False):
        """执行手动抓取"""
        print(f"[{datetime.now().isoformat()}] Starting manual fetch...")
        print(f"Accounts: {accounts}")
        
        success_count = 0
        error_count = 0
        results = []
        
        for account in accounts:
            print(f"Fetching {account}...")
            result = self.fetch_account(account, with_replies)
            results.append(result)
            
            if result["success"]:
                success_count += 1
                print(f"  ✓ Fetched {len(result['tweets'])} tweets, {len(result['replies'])} replies")
            else:
                error_count += 1
                print(f"  ✗ Error: {result['error']}")
        
        # 记录日志
        self._log_fetch(accounts, "manual", success_count, error_count,
                       f"with_replies={with_replies}")
        
        # 保存画像
        self._save_profiles()
        
        # 保存抓取结果
        self._save_fetch_results(results)
        
        print(f"Fetch completed: {success_count} success, {error_count} errors")
        
        return results
    
    def _save_fetch_results(self, results: List[Dict[str, Any]]):
        """保存抓取结果"""
        try:
            # 生成文件名
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"fetch_results_{timestamp}.json"
            filepath = INPUT_DIR / "x-大佬" / filename
            
            # 确保目录存在
            filepath.parent.mkdir(parents=True, exist_ok=True)
            
            # 保存结果
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(results, f, indent=2, ensure_ascii=False)
            
            print(f"Results saved to: {filepath}")
        except Exception as e:
            print(f"Error saving results: {e}")
    
    def show_profiles(self):
        """显示账号画像"""
        print(f"\n{'='*60}")
        print("Account Profiles")
        print(f"{'='*60}\n")
        
        # 按分类分组
        categories = {}
        for account, profile in self.profiles.items():
            category = profile.get('category', 'unknown')
            if category not in categories:
                categories[category] = []
            categories[category].append((account, profile))
        
        # 显示每个分类
        for category, accounts in categories.items():
            print(f"\n[{category}]")
            print(f"{'Account':<20} {'Name':<25} {'Priority':<10} {'Frequency':<10} {'Last Updated':<20}")
            print("-" * 85)
            
            for account, profile in accounts:
                name = profile.get('name', 'Unknown')
                priority = profile.get('priority', 1)
                frequency = profile.get('frequency', 'medium')
                last_updated = profile.get('last_updated', 'Never')
                
                # 截断显示
                if len(name) > 24:
                    name = name[:21] + "..."
                if len(last_updated) > 19:
                    last_updated = last_updated[:16] + "..."
                
                print(f"@{account:<19} {name:<25} {'⭐' * priority:<10} {frequency:<10} {last_updated:<20}")
    
    def update_profiles(self):
        """更新账号画像（基于抓取结果）"""
        print(f"[{datetime.now().isoformat()}] Updating profiles...")
        
        # TODO: 实现自学习逻辑
        # 1. 分析抓取结果
        # 2. 更新频率
        # 3. 更新活跃时段
        # 4. 调整优先级
        
        self._save_profiles()
        print("Profiles updated.")

def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Smart Scheduler — 智能抓取调度系统')
    parser.add_argument('--type', choices=['scheduled', 'manual', 'cross_validation'],
                       default='scheduled', help='抓取类型')
    parser.add_argument('--accounts', type=str, help='指定账号（逗号分隔）')
    parser.add_argument('--count', type=int, default=5, help='抓取账号数量')
    parser.add_argument('--category', type=str, help='账号分类')
    parser.add_argument('--show-profiles', action='store_true', help='显示账号画像')
    parser.add_argument('--update-profiles', action='store_true', help='更新账号画像')
    parser.add_argument('--analyze', action='store_true', help='分析账号内容')
    parser.add_argument('--compare', type=str, help='对比博主（逗号分隔）')
    parser.add_argument('--with-replies', action='store_true', help='包含评论区内容')
    parser.add_argument('--adaptive', action='store_true', help='自适应模式（根据学习结果决策）')
    
    args = parser.parse_args()
    
    # 创建调度器
    scheduler = SmartScheduler()
    
    # 执行操作
    if args.show_profiles:
        scheduler.show_profiles()
    elif args.update_profiles:
        scheduler.update_profiles()
    elif args.analyze:
        if args.accounts:
            accounts = args.accounts.split(',')
            for account in accounts:
                print(f"\n{'='*60}")
                print(f"Analyzing @{account}...")
                print(f"{'='*60}")
                analysis = scheduler.analyze_account(account)
                print(json.dumps(analysis, indent=2, ensure_ascii=False))
        else:
            print("Error: --accounts required for analyze")
            sys.exit(1)
    elif args.compare:
        accounts = args.compare.split(',')
        print(f"\n{'='*60}")
        print(f"Comparing accounts: {', '.join(accounts)}")
        print(f"{'='*60}")
        comparison = scheduler.compare_accounts(accounts)
        print(json.dumps(comparison, indent=2, ensure_ascii=False))
    elif args.adaptive:
        scheduler.run_adaptive_fetch(args.with_replies)
    elif args.type == 'scheduled':
        scheduler.run_scheduled_fetch(args.count, args.with_replies)
    elif args.type == 'manual':
        if args.accounts:
            accounts = args.accounts.split(',')
            scheduler.run_manual_fetch(accounts, args.with_replies)
        else:
            print("Error: --accounts required for manual fetch")
            sys.exit(1)
    elif args.type == 'cross_validation':
        # TODO: 实现交叉验证
        print("Cross validation not implemented yet")

if __name__ == "__main__":
    main()
