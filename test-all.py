#!/usr/bin/env python3
"""
Smart Scheduler 测试脚本
测试所有功能
"""

import sys
import os
from pathlib import Path

# 添加脚本目录到 Python 路径
script_dir = Path(__file__).parent
sys.path.insert(0, str(script_dir))

from learning_algorithms import LearningEngine
from datetime import datetime

def test_learning_algorithms():
    """测试学习算法"""
    print("=========================================")
    print("测试学习算法")
    print("=========================================")
    print()
    
    # 创建学习引擎
    engine = LearningEngine()
    
    # 测试贝叶斯更新
    print("1. 测试贝叶斯更新...")
    engine.bayesian_updater.update_active_hours("karpathy", 10, True)
    engine.bayesian_updater.update_active_hours("karpathy", 10, True)
    engine.bayesian_updater.update_active_hours("karpathy", 10, False)
    print("   ✅ 贝叶斯更新测试完成")
    
    # 测试 Thompson Sampling
    print("2. 测试 Thompson Sampling...")
    accounts = [
        {'account': 'karpathy', 'success_count': 5, 'failure_count': 1},
        {'account': 'sama', 'success_count': 3, 'failure_count': 2},
        {'account': 'AndrewYNg', 'success_count': 4, 'failure_count': 1},
    ]
    selected = engine.select_account(accounts)
    print(f"   ✅ Thompson Sampling 选择: @{selected['account']}")
    
    # 测试时间序列分析
    print("3. 测试时间序列分析...")
    prediction = engine.predict_update_pattern("karpathy")
    print(f"   ✅ 时间序列分析: {prediction['prediction']}")
    
    # 测试协同过滤
    print("4. 测试协同过滤...")
    recommendations = engine.recommend_accounts("karpathy", ["sama", "AndrewYNg", "elonmusk"], 2)
    print(f"   ✅ 协同过滤推荐: {[r['account'] for r in recommendations]}")
    
    # 测试强化学习
    print("5. 测试强化学习...")
    action = engine.get_optimal_action(10)  # 10 点
    print(f"   ✅ 强化学习最优动作: {action}")
    
    print()
    print("=========================================")
    print("所有测试完成")
    print("=========================================")

def test_smart_scheduler():
    """测试智能调度器"""
    print()
    print("=========================================")
    print("测试智能调度器")
    print("=========================================")
    print()
    
    # 导入智能调度器
    from smart_scheduler import SmartScheduler
    
    # 创建调度器
    scheduler = SmartScheduler()
    
    # 测试显示账号画像
    print("1. 测试显示账号画像...")
    scheduler.show_profiles()
    print("   ✅ 账号画像显示完成")
    
    # 测试选择账号
    print("2. 测试选择账号...")
    accounts = scheduler.select_accounts(3)
    print(f"   ✅ 选择账号: {accounts}")
    
    print()
    print("=========================================")
    print("智能调度器测试完成")
    print("=========================================")

def main():
    """主函数"""
    print("=========================================")
    print("Smart Scheduler 完整测试")
    print("=========================================")
    print()
    
    # 测试学习算法
    test_learning_algorithms()
    
    # 测试智能调度器
    test_smart_scheduler()
    
    print()
    print("=========================================")
    print("所有测试完成")
    print("=========================================")
    print()
    print("现在可以运行 Smart Scheduler 了：")
    print("  python3 programs/smart-fetcher/smart-fetcher.py --help")
    print()

if __name__ == "__main__":
    main()
