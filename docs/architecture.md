# 架构设计

## 项目概述

Smart Scheduler 是一个智能抓取调度系统，用于根据账号习惯动态调整抓取时间，像真人一样刷推特。

## 核心设计原则

1. **自学习**：系统能够根据抓取结果自动优化抓取策略
2. **动态调度**：系统能够根据账号活跃时段动态调整抓取时间
3. **智能分析**：系统能够分析推文内容、互动数据、评论区
4. **自适应**：系统能够根据内容密度动态调整抓取数量和间隔
5. **精准推荐**：系统能够通过交叉验证发现新的值得关注的账号

## 系统架构

```
┌─────────────────────────────────────────────────────────────┐
│                      Smart Scheduler                        │
├─────────────────────────────────────────────────────────────┤
│                      核心层 (Core)                          │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐        │
│  │  Scheduler  │  │   Fetcher   │  │  Analyzer   │        │
│  │  (调度器)   │  │  (抓取器)   │  │  (分析器)   │        │
│  └─────────────┘  └─────────────┘  └─────────────┘        │
├─────────────────────────────────────────────────────────────┤
│                      学习层 (Learning)                      │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐        │
│  │  Bayesian   │  │  Thompson   │  │ TimeSeries  │        │
│  │  (贝叶斯)   │  │ (汤普森)    │  │  (时间序列) │        │
│  └─────────────┘  └─────────────┘  └─────────────┘        │
│  ┌─────────────┐  ┌─────────────┐                         │
│  │Collaborative│  │Reinforcement│                         │
│  │  (协同过滤) │  │  (强化学习) │                         │
│  └─────────────┘  └─────────────┘                         │
├─────────────────────────────────────────────────────────────┤
│                      数据层 (Database)                      │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐        │
│  │   Models    │  │ Operations  │  │   Schema    │        │
│  │  (数据模型) │  │  (数据库操作)│  │  (数据库结构)│        │
│  └─────────────┘  └─────────────┘  └─────────────┘        │
├─────────────────────────────────────────────────────────────┤
│                      工具层 (Utils)                         │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐        │
│  │   Config    │  │   Logger    │  │   Helpers   │        │
│  │  (配置管理) │  │  (日志管理) │  │  (辅助函数) │        │
│  └─────────────┘  └─────────────┘  └─────────────┘        │
└─────────────────────────────────────────────────────────────┘
```

## 数据流

```
外部数据源 (Twitter)
    ↓
抓取器 (Fetcher)
    ↓
分析器 (Analyzer)
    ↓
学习引擎 (Learning Engine)
    ↓
数据库 (Database)
    ↓
调度器 (Scheduler)
    ↓
执行抓取
```

## 核心模块

### 1. 调度器 (Scheduler)

**职责**：
- 根据学习结果动态决定是否执行
- 根据学习结果动态调整抓取数量
- 根据学习结果动态调整抓取间隔
- 选择要抓取的账号

**接口**：
```python
class SmartScheduler:
    def should_execute_now() -> bool
    def get_adaptive_count() -> int
    def get_adaptive_interval() -> int
    def select_accounts(count: int) -> List[str]
    def run_adaptive_fetch(with_replies: bool) -> List[Dict]
```

### 2. 抓取器 (Fetcher)

**职责**：
- 从 Twitter 抓取推文
- 从 Twitter 抓取评论区
- 从 Twitter 抓取账号信息

**接口**：
```python
class TwitterFetcher:
    def fetch_tweets(account: str, limit: int) -> List[Dict]
    def fetch_replies(tweet_id: str, limit: int) -> List[Dict]
    def fetch_profile(account: str) -> Dict
```

### 3. 分析器 (Analyzer)

**职责**：
- 分析推文内容
- 分析互动数据
- 分析评论区内容
- 生成分析报告

**接口**：
```python
class ContentAnalyzer:
    def analyze_tweets(tweets: List[Dict]) -> Dict
    def analyze_engagement(tweets: List[Dict]) -> Dict
    def analyze_replies(replies: List[Dict]) -> Dict
    def generate_report(analysis: Dict) -> str
```

### 4. 学习引擎 (Learning Engine)

**职责**：
- 整合所有学习算法
- 从抓取结果学习
- 从用户反馈学习
- 预测更新模式
- 推荐相似账号

**接口**：
```python
class LearningEngine:
    def learn_from_fetch(account, fetch_time, has_new_content, ...)
    def learn_from_feedback(account, feedback_type, reason)
    def predict_update_pattern(account) -> Dict
    def recommend_accounts(target_account, all_accounts, top_n) -> List[Dict]
    def select_account(accounts) -> Dict
    def get_optimal_action(state) -> int
```

## 学习算法

### 1. 贝叶斯更新 (Bayesian Update)

**用途**：估计账号在某个时段有新内容的概率

**算法**：
```
P(有新内容|时段) = (旧概率 × 旧次数 + 新证据) / (旧次数 + 1)
```

**数据结构**：
```python
{
    "account": "karpathy",
    "hour": 10,
    "fetch_count": 5,
    "new_content_count": 4,
    "probability": 0.8
}
```

### 2. Thompson Sampling

**用途**：选择哪个账号抓取（平衡探索新账号和利用已知高质量账号）

**算法**：
```
1. 为每个账号维护一个 Beta 分布 Beta(α, β)
2. α = 成功次数 + 1
3. β = 失败次数 + 1
4. 从每个账号的 Beta 分布中采样
5. 选择采样值最高的账号
```

**数据结构**：
```python
{
    "account": "karpathy",
    "success_count": 5,
    "failure_count": 1,
    "alpha": 6,
    "beta": 2
}
```

### 3. 时间序列分析 (Time Series Analysis)

**用途**：预测账号的更新时间和频率

**算法**：使用 Prophet 或 ARIMA 模型

**数据结构**：
```python
{
    "account": "karpathy",
    "history": [
        {"time": "2026-04-29 10:15:00", "has_new": True},
        {"time": "2026-04-29 20:30:00", "has_new": True},
        ...
    ],
    "prediction": {
        "next_update": "2026-04-30 10:00:00",
        "confidence": 0.85
    }
}
```

### 4. 协同过滤 (Collaborative Filtering)

**用途**：发现与你关注的账号相似的新账号

**算法**：使用基于用户的协同过滤

**数据结构**：
```python
{
    "target_account": "karpathy",
    "similar_accounts": [
        {"account": "sama", "similarity": 0.85},
        {"account": "AndrewYNg", "similarity": 0.78},
        ...
    ]
}
```

### 5. 强化学习 (Reinforcement Learning)

**用途**：最大化长期收益（获取高质量内容）

**算法**：使用 Q-Learning 或 Policy Gradient

**数据结构**：
```python
{
    "states": 24,  # 24小时
    "actions": 5,  # 5种抓取策略
    "q_table": [[0.0, ...], ...],
    "learning_rate": 0.1,
    "discount_factor": 0.95
}
```

## 数据库设计

### 表结构

1. **fetch_history**: 抓取历史表
2. **user_feedback**: 用户反馈表
3. **active_hours_stats**: 活跃时段统计表
4. **update_frequency_stats**: 更新频率统计表
5. **schedule_strategy**: 调度策略表
6. **account_profiles**: 账号画像表

### 索引

- `idx_fetch_history_account`: 账号索引
- `idx_fetch_history_time`: 时间索引
- `idx_user_feedback_account`: 账号索引
- `idx_active_hours_account`: 账号索引
- `idx_update_frequency_account`: 账号索引

## 配置管理

### 配置文件

- `config.yaml`: 主配置文件
- `profiles.json`: 账号画像配置

### 配置项

- `scheduler`: 调度行为配置
- `learning`: 学习算法配置
- `output`: 输出配置

## 日志管理

### 日志级别

- `DEBUG`: 调试信息
- `INFO`: 一般信息
- `WARNING`: 警告信息
- `ERROR`: 错误信息
- `CRITICAL`: 严重错误信息

### 日志格式

```
%(asctime)s - %(name)s - %(levelname)s - %(message)s
```

## 扩展性

### 添加新算法

1. 在 `smart_scheduler/learning/` 目录下创建新文件
2. 实现算法类
3. 在 `smart_scheduler/learning/__init__.py` 中导出
4. 在 `smart_scheduler/learning/engine.py` 中集成

### 添加新数据源

1. 在 `smart_scheduler/core/fetcher.py` 中添加新的抓取方法
2. 在 `smart_scheduler/database/models.py` 中添加新的数据模型
3. 在 `smart_scheduler/database/operations.py` 中添加新的数据库操作

## 性能优化

### 数据库优化

- 使用索引加速查询
- 使用连接池减少连接开销
- 使用批量操作减少数据库交互

### 算法优化

- 使用缓存减少重复计算
- 使用异步操作提高并发性能
- 使用批量处理减少 I/O 开销

## 安全性

### 数据安全

- 使用加密存储敏感数据
- 使用访问控制限制数据访问
- 使用备份机制防止数据丢失

### 接口安全

- 使用认证机制限制接口访问
- 使用限流机制防止滥用
- 使用输入验证防止注入攻击

## 监控

### 性能监控

- 监控抓取成功率
- 监控学习算法收敛速度
- 监控系统资源使用情况

### 业务监控

- 监控账号活跃度变化
- 监控内容质量变化
- 监控用户反馈变化
