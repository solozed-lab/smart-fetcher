# API 文档

## 概述

Smart Scheduler 提供了 Python API 和命令行接口，用于智能抓取调度。

## Python API

### SmartScheduler 类

智能调度器主类。

```python
from smart_scheduler import SmartScheduler

scheduler = SmartScheduler()
```

#### 方法

##### `should_execute_now() -> bool`

根据学习结果决定是否现在执行。

**返回值**：
- `True`：应该执行
- `False`：应该跳过

**示例**：
```python
if scheduler.should_execute_now():
    print("执行抓取")
else:
    print("跳过执行")
```

##### `get_adaptive_count() -> int`

根据学习结果动态调整抓取数量。

**返回值**：抓取数量（3-8）

**示例**：
```python
count = scheduler.get_adaptive_count()
print(f"抓取数量: {count}")
```

##### `get_adaptive_interval() -> int`

根据学习结果动态调整抓取间隔（分钟）。

**返回值**：抓取间隔（30-120 分钟）

**示例**：
```python
interval = scheduler.get_adaptive_interval()
print(f"抓取间隔: {interval} 分钟")
```

##### `select_accounts(count: int = 5, category: str = None) -> List[str]`

选择要抓取的账号。

**参数**：
- `count`：抓取数量（默认 5）
- `category`：账号分类（可选）

**返回值**：账号列表

**示例**：
```python
accounts = scheduler.select_accounts(3)
print(f"选择账号: {accounts}")
```

##### `fetch_account(account: str, with_replies: bool = False) -> Dict[str, Any]`

抓取单个账号。

**参数**：
- `account`：账号名
- `with_replies`：是否抓取评论区（默认 False）

**返回值**：
```python
{
    "account": "karpathy",
    "success": True,
    "tweets": [...],
    "replies": [...],
    "error": None
}
```

**示例**：
```python
result = scheduler.fetch_account("karpathy", with_replies=True)
print(f"推文数量: {len(result['tweets'])}")
```

##### `run_adaptive_fetch(with_replies: bool = False) -> List[Dict]`

执行自适应抓取。

**参数**：
- `with_replies`：是否抓取评论区（默认 False）

**返回值**：抓取结果列表

**示例**：
```python
results = scheduler.run_adaptive_fetch(with_replies=True)
print(f"抓取 {len(results)} 个账号")
```

##### `run_scheduled_fetch(count: int = 5, with_replies: bool = False) -> List[Dict]`

执行定时抓取。

**参数**：
- `count`：抓取数量（默认 5）
- `with_replies`：是否抓取评论区（默认 False）

**返回值**：抓取结果列表

**示例**：
```python
results = scheduler.run_scheduled_fetch(3, with_replies=True)
```

##### `run_manual_fetch(accounts: List[str], with_replies: bool = False) -> List[Dict]`

执行手动抓取。

**参数**：
- `accounts`：账号列表
- `with_replies`：是否抓取评论区（默认 False）

**返回值**：抓取结果列表

**示例**：
```python
results = scheduler.run_manual_fetch(["karpathy", "sama"], with_replies=True)
```

##### `analyze_account(account: str) -> Dict[str, Any]`

分析账号内容。

**参数**：
- `account`：账号名

**返回值**：
```python
{
    "account": "karpathy",
    "name": "Andrej Karpathy",
    "category": "core",
    "priority": 3,
    "frequency": "medium",
    "content_type": "education",
    "tags": ["AI", "深度学习", "教育"],
    "tweets_count": 5,
    "replies_count": 10,
    "recent_tweets": [...],
    "key_topics": [...],
    "engagement": {
        "avg_likes": 65.6,
        "avg_retweets": 214.8,
        "avg_replies": 144.0
    },
    "replies_analysis": {...}
}
```

**示例**：
```python
analysis = scheduler.analyze_account("karpathy")
print(f"平均点赞: {analysis['engagement']['avg_likes']}")
```

##### `compare_accounts(accounts: List[str]) -> Dict[str, Any]`

对比多个账号。

**参数**：
- `accounts`：账号列表

**返回值**：
```python
{
    "accounts": ["karpathy", "sama"],
    "profiles": [...],
    "content_analysis": [...],
    "engagement_comparison": [...],
    "topic_overlap": {...}
}
```

**示例**：
```python
comparison = scheduler.compare_accounts(["karpathy", "sama"])
print(f"共同话题: {comparison['topic_overlap']}")
```

##### `show_profiles()`

显示账号画像。

**示例**：
```python
scheduler.show_profiles()
```

##### `update_profiles()`

更新账号画像。

**示例**：
```python
scheduler.update_profiles()
```

### LearningEngine 类

学习引擎类。

```python
from smart_scheduler.learning import LearningEngine

engine = LearningEngine()
```

#### 方法

##### `learn_from_fetch(account: str, fetch_time: datetime, has_new_content: bool, tweets_count: int, replies_count: int, engagement_score: float)`

从抓取结果学习。

**参数**：
- `account`：账号名
- `fetch_time`：抓取时间
- `has_new_content`：是否有新内容
- `tweets_count`：推文数量
- `replies_count`：评论数量
- `engagement_score`：互动分数

**示例**：
```python
from datetime import datetime

engine.learn_from_fetch(
    account="karpathy",
    fetch_time=datetime.now(),
    has_new_content=True,
    tweets_count=3,
    replies_count=15,
    engagement_score=85.5
)
```

##### `learn_from_feedback(account: str, feedback_type: str, reason: str = "")`

从用户反馈学习。

**参数**：
- `account`：账号名
- `feedback_type`：反馈类型（positive, negative, neutral）
- `reason`：原因

**示例**：
```python
engine.learn_from_feedback(
    account="karpathy",
    feedback_type="positive",
    reason="内容质量高"
)
```

##### `predict_update_pattern(account: str) -> Dict[str, Any]`

预测更新模式。

**参数**：
- `account`：账号名

**返回值**：
```python
{
    "prediction": "pattern_detected",
    "confidence": 0.85,
    "pattern": {
        "active_hours": {10: 0.8, 20: 0.9},
        "active_days": {0: 0.7, 2: 0.8},
        "confidence": 0.85
    },
    "next_update": "2026-04-30 10:00:00",
    "recommendation": "高置信度：可以按照预测时间抓取"
}
```

**示例**：
```python
prediction = engine.predict_update_pattern("karpathy")
print(f"下次更新: {prediction['next_update']}")
```

##### `recommend_accounts(target_account: str, all_accounts: List[str], top_n: int = 5) -> List[Dict[str, Any]]`

推荐相似账号。

**参数**：
- `target_account`：目标账号
- `all_accounts`：所有账号列表
- `top_n`：推荐数量

**返回值**：
```python
[
    {
        "account": "sama",
        "similarity": 0.85,
        "reason": "与 @karpathy 高度相似"
    },
    ...
]
```

**示例**：
```python
recommendations = engine.recommend_accounts(
    target_account="karpathy",
    all_accounts=["sama", "AndrewYNg", "elonmusk"],
    top_n=5
)
```

##### `select_account(accounts: List[Dict[str, Any]]) -> Dict[str, Any]`

使用 Thompson Sampling 选择账号。

**参数**：
- `accounts`：账号列表，每个账号有 success_count 和 failure_count

**返回值**：选中的账号

**示例**：
```python
accounts = [
    {'account': 'karpathy', 'success_count': 5, 'failure_count': 1},
    {'account': 'sama', 'success_count': 3, 'failure_count': 2},
]
selected = engine.select_account(accounts)
```

##### `get_optimal_action(state: int) -> int`

获取最优动作。

**参数**：
- `state`：状态（小时）

**返回值**：动作（0-4）

**示例**：
```python
action = engine.get_optimal_action(10)  # 10 点
print(f"最优动作: {action}")
```

### BayesianUpdater 类

贝叶斯更新器类。

```python
from smart_scheduler.learning import BayesianUpdater

updater = BayesianUpdater()
```

#### 方法

##### `update_probability(old_probability: float, old_count: int, new_evidence: float) -> Tuple[float, int]`

更新概率。

**参数**：
- `old_probability`：旧概率
- `old_count`：旧观测次数
- `new_evidence`：新证据（1.0 或 0.0）

**返回值**：(新概率, 新次数)

**示例**：
```python
new_probability, new_count = updater.update_probability(0.5, 10, 1.0)
```

##### `update_active_hours(account: str, hour: int, has_new_content: bool)`

更新活跃时段概率。

**参数**：
- `account`：账号名
- `hour`：小时（0-23）
- `has_new_content`：是否有新内容

**示例**：
```python
updater.update_active_hours("karpathy", 10, True)
```

##### `update_frequency(account: str, frequency_type: str)`

更新频率统计。

**参数**：
- `account`：账号名
- `frequency_type`：频率类型（daily, weekly, monthly）

**示例**：
```python
updater.update_frequency("karpathy", "daily")
```

### ThompsonSampler 类

Thompson Sampling 选择器类。

```python
from smart_scheduler.learning import ThompsonSampler

sampler = ThompsonSampler()
```

#### 方法

##### `select_account(accounts: List[Dict[str, Any]]) -> Dict[str, Any]`

选择账号。

**参数**：
- `accounts`：账号列表，每个账号有 success_count 和 failure_count

**返回值**：选中的账号

**示例**：
```python
accounts = [
    {'account': 'karpathy', 'success_count': 5, 'failure_count': 1},
    {'account': 'sama', 'success_count': 3, 'failure_count': 2},
]
selected = sampler.select_account(accounts)
```

##### `update_account_stats(account: str, success: bool)`

更新账号统计。

**参数**：
- `account`：账号名
- `success`：是否成功

**示例**：
```python
sampler.update_account_stats("karpathy", True)
```

### TimeSeriesAnalyzer 类

时间序列分析器类。

```python
from smart_scheduler.learning import TimeSeriesAnalyzer

analyzer = TimeSeriesAnalyzer()
```

#### 方法

##### `predict_update_pattern(account: str) -> Dict[str, Any]`

预测更新模式。

**参数**：
- `account`：账号名

**返回值**：
```python
{
    "prediction": "pattern_detected",
    "confidence": 0.85,
    "pattern": {...},
    "next_update": "2026-04-30 10:00:00",
    "recommendation": "高置信度：可以按照预测时间抓取"
}
```

**示例**：
```python
prediction = analyzer.predict_update_pattern("karpathy")
```

### CollaborativeFilter 类

协同过滤推荐器类。

```python
from smart_scheduler.learning import CollaborativeFilter

filter = CollaborativeFilter()
```

#### 方法

##### `recommend_accounts(target_account: str, all_accounts: List[str], top_n: int = 5) -> List[Dict[str, Any]]`

推荐相似账号。

**参数**：
- `target_account`：目标账号
- `all_accounts`：所有账号列表
- `top_n`：推荐数量

**返回值**：
```python
[
    {
        "account": "sama",
        "similarity": 0.85,
        "reason": "与 @karpathy 高度相似"
    },
    ...
]
```

**示例**：
```python
recommendations = filter.recommend_accounts(
    target_account="karpathy",
    all_accounts=["sama", "AndrewYNg", "elonmusk"],
    top_n=5
)
```

### ReinforcementLearner 类

强化学习器类。

```python
from smart_scheduler.learning import ReinforcementLearner

learner = ReinforcementLearner(states=24, actions=5)
```

#### 方法

##### `choose_action(state: int, epsilon: float = 0.1) -> int`

选择动作。

**参数**：
- `state`：状态
- `epsilon`：探索率

**返回值**：动作

**示例**：
```python
action = learner.choose_action(10, epsilon=0.1)
```

##### `learn(state: int, action: int, reward: float, next_state: int)`

学习更新 Q 表。

**参数**：
- `state`：当前状态
- `action`：动作
- `reward`：奖励
- `next_state`：下一个状态

**示例**：
```python
learner.learn(10, 2, 0.85, 11)
```

##### `get_policy() -> List[int]`

获取策略。

**返回值**：每个状态的最优动作

**示例**：
```python
policy = learner.get_policy()
print(f"策略: {policy}")
```

## 命令行接口

### 基本用法

```bash
python3 smart_scheduler.py [OPTIONS]
```

### 选项

#### `--show-profiles`

显示账号画像。

```bash
python3 smart_scheduler.py --show-profiles
```

#### `--update-profiles`

更新账号画像。

```bash
python3 smart_scheduler.py --update-profiles
```

#### `--analyze`

分析账号内容。

```bash
python3 smart_scheduler.py --analyze --accounts karpathy
```

#### `--compare`

对比博主。

```bash
python3 smart_scheduler.py --compare karpathy,sama
```

#### `--type`

指定抓取类型。

```bash
python3 smart_scheduler.py --type scheduled
python3 smart_scheduler.py --type manual --accounts karpathy,sama
python3 smart_scheduler.py --type cross_validation
```

#### `--accounts`

指定账号（逗号分隔）。

```bash
python3 smart_scheduler.py --accounts karpathy,sama,AndrewYNg
```

#### `--count`

指定抓取数量。

```bash
python3 smart_scheduler.py --count 3
```

#### `--category`

指定账号分类。

```bash
python3 smart_scheduler.py --category core
```

#### `--with-replies`

包含评论区内容。

```bash
python3 smart_scheduler.py --with-replies
```

#### `--adaptive`

自适应模式（根据学习结果决策）。

```bash
python3 smart_scheduler.py --adaptive --with-replies
```

### 示例

#### 显示账号画像

```bash
python3 smart_scheduler.py --show-profiles
```

#### 执行自适应抓取

```bash
python3 smart_scheduler.py --adaptive --with-replies
```

#### 分析账号内容

```bash
python3 smart_scheduler.py --analyze --accounts karpathy
```

#### 对比博主

```bash
python3 smart_scheduler.py --compare karpathy,sama
```

#### 手动抓取指定账号

```bash
python3 smart_scheduler.py --type manual --accounts karpathy,sama --with-replies
```

## 错误处理

### 异常类型

- `ConnectionError`：网络连接错误
- `TimeoutError`：请求超时
- `ValidationError`：数据验证错误
- `DatabaseError`：数据库错误

### 错误示例

```python
try:
    result = scheduler.fetch_account("karpathy")
except ConnectionError as e:
    print(f"网络连接错误: {e}")
except TimeoutError as e:
    print(f"请求超时: {e}")
except Exception as e:
    print(f"未知错误: {e}")
```

## 配置

### 环境变量

- `AUTOCLI_PATH`：autocli 路径
- `SMART_SCHEDULER_DB_PATH`：数据库路径
- `SMART_SCHEDULER_LOG_LEVEL`：日志级别

### 配置文件

- `config/config.yaml`：主配置文件
- `config/profiles.json`：账号画像配置

## 依赖

- Python 3.9+
- pyyaml
- numpy
- scipy
- pandas
- prophet
- statsmodels
- scikit-learn
- matplotlib
- seaborn
- requests
- tqdm

## 许可证

MIT License
