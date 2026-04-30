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
    python3 smart_scheduler.py --adaptive         # 自适应模式（根据学习结果决策）
    python3 smart_scheduler.py --data-dir /path   # 自定义数据目录
    python3 smart_scheduler.py --show-paths       # 显示路径配置
"""

import json
import yaml
import random
import subprocess
import sys
import os
import sqlite3
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Any, Optional

# 导入路径配置
from paths import get_paths, print_paths

# 导入日志系统
from logger import logger, log_manager


class SmartScheduler:
    """智能抓取调度器"""
    
    def __init__(self, data_dir: str = None):
        # 获取路径配置
        self.paths = get_paths(data_dir)
        
        logger.info("初始化 SmartScheduler")
        logger.info(f"数据目录: {self.paths['data_dir']}")
        
        self.config = self._load_config()
        self.profiles = self._load_profiles()
        self.current_hour = datetime.now().hour
        self._init_db()
        logger.debug(f"当前时间: {datetime.now()}, 当前小时: {self.current_hour}")
    
    def _init_db(self):
        """初始化学习数据库表结构"""
        try:
            conn = sqlite3.connect(self.paths['db_file'])
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS active_hours_stats (
                    hour INTEGER PRIMARY KEY,
                    avg_active_count REAL DEFAULT 0,
                    avg_fetch_count REAL DEFAULT 0,
                    avg_interval_minutes REAL DEFAULT 0,
                    total_fetches INTEGER DEFAULT 0,
                    successful_fetches INTEGER DEFAULT 0,
                    last_updated TEXT
                )
            """)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS fetch_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    handle TEXT,
                    fetch_time TEXT,
                    hour INTEGER,
                    success INTEGER,
                    tweet_count INTEGER DEFAULT 0,
                    error_message TEXT
                )
            """)
            conn.commit()
            conn.close()
            logger.debug("数据库表初始化完成")
        except Exception as e:
            logger.error(f"数据库初始化失败: {e}")
    
    def _load_config(self) -> Dict[str, Any]:
        """加载配置文件"""
        try:
            config_file = self.paths['config_file']
            logger.debug(f"加载配置文件: {config_file}")
            
            if not config_file.exists():
                logger.warning(f"配置文件不存在: {config_file}")
                return {}
            
            with open(config_file, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)
                logger.info(f"配置加载成功，包含 {len(config)} 个配置项")
                return config
        except Exception as e:
            logger.error(f"加载配置文件失败: {e}")
            return {}
    
    def _load_profiles(self) -> Dict[str, Any]:
        """加载账号画像"""
        try:
            profiles_file = self.paths['profiles_file']
            logger.debug(f"加载账号画像: {profiles_file}")
            
            if not profiles_file.exists():
                logger.warning(f"账号画像文件不存在: {profiles_file}")
                return {}
            
            with open(profiles_file, 'r', encoding='utf-8') as f:
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
            profiles_file = self.paths['profiles_file']
            logger.debug(f"保存账号画像: {profiles_file}")
            
            data = {
                "version": "1.0",
                "last_updated": datetime.now().isoformat(),
                "accounts": self.profiles
            }
            with open(profiles_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            logger.info(f"账号画像保存成功，共 {len(self.profiles)} 个账号")
        except Exception as e:
            logger.error(f"保存账号画像失败: {e}")
    
    def _log_fetch(self, accounts: List[str], fetch_type: str, 
                   success_count: int, error_count: int, 
                   total_duration: float = 0, notes: str = ""):
        """记录抓取日志"""
        try:
            today = datetime.now().strftime("%Y-%m-%d")
            log_file = self.paths['fetch_log_dir'] / f"{today}.json"
            
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
                "duration_seconds": total_duration,
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
            
            logger.info(f"抓取日志记录成功: {fetch_type}, 成功 {success_count}, 失败 {error_count}, 耗时 {total_duration}s")
            
        except Exception as e:
            logger.error(f"记录抓取日志失败: {e}")
    
    def _record_fetch_to_db(self, handle: str, success: bool):
        """记录抓取结果到学习数据库"""
        try:
            conn = sqlite3.connect(self.paths['db_file'])
            cursor = conn.cursor()
            
            now = datetime.now()
            hour = now.hour
            
            # 记录到 fetch_history（字段与表结构匹配）
            cursor.execute("""
                INSERT INTO fetch_history (account, fetch_time, has_new_content, tweets_count)
                VALUES (?, ?, ?, ?)
            """, (handle, now.isoformat(), 1 if success else 0, 20 if success else 0))
            
            # 更新 active_hours_stats（UPSERT，字段与表结构匹配）
            cursor.execute("""
                INSERT INTO active_hours_stats (account, hour, fetch_count, new_content_count, probability, updated_at)
                VALUES (?, ?, 1, ?, ?, ?)
                ON CONFLICT(account, hour) DO UPDATE SET
                    fetch_count = fetch_count + 1,
                    new_content_count = new_content_count + ?,
                    probability = CAST(new_content_count + ? AS FLOAT) / (fetch_count + 1),
                    updated_at = ?
            """, (handle, hour, 1 if success else 0, 1.0 if success else 0.0, now.isoformat(),
                  1 if success else 0, 1 if success else 0, now.isoformat()))
            
            conn.commit()
            conn.close()
            logger.debug(f"学习数据记录: {handle} hour={hour} success={success}")
        except Exception as e:
            logger.error(f"记录学习数据失败: {e}")
    
    def should_execute_now(self) -> bool:
        """根据学习结果决定是否现在执行"""
        try:
            logger.debug("检查是否应该现在执行")
            
            conn = sqlite3.connect(self.paths['db_file'])
            cursor = conn.cursor()
            
            # 查询当前时段有数据的账号数量（按账号去重）
            cursor.execute("""
                SELECT COUNT(DISTINCT account) FROM active_hours_stats 
                WHERE hour = ? AND fetch_count > 0
            """, (self.current_hour,))
            
            result = cursor.fetchone()
            active_count = result[0] if result else 0
            
            logger.debug(f"当前时段 ({self.current_hour}:00) 活跃账号数: {active_count}")
            
            # 检查总数据量，数据不足时进入 bootstrap 模式（始终执行）
            try:
                cursor.execute("SELECT COUNT(*) FROM active_hours_stats")
                total_rows = cursor.fetchone()[0]
            except sqlite3.Error as e:
                logger.warning(f"查询数据量失败: {e}")
                total_rows = 0
            
            conn.close()
            
            if total_rows < 20:
                logger.info(f"Bootstrap 模式（数据量 {total_rows} < 20），始终执行")
                return True
            
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
            
            conn = sqlite3.connect(self.paths['db_file'])
            cursor = conn.cursor()
            
            # 查询当前时段有数据的账号总数作为抓取数量参考
            cursor.execute("""
                SELECT COUNT(DISTINCT account) FROM active_hours_stats 
                WHERE hour = ? AND fetch_count > 0
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
            
            conn = sqlite3.connect(self.paths['db_file'])
            cursor = conn.cursor()
            
            # 查询当前时段的平均抓取概率作为间隔参考（概率越高，间隔越短）
            cursor.execute("""
                SELECT AVG(probability) FROM active_hours_stats 
                WHERE hour = ? AND fetch_count > 0
            """, (self.current_hour,))
            
            result = cursor.fetchone()
            conn.close()
            
            if result and result[0] and result[0] > 0:
                # 概率高 → 间隔短，概率低 → 间隔长
                probability = result[0]
                interval = max(15, int(60 * (1 - probability)))
                logger.debug(f"根据历史概率 {probability:.2f}，抓取间隔: {interval} 分钟")
                return interval
            else:
                # 默认间隔
                default_interval = 60
                logger.debug(f"使用默认抓取间隔: {default_interval} 分钟")
                return default_interval
                
        except Exception as e:
            logger.error(f"获取自适应抓取间隔失败: {e}")
            return 60  # 默认间隔
    
    def fetch_account(self, handle: str) -> tuple[bool, float]:
        """抓取单个账号，返回 (成功与否, 耗时秒数)"""
        start_time = time.time()
        try:
            logger.info(f"开始抓取账号: {handle}")
            
            # 构建命令
            cmd = ["autocli", "twitter", "search", f"from:{handle}", "--format", "json", "--limit", "20"]
            
            logger.debug(f"执行命令: {' '.join(cmd)}")
            
            # 执行抓取
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=60
            )
            
            duration = round(time.time() - start_time, 2)
            
            if result.returncode == 0:
                logger.info(f"账号 {handle} 抓取成功 (耗时 {duration}s)")
                
                # 保存内容
                self._save_content(handle, result.stdout)
                
                return True, duration
            else:
                logger.error(f"账号 {handle} 抓取失败 (耗时 {duration}s): {result.stderr}")
                return False, duration
                
        except subprocess.TimeoutExpired:
            duration = round(time.time() - start_time, 2)
            logger.error(f"账号 {handle} 抓取超时 (耗时 {duration}s)")
            return False, duration
        except Exception as e:
            duration = round(time.time() - start_time, 2)
            logger.error(f"账号 {handle} 抓取异常 (耗时 {duration}s): {e}")
            return False, duration
    
    def _save_content(self, handle: str, content: str):
        """保存抓取内容"""
        try:
            today = datetime.now().strftime("%Y-%m-%d")
            content_dir = self.paths['content_dir'] / "x-收藏" / handle
            content_dir.mkdir(parents=True, exist_ok=True)
            
            content_file = content_dir / f"{today}.md"
            
            logger.debug(f"保存内容到: {content_file}")
            
            with open(content_file, 'w', encoding='utf-8') as f:
                f.write(f"# {handle} - {today}\n\n")
                f.write(content)
            
            logger.info(f"内容保存成功: {content_file}")
            
        except Exception as e:
            logger.error(f"保存内容失败: {e}")
    
    def run_adaptive(self):
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
        total_duration = 0
        
        for i, account in enumerate(accounts):
            logger.info(f"抓取进度: {i+1}/{len(accounts)} - {account}")
            
            success, duration = self.fetch_account(account)
            total_duration += duration
            
            # 记录到学习数据库
            self._record_fetch_to_db(account, success)
            
            if success:
                success_count += 1
            else:
                error_count += 1
            
            # 随机间隔（interval 单位是分钟，转换为秒）
            if i < len(accounts) - 1:
                delay_seconds = random.randint(interval // 2, interval * 2)  # 0.5x 到 2x 分钟，转换为秒
                logger.debug(f"等待 {delay_seconds} 秒后继续")
                time.sleep(delay_seconds)
        
        # 记录日志
        self._log_fetch(
            accounts,
            "adaptive",
            success_count,
            error_count,
            total_duration,
            f"自适应模式，抓取 {count} 个账号"
        )
        
        logger.info(f"=== 自适应模式完成: 成功 {success_count}, 失败 {error_count}, 耗时 {total_duration}s ===")
    
    def _select_accounts(self, count: int) -> List[str]:
        """选择要抓取的账号"""
        logger.debug(f"选择 {count} 个账号")
        
        # 优先级映射为数值
        priority_map = {'high': 3, 'medium': 2, 'low': 1}
        
        # 按优先级排序（数值排序，不是字符串排序）
        sorted_accounts = sorted(
            self.profiles.items(),
            key=lambda x: priority_map.get(x[1].get('priority', 'medium'), 2),
            reverse=True
        )
        
        # 选择前 N 个
        selected = [handle for handle, _ in sorted_accounts[:count]]
        
        logger.debug(f"选中账号: {selected}")
        return selected
    
    def run_scheduled(self):
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
        total_duration = 0
        
        for i, account in enumerate(accounts):
            logger.info(f"抓取进度: {i+1}/{len(accounts)} - {account}")
            
            success, duration = self.fetch_account(account)
            total_duration += duration
            
            if success:
                success_count += 1
            else:
                error_count += 1
            
            # 随机间隔（interval 单位是分钟，转换为秒）
            if i < len(accounts) - 1:
                interval = self.config.get('scheduler', {}).get('default_interval_minutes', 60)
                delay_seconds = random.randint(interval // 2, interval * 2)  # 0.5x 到 2x 分钟，转换为秒
                logger.debug(f"等待 {delay_seconds} 秒后继续")
                time.sleep(delay_seconds)
        
        # 记录日志
        self._log_fetch(
            accounts,
            "scheduled",
            success_count,
            error_count,
            total_duration,
            f"定时模式，抓取 {count} 个账号"
        )
        
        logger.info(f"=== 定时模式完成: 成功 {success_count}, 失败 {error_count}, 耗时 {total_duration}s ===")
    
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
    parser.add_argument('--with-replies', action='store_true', help='包含评论区内容（暂不支持）')
    parser.add_argument('--adaptive', action='store_true', help='自适应模式')
    parser.add_argument('--data-dir', help='自定义数据目录')
    parser.add_argument('--show-paths', action='store_true', help='显示路径配置')
    
    args = parser.parse_args()
    
    # 显示路径配置
    if args.show_paths:
        print_paths(args.data_dir)
        return
    
    # 记录启动日志
    logger.info("=" * 50)
    logger.info("Smart Scheduler 启动")
    logger.info(f"参数: type={args.type}, adaptive={args.adaptive}")
    if args.accounts:
        logger.info(f"指定账号: {args.accounts}")
    if args.data_dir:
        logger.info(f"自定义数据目录: {args.data_dir}")
    logger.info("=" * 50)
    
    # 初始化调度器
    scheduler = SmartScheduler(data_dir=args.data_dir)
    
    # 执行相应操作
    try:
        if args.show_profiles:
            scheduler.show_profiles()
        elif args.update_profiles:
            scheduler.update_profiles()
        elif args.adaptive:
            scheduler.run_adaptive()
        elif args.type == 'adaptive':
            scheduler.run_adaptive()
        elif args.type == 'scheduled':
            scheduler.run_scheduled()
        else:
            scheduler.run_scheduled()
        
        logger.info("Smart Scheduler 正常退出")
        
    except KeyboardInterrupt:
        logger.warning("用户中断执行")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Smart Scheduler 异常退出: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
