#!/usr/bin/env python3
"""
Scheduler Core — 调度核心逻辑
包含账号选择、优先级计算、自学习等核心功能
"""

import json
import random
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from pathlib import Path


class AccountProfile:
    """账号画像"""
    
    def __init__(self, data: Dict[str, Any]):
        self.name = data.get('name', '')
        self.handle = data.get('handle', '')
        self.category = data.get('category', 'unknown')
        self.frequency = data.get('frequency', 'medium')
        self.active_hours = data.get('active_hours', [])
        self.content_type = data.get('content_type', 'mixed')
        self.priority = data.get('priority', 1)
        self.last_updated = data.get('last_updated', '')
        self.update_pattern = data.get('update_pattern', '')
        self.interaction = data.get('interaction', 'medium')
        self.status = data.get('status', 'active')
        self.tags = data.get('tags', [])
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'name': self.name,
            'handle': self.handle,
            'category': self.category,
            'frequency': self.frequency,
            'active_hours': self.active_hours,
            'content_type': self.content_type,
            'priority': self.priority,
            'last_updated': self.last_updated,
            'update_pattern': self.update_pattern,
            'interaction': self.interaction,
            'status': self.status,
            'tags': self.tags
        }


class SchedulerCore:
    """调度核心逻辑"""
    
    def __init__(self, config: Dict[str, Any], profiles: Dict[str, AccountProfile]):
        self.config = config
        self.profiles = profiles
        self.current_hour = datetime.now().hour
    
    def calculate_priority_score(self, profile: AccountProfile) -> float:
        """计算账号的优先级分数"""
        # 基础优先级权重
        priority_weights = self.config.get('scheduler', {}).get('priority_weights', {})
        priority_weight = priority_weights.get(profile.priority, 0.5)
        
        # 更新频率权重
        frequency_weights = {'high': 1.0, 'medium': 0.7, 'low': 0.4, 'occasional': 0.2}
        frequency_weight = frequency_weights.get(profile.frequency, 0.5)
        
        # 最后更新时间权重（越久未更新，权重越高）
        time_weight = self._calculate_time_weight(profile.last_updated)
        
        # 活跃时段权重
        active_weight = self._calculate_active_weight(profile.active_hours)
        
        # 综合优先级
        total_priority = (
            priority_weight * 0.4 +
            frequency_weight * 0.3 +
            time_weight * 0.2 +
            active_weight * 0.1
        )
        
        return total_priority
    
    def _calculate_time_weight(self, last_updated: str) -> float:
        """计算时间权重"""
        if not last_updated:
            return 0.5
        
        try:
            last_update_time = datetime.fromisoformat(last_updated)
            hours_since_update = (datetime.now() - last_update_time).total_seconds() / 3600
            
            # 超过 24 小时未更新，权重增加
            if hours_since_update > 24:
                return min(1.0, hours_since_update / 48)
            else:
                return 0.3
        except:
            return 0.5
    
    def _calculate_active_weight(self, active_hours: List[int]) -> float:
        """计算活跃时段权重"""
        if not active_hours:
            return 0.5
        
        if self.current_hour in active_hours:
            return 1.0
        else:
            # 计算距离最近活跃时段的时间
            min_distance = min(
                abs(self.current_hour - hour) for hour in active_hours
            )
            return max(0.1, 1.0 - min_distance / 12)
    
    def select_accounts(self, count: int = 5, 
                       category: Optional[str] = None,
                       exclude: List[str] = None) -> List[str]:
        """选择要抓取的账号"""
        exclude = exclude or []
        
        # 筛选账号
        candidates = []
        for account, profile in self.profiles.items():
            # 排除已抓取的账号
            if account in exclude:
                continue
            
            # 分类筛选
            if category and profile.category != category:
                continue
            
            # 状态筛选
            if profile.status not in ['active', 'pending']:
                continue
            
            candidates.append((account, profile))
        
        # 计算优先级
        account_priorities = []
        for account, profile in candidates:
            priority = self.calculate_priority_score(profile)
            account_priorities.append((account, priority))
        
        # 按优先级排序
        account_priorities.sort(key=lambda x: x[1], reverse=True)
        
        # 选择 top N
        selected = [account for account, _ in account_priorities[:count]]
        
        return selected
    
    def update_frequency(self, account: str, new_frequency: str):
        """更新账号频率"""
        if account in self.profiles:
            self.profiles[account].frequency = new_frequency
    
    def update_active_hours(self, account: str, new_active_hours: List[int]):
        """更新活跃时段"""
        if account in self.profiles:
            self.profiles[account].active_hours = new_active_hours
    
    def update_priority(self, account: str, new_priority: int):
        """更新优先级"""
        if account in self.profiles:
            self.profiles[account].priority = new_priority
    
    def learn_from_fetch(self, account: str, fetch_time: datetime):
        """从抓取结果学习"""
        if account not in self.profiles:
            return
        
        profile = self.profiles[account]
        
        # 更新最后更新时间
        profile.last_updated = fetch_time.isoformat()
        
        # 学习活跃时段
        hour = fetch_time.hour
        if hour not in profile.active_hours:
            profile.active_hours.append(hour)
            profile.active_hours.sort()
        
        # 学习更新频率
        # TODO: 需要更复杂的逻辑来判断频率变化
    
    def learn_from_user_feedback(self, account: str, feedback: str):
        """从用户反馈学习"""
        if account not in self.profiles:
            return
        
        profile = self.profiles[account]
        
        if feedback == 'positive':
            # 提升优先级
            if profile.priority < 3:
                profile.priority += 1
        elif feedback == 'negative':
            # 降低优先级
            if profile.priority > 1:
                profile.priority -= 1


class CrossValidator:
    """交叉验证器"""
    
    def __init__(self, config: Dict[str, Any], profiles: Dict[str, AccountProfile]):
        self.config = config
        self.profiles = profiles
    
    def find_common_follows(self, accounts: List[str]) -> List[Dict[str, Any]]:
        """找出共同关注的账号"""
        # TODO: 实现交叉验证逻辑
        # 1. 获取每个账号的关注列表
        # 2. 统计共同关注
        # 3. 筛选符合条件的账号
        
        return []
    
    def recommend_accounts(self, common_follows: List[Dict[str, Any]]) -> List[str]:
        """推荐值得关注的账号"""
        # TODO: 实现推荐逻辑
        # 1. 根据共同关注数筛选
        # 2. 根据粉丝数筛选
        # 3. 根据内容相关性筛选
        
        return []


class LearningEngine:
    """自学习引擎"""
    
    def __init__(self, config: Dict[str, Any], profiles: Dict[str, AccountProfile]):
        self.config = config
        self.profiles = profiles
    
    def analyze_update_pattern(self, account: str, 
                              fetch_history: List[Dict[str, Any]]) -> Dict[str, Any]:
        """分析更新模式"""
        # TODO: 实现更新模式分析
        # 1. 分析抓取历史
        # 2. 识别更新规律
        # 3. 预测下次更新时间
        
        return {}
    
    def optimize_schedule(self, accounts: List[str]) -> Dict[str, List[int]]:
        """优化抓取时间表"""
        # TODO: 实现时间表优化
        # 1. 分析每个账号的更新模式
        # 2. 计算最优抓取时间
        # 3. 生成时间表
        
        return {}
