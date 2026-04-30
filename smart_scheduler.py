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

# 导入日志系统
from logger import logger, log_manager

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
        logger.info("初始化 SmartScheduler")
        self.config = self._load_config()
        self.profiles = self._load_profiles()
        self.current_hour = datetime.now().hour
        logger.debug(f"当前时间: {datetime.now()}, 当前小时: {self.current_hour}")
    
    def _load_config(self) -> Dict[str, Any]:
        """加载配置文件"""
        try:
            logger.debug(f"加载配置文件: {CONFIG_PATH}")
            with open(CONFIG_PATH, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)
                logger.info(f"配置加载成功，包含 {len(config)} 个配置项")
                return config
        except Exception as e:
            logger.error(f"加载配置文件失败: {e}")
            return {}
    
    def _load_profiles(self) -> Dict[str, Any]:
        """加载账号画像"""
        try:
            logger.debug(f"加载账号画像: {PROFILES_PATH}")
            with open(PROFILES_PATH, 'r', encoding='utf-8') as f:
                data = json.load(f)
                accounts = data.get('accounts', {})
                logger.info(f"账号画像加载成功，共 {len(accounts)} 个账号")
                return accounts
        except Exception as e:
            logger.error(f"加载账号画像失败: {e}")
            return {}
    
    def _save_profiles(self):
        """保存账号画像"""
        try:
            logger.debug(f"保存账号画像: {PROFILES_PATH}")
            data = {
                "version": "1.0",
                "last_updated": datetime.now().isoformat(),
                "accounts": self.profiles
            }
            with open(PROFILES_PATH, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            logger.info(f"账号画像保存成功，共 {len(self.profiles)} 个账号")
        except Exception as e:
            logger.error(f"保存账号画像失败: {e}")
    
    def _log_fetch(self, accounts: List[str], fetch_type: str, 
                   success_count: int, error_count: int, notes: str = ""):
        """记录抓取日志"""
        try:
            today = datetime.now().strftime("%Y-%m-%d")
            log_file = LOG_DIR / f"{today}.json"
            
            logger.debug(f"记录抓取日志: {log_file}")
            
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
                "logs": logs
            }
            with open(log_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            logger.info(f"抓取日志记录成功: {fetch_type}, 成功 {success_count}, 失败 {error_count}")
            
        except Exception as e:
            logger.error(f"记录抓取日志失败: {e}")
    
    def should_execute_now(self) -> bool:
        """根据学习结果决定是否现在执行"""
        try:
            logger.debug("检查是否应该现在执行")
            
            # 查询当前时段的活跃账号数量
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT COUNT(*) FROM active_hours_stats 
                WHERE hour = ? AND avg_active_count > 0
            """, (self.current_hour,))
            
            result = cursor.fetchone()
            active_count = result[0] if result else 0
            conn.close()
            
            logger.debug(f"当前时段 ({self.current_hour}:00) 活跃账号数: {active_count}")
            
            # 如果有 3 个以上账号在这个时段活跃，执行抓取
            should_execute = active_count >= 3
            logger.info(f"执行决策: {'执行' if should_execute else '跳过'} (活跃账号: {active_count})")
            
            return should_execute
            
        except Exception as e:
            logger.error(f"检查活跃时段失败: {e}")
            return True  # 默认执行
    
    def get_adaptive_count(self) -> int:
        """根据学习结果决定抓取数量"""
        try:
            logger.debug("获取自适应抓取数量")
            
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            
            # 查询当前时段的平均抓取数量
            cursor.execute("""
                SELECT avg_fetch_count FROM active_hours_stats 
                WHERE hour = ?
            """, (self.current_hour,))
            
            result = cursor.fetchone()
            conn.close()
            
            if result and result[0] > 0:
                count = int(result[0])
                logger.debug(f"根据历史数据，抓取数量: {count}")
                return count
            else:
                # 默认数量
                default_count = 5
                logger.debug(f"使用默认抓取数量: {default_count}")
                return default_count
                
        except Exception as e:
            logger.error(f"获取自适应抓取数量失败: {e}")
            return 5  # 默认数量
    
    def get_adaptive_interval(self) -> int:
        """根据学习结果决定抓取间隔"""
        try:
            logger.debug("获取自适应抓取间隔")
            
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            
            # 查询当前时段的平均间隔
            cursor.execute("""
                SELECT avg_interval_minutes FROM active_hours_stats 
                WHERE hour = ?
            """, (self.current_hour,))
            
            result = cursor.fetchone()
            conn.close()
            
            if result and result[0] > 0:
                interval = int(result[0])
                logger.debug(f"根据历史数据，抓取间隔: {interval} 分钟")
                return interval
            else:
                # 默认间隔
                default_interval = 60
                logger.debug(f"使用默认抓取间隔: {default_interval} 分钟")
                return default_interval
                
        except Exception as e:
            logger.error(f"获取自适应抓取间隔失败: {e}")
            return 60  # 默认间隔
    
    def fetch_account(self, handle: str, with_replies: bool = False) -> bool:
        """抓取单个账号"""
        try:
            logger.info(f"开始抓取账号: {handle}")
            
            # 构建命令
            cmd = ["autocli", "twitter", "search", f"from:{handle}"]
            if with_replies:
                cmd.append("--with-replies")
            
            logger.debug(f"执行命令: {' '.join(cmd)}")
            
            # 执行抓取
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=60
            )
            
            if result.returncode == 0:
                logger.info(f"账号 {handle} 抓取成功")
                
                # 保存内容
                self._save_content(handle, result.stdout)
                
                return True
            else:
                logger.error(f"账号 {handle} 抓取失败: {result.stderr}")
                return False
                
        except subprocess.TimeoutExpired:
            logger.error(f"账号 {handle} 抓取超时")
            return False
        except Exception as e:
            logger.error(f"账号 {handle} 抓取异常: {e}")
            return False
    
    def _save_content(self, handle: str, content: str):
        """保存抓取内容"""
        try:
            today = datetime.now().strftime("%Y-%m-%d")
            content_dir = INPUT_DIR / "x-收藏" / handle
            content_dir.mkdir(parents=True, exist_ok=True)
            
            content_file = content_dir / f"{today}.md"
            
            logger.debug(f"保存内容到: {content_file}")
            
            with open(content_file, 'w', encoding='utf-8') as f:
                f.write(f"# {handle} - {today}\n\n")
                f.write(content)
            
            logger.info(f"内容保存成功: {content_file}")
            
        except Exception as e:
            logger.error(f"保存内容失败: {e}")
    
    def run_adaptive(self, with_replies: bool = False):
        """运行自适应模式"""
        logger.info("=== 开始自适应模式抓取 ===")
        
        # 检查是否应该执行
        if not self.should_execute_now():
            logger.info("当前时段不适合抓取，跳过")
            return
        
        # 获取自适应参数
        count = self.get_adaptive_count()
        interval = self.get_adaptive_interval()
        
        logger.info(f"自适应参数: 抓取数量={count}, 间隔={interval}分钟")
        
        # 选择账号
        accounts = self._select_accounts(count)
        
        if not accounts:
            logger.warning("没有可抓取的账号")
            return
        
        logger.info(f"选中账号: {', '.join(accounts)}")
        
        # 执行抓取
        success_count = 0
        error_count = 0
        
        for i, account in enumerate(accounts):
            logger.info(f"抓取进度: {i+1}/{len(accounts)} - {account}")
            
            if self.fetch_account(account, with_replies):
                success_count += 1
            else:
                error_count += 1
            
            # 随机间隔
            if i < len(accounts) - 1:
                delay = random.randint(interval // 2, interval * 2)
                logger.debug(f"等待 {delay} 秒后继续")
                import time
                time.sleep(delay)
        
        # 记录日志
        self._log_fetch(
            accounts,
            "adaptive",
            success_count,
            error_count,
            f"自适应模式，抓取 {count} 个账号"
        )
        
        logger.info(f"=== 自适应模式完成: 成功 {success_count}, 失败 {error_count} ===")
    
    def _select_accounts(self, count: int) -> List[str]:
        """选择要抓取的账号"""
        logger.debug(f"选择 {count} 个账号")
        
        # 按优先级排序
        sorted_accounts = sorted(
            self.profiles.items(),
            key=lambda x: x[1].get('priority', 'medium'),
            reverse=True
        )
        
        # 选择前 N 个
        selected = [handle for handle, _ in sorted_accounts[:count]]
        
        logger.debug(f"选中账号: {selected}")
        return selected
    
    def run_scheduled(self, with_replies: bool = False):
        """运行定时模式"""
        logger.info("=== 开始定时模式抓取 ===")
        
        # 选择账号
        count = self.config.get('scheduler', {}).get('max_accounts_per_run', 5)
        accounts = self._select_accounts(count)
        
        if not accounts:
            logger.warning("没有可抓取的账号")
            return
        
        logger.info(f"选中账号: {', '.join(accounts)}")
        
        # 执行抓取
        success_count = 0
        error_count = 0
        
        for i, account in enumerate(accounts):
            logger.info(f"抓取进度: {i+1}/{len(accounts)} - {account}")
            
            if self.fetch_account(account, with_replies):
                success_count += 1
            else:
                error_count += 1
            
            # 随机间隔
            if i < len(accounts) - 1:
                interval = self.config.get('scheduler', {}).get('default_interval_minutes', 60)
                delay = random.randint(interval // 2, interval * 2)
                logger.debug(f"等待 {delay} 秒后继续")
                import time
                time.sleep(delay)
        
        # 记录日志
        self._log_fetch(
            accounts,
            "scheduled",
            success_count,
            error_count,
            f"定时模式，抓取 {count} 个账号"
        )
        
        logger.info(f"=== 定时模式完成: 成功 {success_count}, 失败 {error_count} ===")
    
    def show_profiles(self):
        """显示账号画像"""
        logger.info("=== 账号画像 ===")
        
        for handle, profile in sorted(self.profiles.items()):
            name = profile.get('name', handle)
            category = profile.get('category', '未分类')
            priority = profile.get('priority', 'medium')
            status = profile.get('status', 'active')
            
            logger.info(f"{handle}: {name} [{category}] 优先级={priority} 状态={status}")
    
    def update_profiles(self):
        """更新账号画像"""
        logger.info("=== 更新账号画像 ===")
        
        updated = 0
        for handle in self.profiles:
            try:
                # 获取最新信息
                result = subprocess.run(
                    ["autocli", "twitter", "profile", handle, "--format", "json"],
                    capture_output=True,
                    text=True,
                    timeout=30
                )
                
                if result.returncode == 0:
                    profile_data = json.loads(result.stdout)
                    
                    # 更新画像
                    self.profiles[handle].update({
                        'name': profile_data.get('name', self.profiles[handle].get('name')),
                        'followers': profile_data.get('followers_count'),
                        'following': profile_data.get('following_count'),
                        'last_updated': datetime.now().isoformat()
                    })
                    
                    updated += 1
                    logger.debug(f"更新账号 {handle} 成功")
                else:
                    logger.warning(f"获取账号 {handle} 信息失败")
                    
            except Exception as e:
                logger.error(f"更新账号 {handle} 失败: {e}")
        
        # 保存更新
        self._save_profiles()
        
        logger.info(f"=== 账号画像更新完成: 更新 {updated} 个账号 ===")


def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Smart Scheduler - 智能抓取调度系统')
    parser.add_argument('--type', choices=['scheduled', 'adaptive', 'manual'], 
                       default='scheduled', help='抓取类型')
    parser.add_argument('--accounts', help='指定账号，逗号分隔')
    parser.add_argument('--show-profiles', action='store_true', help='显示账号画像')
    parser.add_argument('--update-profiles', action='store_true', help='更新账号画像')
    parser.add_argument('--analyze', action='store_true', help='分析账号内容')
    parser.add_argument('--compare', help='对比博主，逗号分隔')
    parser.add_argument('--with-replies', action='store_true', help='包含评论区内容')
    parser.add_argument('--adaptive', action='store_true', help='自适应模式')
    
    args = parser.parse_args()
    
    # 初始化调度器
    scheduler = SmartScheduler()
    
    # 执行相应操作
    if args.show_profiles:
        scheduler.show_profiles()
    elif args.update_profiles:
        scheduler.update_profiles()
    elif args.adaptive:
        scheduler.run_adaptive(args.with_replies)
    elif args.type == 'adaptive':
        scheduler.run_adaptive(args.with_replies)
    elif args.type == 'scheduled':
        scheduler.run_scheduled(args.with_replies)
    else:
        scheduler.run_scheduled(args.with_replies)


if __name__ == "__main__":
    main()
