#!/usr/bin/env python3
"""
Learning Database — 学习数据库初始化
创建 SQLite 数据库和表结构
"""

import sqlite3
import os
from pathlib import Path

# 数据库路径
DB_PATH = Path(__file__).parent.parent.parent / "input" / "learn" / "learning.db"

def create_database():
    """创建数据库和表结构"""
    
    # 确保目录存在
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    
    # 连接数据库
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # 创建抓取历史表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS fetch_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            account TEXT NOT NULL,
            fetch_time TIMESTAMP NOT NULL,
            has_new_content BOOLEAN,
            tweets_count INTEGER DEFAULT 0,
            replies_count INTEGER DEFAULT 0,
            engagement_score FLOAT DEFAULT 0.0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # 创建用户反馈表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS user_feedback (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            account TEXT NOT NULL,
            feedback_type TEXT NOT NULL,
            feedback_time TIMESTAMP NOT NULL,
            reason TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # 创建活跃时段统计表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS active_hours_stats (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            account TEXT NOT NULL,
            hour INTEGER NOT NULL,
            fetch_count INTEGER DEFAULT 0,
            new_content_count INTEGER DEFAULT 0,
            probability FLOAT DEFAULT 0.0,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(account, hour)
        )
    ''')
    
    # 创建更新频率统计表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS update_frequency_stats (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            account TEXT NOT NULL,
            frequency_type TEXT NOT NULL,
            observed_count INTEGER DEFAULT 0,
            probability FLOAT DEFAULT 0.0,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(account, frequency_type)
        )
    ''')
    
    # 创建调度策略表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS schedule_strategy (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            strategy_name TEXT NOT NULL,
            strategy_value TEXT NOT NULL,
            success_count INTEGER DEFAULT 0,
            failure_count INTEGER DEFAULT 0,
            success_rate FLOAT DEFAULT 0.0,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(strategy_name, strategy_value)
        )
    ''')
    
    # 创建账号画像表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS account_profiles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            account TEXT NOT NULL UNIQUE,
            name TEXT,
            category TEXT,
            priority INTEGER DEFAULT 1,
            frequency TEXT DEFAULT 'medium',
            content_type TEXT DEFAULT 'mixed',
            status TEXT DEFAULT 'active',
            last_updated TIMESTAMP,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # 创建索引
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_fetch_history_account ON fetch_history(account)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_fetch_history_time ON fetch_history(fetch_time)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_user_feedback_account ON user_feedback(account)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_active_hours_account ON active_hours_stats(account)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_update_frequency_account ON update_frequency_stats(account)')
    
    # 提交更改
    conn.commit()
    
    print(f"✅ 数据库创建成功: {DB_PATH}")
    print(f"✅ 表结构创建完成")
    
    # 关闭连接
    conn.close()

def insert_sample_data():
    """插入示例数据"""
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # 插入示例抓取历史
    sample_fetches = [
        ('karpathy', '2026-04-29 10:15:00', True, 3, 15, 85.5),
        ('karpathy', '2026-04-29 20:30:00', True, 2, 10, 72.3),
        ('AndrewYNg', '2026-04-29 11:00:00', False, 0, 0, 0.0),
        ('sama', '2026-04-29 09:45:00', True, 5, 25, 92.1),
    ]
    
    cursor.executemany('''
        INSERT INTO fetch_history (account, fetch_time, has_new_content, tweets_count, replies_count, engagement_score)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', sample_fetches)
    
    # 插入示例用户反馈
    sample_feedback = [
        ('karpathy', 'positive', '2026-04-29 10:20:00', '内容质量高'),
        ('karpathy', 'positive', '2026-04-29 20:35:00', 'LLM Wiki 相关'),
        ('sama', 'positive', '2026-04-29 09:50:00', '行业洞察'),
    ]
    
    cursor.executemany('''
        INSERT INTO user_feedback (account, feedback_type, feedback_time, reason)
        VALUES (?, ?, ?, ?)
    ''', sample_feedback)
    
    # 插入示例活跃时段统计
    sample_active_hours = [
        ('karpathy', 10, 5, 4, 0.8),
        ('karpathy', 20, 4, 3, 0.75),
        ('karpathy', 21, 3, 2, 0.67),
        ('sama', 9, 3, 2, 0.67),
        ('sama', 10, 2, 1, 0.5),
    ]
    
    cursor.executemany('''
        INSERT INTO active_hours_stats (account, hour, fetch_count, new_content_count, probability)
        VALUES (?, ?, ?, ?, ?)
    ''', sample_active_hours)
    
    # 插入示例更新频率统计
    sample_frequency = [
        ('karpathy', 'daily', 3, 0.3),
        ('karpathy', 'weekly', 5, 0.5),
        ('karpathy', 'monthly', 2, 0.2),
        ('sama', 'daily', 4, 0.4),
        ('sama', 'weekly', 4, 0.4),
        ('sama', 'monthly', 2, 0.2),
    ]
    
    cursor.executemany('''
        INSERT INTO update_frequency_stats (account, frequency_type, observed_count, probability)
        VALUES (?, ?, ?, ?)
    ''', sample_frequency)
    
    # 插入示例调度策略
    sample_strategies = [
        ('fetch_count', '3', 10, 2, 0.83),
        ('fetch_count', '5', 8, 4, 0.67),
        ('fetch_count', '8', 3, 1, 0.75),
        ('fetch_interval', '1h', 5, 3, 0.625),
        ('fetch_interval', '2h', 8, 2, 0.8),
        ('fetch_interval', '3h', 4, 1, 0.8),
    ]
    
    cursor.executemany('''
        INSERT INTO schedule_strategy (strategy_name, strategy_value, success_count, failure_count, success_rate)
        VALUES (?, ?, ?, ?, ?)
    ''', sample_strategies)
    
    # 提交更改
    conn.commit()
    
    print(f"✅ 示例数据插入完成")
    
    # 关闭连接
    conn.close()

def main():
    """主函数"""
    print("=========================================")
    print("Learning Database 初始化")
    print("=========================================")
    print()
    
    # 创建数据库
    create_database()
    
    # 插入示例数据
    insert_sample_data()
    
    print()
    print("=========================================")
    print("初始化完成")
    print("=========================================")
    print()
    print(f"数据库位置: {DB_PATH}")
    print()
    print("现在可以运行 Smart Scheduler 了：")
    print("  python3 programs/smart-scheduler/smart-scheduler.py --help")
    print()

if __name__ == "__main__":
    main()
