#!/usr/bin/env python3
"""
Cross Validation — 交叉验证脚本
交叉验证账号关注关系，发现新账号
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


def get_account_following(account: str) -> List[str]:
    """获取账号的关注列表"""
    try:
        cmd = f'autocli twitter following --user {account} --limit 50 --format json'
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=30)
        
        if result.returncode == 0:
            data = json.loads(result.stdout)
            if data:
                return [user.get('screen_name', '') for user in data if user.get('screen_name')]
    except Exception as e:
        print(f"Error getting following for {account}: {e}")
    
    return []


def cross_validate_accounts(accounts: List[str]) -> Dict[str, Any]:
    """交叉验证账号"""
    print(f"交叉验证 {len(accounts)} 个账号...")
    
    # 获取每个账号的关注列表
    following_map = {}
    for account in accounts:
        print(f"获取 @{account} 的关注列表...")
        following = get_account_following(account)
        following_map[account] = set(following)
        print(f"  ✓ 获取到 {len(following)} 个关注")
    
    # 统计共同关注
    common_follows = {}
    for account1 in accounts:
        for account2 in accounts:
            if account1 >= account2:  # 避免重复
                continue
            
            # 计算共同关注
            common = following_map[account1] & following_map[account2]
            if common:
                for follow in common:
                    if follow not in common_follows:
                        common_follows[follow] = {
                            'account': follow,
                            'common_count': 0,
                            'referenced_by': []
                        }
                    common_follows[follow]['common_count'] += 1
                    common_follows[follow]['referenced_by'].append(f"@{account1} 和 @{account2}")
    
    # 按共同关注数排序
    sorted_follows = sorted(common_follows.values(), 
                           key=lambda x: x['common_count'], 
                           reverse=True)
    
    return {
        'accounts': accounts,
        'common_follows': sorted_follows[:20],  # top 20
        'total_common': len(sorted_follows)
    }


def recommend_accounts(cross_validation_result: Dict[str, Any]) -> List[Dict[str, Any]]:
    """推荐值得关注的账号"""
    recommendations = []
    
    for follow in cross_validation_result['common_follows']:
        account = follow['account']
        common_count = follow['common_count']
        
        # 获取账号信息
        try:
            cmd = f'autocli twitter profile {account} --format json'
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=15)
            
            if result.returncode == 0:
                data = json.loads(result.stdout)
                if data:
                    profile = data[0]
                    followers = profile.get('followers', 0)
                    
                    # 只推荐粉丝数 > 10000 的账号
                    if followers >= 10000:
                        recommendations.append({
                            'account': account,
                            'name': profile.get('name', ''),
                            'followers': followers,
                            'common_count': common_count,
                            'referenced_by': follow['referenced_by'],
                            'reason': f"被 {common_count} 个大佬共同关注"
                        })
        except Exception as e:
            print(f"Error getting profile for {account}: {e}")
    
    # 按共同关注数排序
    recommendations.sort(key=lambda x: x['common_count'], reverse=True)
    
    return recommendations[:10]  # top 10


def save_recommendations(recommendations: List[Dict[str, Any]]):
    """保存推荐结果"""
    today = datetime.now().strftime("%Y-%m-%d")
    output_path = INPUT_DIR / "推荐账号" / f"{today}.json"
    
    # 确保目录存在
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    # 保存结果
    data = {
        'date': today,
        'recommendations': recommendations
    }
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    
    print(f"✅ 推荐结果保存到: {output_path}")


def main():
    """主函数"""
    print("=========================================")
    print("交叉验证")
    print("=========================================")
    print()
    
    # 加载账号画像
    with open(PROFILES_PATH, 'r', encoding='utf-8') as f:
        profiles = json.load(f)
    
    # 获取核心大佬
    core_accounts = []
    for account, profile in profiles.get('accounts', {}).items():
        if profile.get('category') == 'core' and profile.get('priority', 0) >= 2:
            core_accounts.append(account)
    
    # 随机选择 3-5 个账号
    import random
    selected_accounts = random.sample(core_accounts, min(5, len(core_accounts)))
    
    print(f"选择账号: {selected_accounts}")
    print()
    
    # 交叉验证
    result = cross_validate_accounts(selected_accounts)
    
    print()
    print(f"发现 {result['total_common']} 个共同关注")
    print()
    
    # 推荐账号
    recommendations = recommend_accounts(result)
    
    print(f"推荐 {len(recommendations)} 个值得关注的账号:")
    for i, rec in enumerate(recommendations, 1):
        print(f"  {i}. @{rec['account']} ({rec['name']}) - {rec['reason']}")
    
    # 保存推荐结果
    save_recommendations(recommendations)
    
    print()
    print("=========================================")
    print("交叉验证完成")
    print("=========================================")


if __name__ == "__main__":
    main()
