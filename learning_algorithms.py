#!/usr/bin/env python3
"""
Learning Algorithms — 学习算法核心模块
包含贝叶斯更新、Thompson Sampling、时间序列分析、协同过滤、强化学习
"""

import numpy as np
import pandas as pd
from scipy import stats
from typing import List, Dict, Any, Tuple
from datetime import datetime, timedelta
import sqlite3
from pathlib import Path

# 数据库路径
DB_PATH = Path(__file__).parent.parent.parent / "input" / "learn" / "learning.db"


class BayesianUpdater:
    """贝叶斯更新器"""
    
    def __init__(self):
        pass
    
    def update_probability(self, old_probability: float, old_count: int, 
                          new_evidence: float) -> Tuple[float, int]:
        """
        贝叶斯更新概率
        
        old_probability: 旧概率
        old_count: 旧观测次数
        new_evidence: 新证据（1.0 或 0.0）
        
        返回: (新概率, 新次数)
        """
        new_count = old_count + 1
        new_probability = (old_probability * old_count + new_evidence) / new_count
        return new_probability, new_count
    
    def update_active_hours(self, account: str, hour: int, has_new_content: bool):
        """
        更新活跃时段概率
        
        account: 账号名
        hour: 小时（0-23）
        has_new_content: 是否有新内容
        """
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # 获取现有统计
        cursor.execute('''
            SELECT fetch_count, new_content_count, probability
            FROM active_hours_stats
            WHERE account = ? AND hour = ?
        ''', (account, hour))
        
        result = cursor.fetchone()
        
        if result:
            old_count, old_new_count, old_probability = result
            new_evidence = 1.0 if has_new_content else 0.0
            new_probability, new_count = self.update_probability(
                old_probability, old_count, new_evidence
            )
            new_new_count = old_new_count + (1 if has_new_content else 0)
            
            # 更新统计
            cursor.execute('''
                UPDATE active_hours_stats
                SET fetch_count = ?, new_content_count = ?, probability = ?, updated_at = ?
                WHERE account = ? AND hour = ?
            ''', (new_count, new_new_count, new_probability, datetime.now().isoformat(), 
                  account, hour))
        else:
            # 插入新记录
            new_probability = 1.0 if has_new_content else 0.0
            cursor.execute('''
                INSERT INTO active_hours_stats (account, hour, fetch_count, new_content_count, probability, updated_at)
                VALUES (?, ?, 1, ?, ?, ?)
            ''', (account, hour, 1 if has_new_content else 0, new_probability, 
                  datetime.now().isoformat()))
        
        conn.commit()
        conn.close()
    
    def update_frequency(self, account: str, frequency_type: str):
        """
        更新频率统计
        
        account: 账号名
        frequency_type: 频率类型（daily, weekly, monthly）
        """
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # 获取现有统计
        cursor.execute('''
            SELECT observed_count
            FROM update_frequency_stats
            WHERE account = ? AND frequency_type = ?
        ''', (account, frequency_type))
        
        result = cursor.fetchone()
        
        if result:
            old_count = result[0]
            new_count = old_count + 1
            
            # 更新统计
            cursor.execute('''
                UPDATE update_frequency_stats
                SET observed_count = ?, updated_at = ?
                WHERE account = ? AND frequency_type = ?
            ''', (new_count, datetime.now().isoformat(), account, frequency_type))
        else:
            # 插入新记录
            cursor.execute('''
                INSERT INTO update_frequency_stats (account, frequency_type, observed_count, updated_at)
                VALUES (?, ?, 1, ?)
            ''', (account, frequency_type, datetime.now().isoformat()))
        
        # 重新计算概率
        self._recalculate_frequency_probabilities(account)
        
        conn.commit()
        conn.close()
    
    def _recalculate_frequency_probabilities(self, account: str):
        """重新计算频率概率"""
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # 获取所有频率统计
        cursor.execute('''
            SELECT frequency_type, observed_count
            FROM update_frequency_stats
            WHERE account = ?
        ''', (account,))
        
        results = cursor.fetchall()
        
        # 计算总观测次数
        total_count = sum(count for _, count in results)
        
        # 更新概率
        for frequency_type, count in results:
            probability = count / total_count if total_count > 0 else 0.0
            cursor.execute('''
                UPDATE update_frequency_stats
                SET probability = ?
                WHERE account = ? AND frequency_type = ?
            ''', (probability, account, frequency_type))
        
        conn.commit()
        conn.close()


class ThompsonSampler:
    """Thompson Sampling 选择器"""
    
    def __init__(self):
        pass
    
    def select_account(self, accounts: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        使用 Thompson Sampling 选择账号
        
        accounts: 账号列表，每个账号有 success_count 和 failure_count
        """
        samples = []
        
        for account in accounts:
            alpha = account.get('success_count', 0) + 1
            beta = account.get('failure_count', 0) + 1
            
            # 从 Beta 分布中采样
            sample = np.random.beta(alpha, beta)
            samples.append((account, sample))
        
        # 选择采样值最高的账号
        selected = max(samples, key=lambda x: x[1])
        return selected[0]
    
    def update_account_stats(self, account: str, success: bool):
        """
        更新账号统计
        
        account: 账号名
        success: 是否成功（有新内容）
        """
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # 获取现有统计
        cursor.execute('''
            SELECT success_count, failure_count
            FROM account_profiles
            WHERE account = ?
        ''', (account,))
        
        result = cursor.fetchone()
        
        if result:
            success_count, failure_count = result
            if success:
                success_count += 1
            else:
                failure_count += 1
            
            # 更新统计
            cursor.execute('''
                UPDATE account_profiles
                SET success_count = ?, failure_count = ?, updated_at = ?
                WHERE account = ?
            ''', (success_count, failure_count, datetime.now().isoformat(), account))
        else:
            # 插入新记录
            success_count = 1 if success else 0
            failure_count = 0 if success else 1
            cursor.execute('''
                INSERT INTO account_profiles (account, success_count, failure_count, updated_at)
                VALUES (?, ?, ?, ?)
            ''', (account, success_count, failure_count, datetime.now().isoformat()))
        
        conn.commit()
        conn.close()


class TimeSeriesAnalyzer:
    """时间序列分析器"""
    
    def __init__(self):
        pass
    
    def predict_update_pattern(self, account: str) -> Dict[str, Any]:
        """
        预测账号的更新模式
        
        account: 账号名
        """
        # 获取历史数据
        history = self._get_account_history(account)
        
        if len(history) < 7:  # 数据不足
            return {
                'prediction': 'insufficient_data',
                'confidence': 0.0,
                'recommendation': 'continue_collecting'
            }
        
        # 分析更新模式
        pattern = self._analyze_pattern(history)
        
        # 预测下次更新时间
        next_update = self._predict_next_update(history, pattern)
        
        return {
            'prediction': 'pattern_detected',
            'confidence': pattern['confidence'],
            'pattern': pattern,
            'next_update': next_update,
            'recommendation': self._generate_recommendation(pattern)
        }
    
    def _get_account_history(self, account: str) -> List[Dict[str, Any]]:
        """获取账号历史数据"""
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT fetch_time, has_new_content, tweets_count, replies_count
            FROM fetch_history
            WHERE account = ?
            ORDER BY fetch_time
        ''', (account,))
        
        results = cursor.fetchall()
        conn.close()
        
        history = []
        for row in results:
            history.append({
                'time': row[0],
                'has_new': row[1],
                'tweets': row[2],
                'replies': row[3]
            })
        
        return history
    
    def _analyze_pattern(self, history: List[Dict[str, Any]]) -> Dict[str, Any]:
        """分析更新模式"""
        # 转换为 DataFrame
        df = pd.DataFrame(history)
        df['time'] = pd.to_datetime(df['time'])
        df['hour'] = df['time'].dt.hour
        df['day_of_week'] = df['time'].dt.dayofweek
        
        # 分析活跃时段
        active_hours = df[df['has_new'] == True]['hour'].value_counts().head(5)
        
        # 分析活跃天数
        active_days = df[df['has_new'] == True]['day_of_week'].value_counts().head(3)
        
        # 计算置信度
        total_fetches = len(df)
        new_content_count = len(df[df['has_new'] == True])
        confidence = new_content_count / total_fetches if total_fetches > 0 else 0.0
        
        return {
            'active_hours': active_hours.to_dict(),
            'active_days': active_days.to_dict(),
            'confidence': confidence,
            'total_fetches': total_fetches,
            'new_content_count': new_content_count
        }
    
    def _predict_next_update(self, history: List[Dict[str, Any]], 
                            pattern: Dict[str, Any]) -> datetime:
        """预测下次更新时间"""
        # 获取最近一次更新
        last_update = max(history, key=lambda x: x['time'])['time']
        
        # 根据模式预测
        if pattern['confidence'] > 0.7:  # 高置信度
            # 使用最活跃的时段
            most_active_hour = max(pattern['active_hours'].items(), key=lambda x: x[1])[0]
            next_update = datetime.now().replace(hour=most_active_hour, minute=0, second=0)
            
            # 如果预测时间已过，则推到明天
            if next_update <= datetime.now():
                next_update += timedelta(days=1)
        else:  # 低置信度
            # 使用默认间隔（24小时）
            next_update = datetime.fromisoformat(last_update) + timedelta(hours=24)
        
        return next_update
    
    def _generate_recommendation(self, pattern: Dict[str, Any]) -> str:
        """生成建议"""
        if pattern['confidence'] > 0.8:
            return "高置信度：可以按照预测时间抓取"
        elif pattern['confidence'] > 0.5:
            return "中置信度：建议在预测时间前后各抓取一次"
        else:
            return "低置信度：建议继续收集数据，暂时使用默认抓取策略"


class CollaborativeFilter:
    """协同过滤推荐器"""
    
    def __init__(self):
        pass
    
    def recommend_accounts(self, target_account: str, 
                          all_accounts: List[str], 
                          top_n: int = 5) -> List[Dict[str, Any]]:
        """
        推荐相似账号
        
        target_account: 目标账号
        all_accounts: 所有账号列表
        top_n: 推荐数量
        """
        similarities = []
        
        for account in all_accounts:
            if account == target_account:
                continue
            
            # 计算相似度
            similarity = self._calculate_similarity(target_account, account)
            similarities.append({
                'account': account,
                'similarity': similarity,
                'reason': self._generate_reason(target_account, account, similarity)
            })
        
        # 按相似度排序
        similarities.sort(key=lambda x: x['similarity'], reverse=True)
        
        # 返回 top N
        return similarities[:top_n]
    
    def _calculate_similarity(self, account1: str, account2: str) -> float:
        """计算两个账号的相似度"""
        # 获取账号特征
        features1 = self._get_account_features(account1)
        features2 = self._get_account_features(account2)
        
        if not features1 or not features2:
            return 0.0
        
        # 计算余弦相似度
        similarity = self._cosine_similarity(features1, features2)
        
        return similarity
    
    def _get_account_features(self, account: str) -> Dict[str, float]:
        """获取账号特征"""
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # 获取抓取历史
        cursor.execute('''
            SELECT AVG(tweets_count), AVG(replies_count), AVG(engagement_score)
            FROM fetch_history
            WHERE account = ?
        ''', (account,))
        
        result = cursor.fetchone()
        conn.close()
        
        if result and result[0] is not None:
            return {
                'avg_tweets': result[0],
                'avg_replies': result[1],
                'avg_engagement': result[2]
            }
        
        return None
    
    def _cosine_similarity(self, features1: Dict[str, float], 
                          features2: Dict[str, float]) -> float:
        """计算余弦相似度"""
        # 转换为向量
        vec1 = np.array([features1['avg_tweets'], features1['avg_replies'], features1['avg_engagement']])
        vec2 = np.array([features2['avg_tweets'], features2['avg_replies'], features2['avg_engagement']])
        
        # 计算余弦相似度
        dot_product = np.dot(vec1, vec2)
        norm1 = np.linalg.norm(vec1)
        norm2 = np.linalg.norm(vec2)
        
        if norm1 == 0 or norm2 == 0:
            return 0.0
        
        return dot_product / (norm1 * norm2)
    
    def _generate_reason(self, account1: str, account2: str, similarity: float) -> str:
        """生成推荐理由"""
        if similarity > 0.8:
            return f"与 @{account1} 高度相似"
        elif similarity > 0.5:
            return f"与 @{account1} 中度相似"
        else:
            return f"与 @{account1} 低度相似"


class ReinforcementLearner:
    """强化学习器"""
    
    def __init__(self, states: int, actions: int, 
                 learning_rate: float = 0.1, 
                 discount_factor: float = 0.95):
        self.states = states
        self.actions = actions
        self.learning_rate = learning_rate
        self.discount_factor = discount_factor
        self.q_table = np.zeros((states, actions))
    
    def choose_action(self, state: int, epsilon: float = 0.1) -> int:
        """
        选择动作（ε-贪心策略）
        
        state: 状态
        epsilon: 探索率
        """
        if np.random.random() < epsilon:
            # 探索：随机选择动作
            return np.random.randint(self.actions)
        else:
            # 利用：选择 Q 值最大的动作
            return np.argmax(self.q_table[state])
    
    def learn(self, state: int, action: int, reward: float, next_state: int):
        """
        学习更新 Q 表
        
        state: 当前状态
        action: 动作
        reward: 奖励
        next_state: 下一个状态
        """
        # Q(s,a) = Q(s,a) + α[r + γ max Q(s',a') - Q(s,a)]
        old_value = self.q_table[state, action]
        next_max = np.max(self.q_table[next_state])
        
        new_value = old_value + self.learning_rate * (
            reward + self.discount_factor * next_max - old_value
        )
        
        self.q_table[state, action] = new_value
    
    def get_policy(self) -> List[int]:
        """获取策略（每个状态的最优动作）"""
        return [np.argmax(self.q_table[state]) for state in range(self.states)]


class LearningEngine:
    """学习引擎（整合所有算法）"""
    
    def __init__(self):
        self.bayesian_updater = BayesianUpdater()
        self.thompson_sampler = ThompsonSampler()
        self.time_series_analyzer = TimeSeriesAnalyzer()
        self.collaborative_filter = CollaborativeFilter()
        self.reinforcement_learner = ReinforcementLearner(states=24, actions=5)  # 24小时，5种抓取策略
    
    def learn_from_fetch(self, account: str, fetch_time: datetime, 
                        has_new_content: bool, tweets_count: int, 
                        replies_count: int, engagement_score: float):
        """
        从抓取结果学习
        
        account: 账号名
        fetch_time: 抓取时间
        has_new_content: 是否有新内容
        tweets_count: 推文数量
        replies_count: 评论数量
        engagement_score: 互动分数
        """
        # 1. 更新贝叶斯概率
        hour = fetch_time.hour
        self.bayesian_updater.update_active_hours(account, hour, has_new_content)
        
        # 2. 更新 Thompson Sampling 统计
        self.thompson_sampler.update_account_stats(account, has_new_content)
        
        # 3. 记录抓取历史
        self._record_fetch_history(account, fetch_time, has_new_content, 
                                  tweets_count, replies_count, engagement_score)
        
        # 4. 更新强化学习
        state = hour  # 状态：小时
        action = self._get_action(tweets_count, replies_count)  # 动作：抓取策略
        reward = engagement_score / 100.0  # 奖励：互动分数
        next_state = (hour + 1) % 24  # 下一个状态：下一小时
        
        self.reinforcement_learner.learn(state, action, reward, next_state)
    
    def learn_from_feedback(self, account: str, feedback_type: str, reason: str = ""):
        """
        从用户反馈学习
        
        account: 账号名
        feedback_type: 反馈类型（positive, negative, neutral）
        reason: 原因
        """
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # 记录反馈
        cursor.execute('''
            INSERT INTO user_feedback (account, feedback_type, feedback_time, reason)
            VALUES (?, ?, ?, ?)
        ''', (account, feedback_type, datetime.now().isoformat(), reason))
        
        # 更新账号优先级
        self._update_account_priority(account, feedback_type)
        
        conn.commit()
        conn.close()
    
    def predict_update_pattern(self, account: str) -> Dict[str, Any]:
        """预测更新模式"""
        return self.time_series_analyzer.predict_update_pattern(account)
    
    def recommend_accounts(self, target_account: str, 
                          all_accounts: List[str], 
                          top_n: int = 5) -> List[Dict[str, Any]]:
        """推荐相似账号"""
        return self.collaborative_filter.recommend_accounts(target_account, all_accounts, top_n)
    
    def select_account(self, accounts: List[Dict[str, Any]]) -> Dict[str, Any]:
        """使用 Thompson Sampling 选择账号"""
        return self.thompson_sampler.select_account(accounts)
    
    def get_optimal_action(self, state: int) -> int:
        """获取最优动作"""
        return self.reinforcement_learner.choose_action(state, epsilon=0.0)  # 不探索
    
    def _record_fetch_history(self, account: str, fetch_time: datetime,
                             has_new_content: bool, tweets_count: int,
                             replies_count: int, engagement_score: float):
        """记录抓取历史"""
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO fetch_history (account, fetch_time, has_new_content, tweets_count, replies_count, engagement_score)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (account, fetch_time.isoformat(), has_new_content, tweets_count, 
              replies_count, engagement_score))
        
        conn.commit()
        conn.close()
    
    def _get_action(self, tweets_count: int, replies_count: int) -> int:
        """根据抓取结果获取动作"""
        total = tweets_count + replies_count
        
        if total >= 20:
            return 4  # 高密度
        elif total >= 10:
            return 3  # 中高密度
        elif total >= 5:
            return 2  # 中密度
        elif total >= 1:
            return 1  # 低密度
        else:
            return 0  # 无内容
    
    def _update_account_priority(self, account: str, feedback_type: str):
        """更新账号优先级"""
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # 获取当前优先级
        cursor.execute('''
            SELECT priority FROM account_profiles WHERE account = ?
        ''', (account,))
        
        result = cursor.fetchone()
        
        if result:
            current_priority = result[0]
            
            # 根据反馈调整优先级
            if feedback_type == 'positive':
                new_priority = min(3, current_priority + 1)
            elif feedback_type == 'negative':
                new_priority = max(1, current_priority - 1)
            else:
                new_priority = current_priority
            
            # 更新优先级
            cursor.execute('''
                UPDATE account_profiles SET priority = ?, updated_at = ?
                WHERE account = ?
            ''', (new_priority, datetime.now().isoformat(), account))
        
        conn.commit()
        conn.close()


# 测试代码
if __name__ == "__main__":
    print("=========================================")
    print("Learning Algorithms 测试")
    print("=========================================")
    print()
    
    # 创建学习引擎
    engine = LearningEngine()
    
    # 测试贝叶斯更新
    print("测试贝叶斯更新...")
    engine.bayesian_updater.update_active_hours("karpathy", 10, True)
    engine.bayesian_updater.update_active_hours("karpathy", 10, True)
    engine.bayesian_updater.update_active_hours("karpathy", 10, False)
    print("✅ 贝叶斯更新测试完成")
    
    # 测试 Thompson Sampling
    print("测试 Thompson Sampling...")
    accounts = [
        {'account': 'karpathy', 'success_count': 5, 'failure_count': 1},
        {'account': 'sama', 'success_count': 3, 'failure_count': 2},
        {'account': 'AndrewYNg', 'success_count': 4, 'failure_count': 1},
    ]
    selected = engine.select_account(accounts)
    print(f"✅ Thompson Sampling 选择: @{selected['account']}")
    
    # 测试时间序列分析
    print("测试时间序列分析...")
    prediction = engine.predict_update_pattern("karpathy")
    print(f"✅ 时间序列分析: {prediction['prediction']}")
    
    # 测试协同过滤
    print("测试协同过滤...")
    recommendations = engine.recommend_accounts("karpathy", ["sama", "AndrewYNg", "elonmusk"], 2)
    print(f"✅ 协同过滤推荐: {[r['account'] for r in recommendations]}")
    
    # 测试强化学习
    print("测试强化学习...")
    action = engine.get_optimal_action(10)  # 10 点
    print(f"✅ 强化学习最优动作: {action}")
    
    print()
    print("=========================================")
    print("所有测试完成")
    print("=========================================")
