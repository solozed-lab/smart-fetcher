# 算法说明

## 概述

Smart Scheduler 使用了多种机器学习算法来实现智能调度，包括贝叶斯更新、Thompson Sampling、时间序列分析、协同过滤和强化学习。

## 1. 贝叶斯更新 (Bayesian Update)

### 原理

贝叶斯更新是一种概率估计方法，用于根据新证据更新先验概率。

### 公式

```
P(有新内容|时段) = (旧概率 × 旧次数 + 新证据) / (旧次数 + 1)
```

其中：
- `旧概率`：之前的概率估计
- `旧次数`：之前的观测次数
- `新证据`：新的观测结果（1.0 或 0.0）

### 应用场景

1. **活跃时段概率估计**：估计账号在某个时段有新内容的概率
2. **更新频率概率估计**：估计账号的更新频率
3. **内容质量概率估计**：估计账号的内容质量

### 实现

```python
class BayesianUpdater:
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
```

### 示例

```python
updater = BayesianUpdater()

# 初始概率 0.5，观测次数 0
probability = 0.5
count = 0

# 观测到有新内容
probability, count = updater.update_probability(probability, count, 1.0)
# 结果：probability = 1.0, count = 1

# 观测到无新内容
probability, count = updater.update_probability(probability, count, 0.0)
# 结果：probability = 0.5, count = 2

# 再次观测到有新内容
probability, count = updater.update_probability(probability, count, 1.0)
# 结果：probability = 0.667, count = 3
```

## 2. Thompson Sampling

### 原理

Thompson Sampling 是一种用于平衡探索与利用的算法，常用于多臂老虎机问题。

### 算法

1. 为每个账号维护一个 Beta 分布 Beta(α, β)
2. α = 成功次数 + 1
3. β = 失败次数 + 1
4. 从每个账号的 Beta 分布中采样
5. 选择采样值最高的账号

### 应用场景

1. **选择抓取账号**：平衡探索新账号和利用已知高质量账号
2. **自适应调整**：根据抓取结果动态调整策略

### 实现

```python
class ThompsonSampler:
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
```

### 示例

```python
sampler = ThompsonSampler()

accounts = [
    {'account': 'karpathy', 'success_count': 5, 'failure_count': 1},
    {'account': 'sama', 'success_count': 3, 'failure_count': 2},
    {'account': 'AndrewYNg', 'success_count': 4, 'failure_count': 1},
]

# 选择账号
selected = sampler.select_account(accounts)
# 结果：可能是 karpathy（因为 success_count 最高）
```

## 3. 时间序列分析 (Time Series Analysis)

### 原理

时间序列分析用于预测未来的数据点，基于历史数据的趋势和周期性。

### 算法

使用 Prophet 或 ARIMA 模型：

1. **Prophet**：Facebook 开发的时间序列预测工具
2. **ARIMA**：自回归积分滑动平均模型

### 应用场景

1. **预测更新时间**：预测账号的下次更新时间
2. **识别更新周期**：识别每天、每周、每月的更新模式
3. **预测内容密度**：预测未来的内容密度

### 实现

```python
class TimeSeriesAnalyzer:
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
```

### 示例

```python
analyzer = TimeSeriesAnalyzer()

# 预测更新模式
prediction = analyzer.predict_update_pattern("karpathy")
# 结果：
# {
#     'prediction': 'pattern_detected',
#     'confidence': 0.85,
#     'pattern': {
#         'active_hours': {10: 0.8, 20: 0.9},
#         'active_days': {0: 0.7, 2: 0.8},
#         'confidence': 0.85
#     },
#     'next_update': '2026-04-30 10:00:00',
#     'recommendation': '高置信度：可以按照预测时间抓取'
# }
```

## 4. 协同过滤 (Collaborative Filtering)

### 原理

协同过滤是一种推荐算法，基于用户行为相似性进行推荐。

### 算法

1. **基于用户的协同过滤**：找到与目标用户相似的用户
2. **计算相似度**：使用余弦相似度或皮尔逊相关系数
3. **推荐**：推荐相似用户喜欢的内容

### 应用场景

1. **推荐相似账号**：发现与你关注的账号相似的新账号
2. **发现新账号**：扩展关注列表
3. **内容推荐**：推荐你可能感兴趣的内容

### 实现

```python
class CollaborativeFilter:
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
```

### 示例

```python
filter = CollaborativeFilter()

# 推荐相似账号
recommendations = filter.recommend_accounts(
    target_account="karpathy",
    all_accounts=["sama", "AndrewYNg", "elonmusk"],
    top_n=5
)
# 结果：
# [
#     {'account': 'sama', 'similarity': 0.85, 'reason': '与 @karpathy 高度相似'},
#     {'account': 'AndrewYNg', 'similarity': 0.78, 'reason': '与 @karpathy 中度相似'},
#     ...
# ]
```

## 5. 强化学习 (Reinforcement Learning)

### 原理

强化学习是一种机器学习方法，通过与环境交互来学习最优策略。

### 算法

使用 Q-Learning 算法：

1. **状态 (State)**：当前时间（小时）
2. **动作 (Action)**：抓取策略
3. **奖励 (Reward)**：内容质量分数
4. **Q 表**：存储状态-动作对的价值

### 公式

```
Q(s,a) = Q(s,a) + α[r + γ max Q(s',a') - Q(s,a)]
```

其中：
- `α`：学习率
- `γ`：折扣因子
- `r`：奖励
- `s`：当前状态
- `a`：动作
- `s'`：下一个状态

### 应用场景

1. **动态调整抓取策略**：根据学习结果调整抓取策略
2. **最大化长期收益**：获取高质量内容
3. **自适应学习**：根据环境变化调整策略

### 实现

```python
class ReinforcementLearner:
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
```

### 示例

```python
learner = ReinforcementLearner(states=24, actions=5)

# 选择动作
state = 10  # 10 点
action = learner.choose_action(state)
# 结果：可能是 2（中密度抓取）

# 学习
reward = 0.85  # 内容质量分数
next_state = 11  # 11 点
learner.learn(state, action, reward, next_state)

# 获取最优策略
policy = learner.get_policy()
# 结果：[2, 2, 1, 1, 0, 0, 1, 2, 3, 3, 2, 2, 1, 1, 2, 3, 3, 2, 1, 1, 2, 3, 2, 1]
```

## 算法组合

### 学习引擎

学习引擎整合了所有算法，提供统一的接口：

```python
class LearningEngine:
    def __init__(self):
        self.bayesian_updater = BayesianUpdater()
        self.thompson_sampler = ThompsonSampler()
        self.time_series_analyzer = TimeSeriesAnalyzer()
        self.collaborative_filter = CollaborativeFilter()
        self.reinforcement_learner = ReinforcementLearner(states=24, actions=5)
    
    def learn_from_fetch(self, account: str, fetch_time: datetime, 
                        has_new_content: bool, tweets_count: int, 
                        replies_count: int, engagement_score: float):
        """
        从抓取结果学习
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
```

### 自适应调度

调度器使用学习结果进行自适应调度：

```python
class SmartScheduler:
    def should_execute_now(self) -> bool:
        """根据学习结果决定是否现在执行"""
        
        # 查询学习结果：这个时段有多少账号活跃？
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
    
    def get_adaptive_count(self) -> int:
        """根据学习结果动态调整抓取数量"""
        
        # 查询最近 24 小时的抓取结果
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
```

## 性能优化

### 缓存

使用缓存减少重复计算：

```python
from functools import lru_cache

@lru_cache(maxsize=128)
def calculate_similarity(account1: str, account2: str) -> float:
    """计算两个账号的相似度（带缓存）"""
    pass
```

### 批量操作

使用批量操作减少数据库交互：

```python
def batch_update_active_hours(accounts: List[str], hour: int, has_new_content: bool):
    """批量更新活跃时段统计"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # 批量插入或更新
    cursor.executemany('''
        INSERT INTO active_hours_stats (account, hour, fetch_count, new_content_count, probability)
        VALUES (?, ?, 1, ?, ?)
        ON CONFLICT(account, hour) DO UPDATE SET
            fetch_count = fetch_count + 1,
            new_content_count = new_content_count + ?,
            probability = (probability * fetch_count + ?) / (fetch_count + 1)
    ''', [(account, hour, 1 if has_new_content else 0, 1.0 if has_new_content else 0.0,
           1 if has_new_content else 0, 1.0 if has_new_content else 0.0) 
          for account in accounts])
    
    conn.commit()
    conn.close()
```

### 异步操作

使用异步操作提高并发性能：

```python
import asyncio

async def fetch_account_async(account: str) -> Dict[str, Any]:
    """异步抓取账号"""
    # 使用 aiohttp 或 httpx 进行异步 HTTP 请求
    pass

async def fetch_multiple_accounts(accounts: List[str]) -> List[Dict[str, Any]]:
    """异步抓取多个账号"""
    tasks = [fetch_account_async(account) for account in accounts]
    return await asyncio.gather(*tasks)
```
