# Smart Scheduler — 智能抓取调度系统

> 🤖 根据账号习惯动态调整抓取时间，像真人一样刷推特

[![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Stars](https://img.shields.io/github/stars/your-username/smart-scheduler.svg)](https://github.com/your-username/smart-scheduler)

---

## ✨ 特性

- 🧠 **自学习**：根据抓取结果自动优化抓取策略
- ⏰ **动态调度**：根据账号活跃时段动态调整抓取时间
- 📊 **智能分析**：分析推文内容、互动数据、评论区
- 🔄 **自适应**：根据内容密度动态调整抓取数量和间隔
- 🎯 **精准推荐**：通过交叉验证发现新的值得关注的账号

---

## 🚀 快速开始

### 安装

```bash
# 克隆仓库
git clone https://github.com/your-username/smart-scheduler.git
cd smart-scheduler

# 安装依赖
./install-dependencies.sh

# 或者手动安装
pip install -r requirements.txt
```

### 初始化

```bash
# 初始化数据库
python3 init_database.py

# 初始化账号画像
python3 init_profiles.py
```

### 使用

```bash
# 显示账号画像
python3 smart_scheduler.py --show-profiles

# 执行一次智能抓取
python3 smart_scheduler.py --adaptive --with-replies

# 分析账号内容
python3 smart_scheduler.py --analyze --accounts karpathy

# 对比博主
python3 smart_scheduler.py --compare karpathy,AndrewYNg

# 手动抓取指定账号
python3 smart_scheduler.py --type manual --accounts karpathy,sama --with-replies
```

---

## 📁 项目结构

```
smart-scheduler/
├── README.md                          # 项目说明
├── LICENSE                            # MIT 许可证
├── .gitignore                         # Git 忽略文件
├── requirements.txt                   # Python 依赖
├── install-dependencies.sh            # 依赖安装脚本
├── setup.py                           # 包安装配置
├── smart_scheduler/                   # 主包
│   ├── __init__.py
│   ├── core/                          # 核心模块
│   │   ├── __init__.py
│   │   ├── scheduler.py               # 智能调度器
│   │   ├── fetcher.py                 # 内容抓取器
│   │   └── analyzer.py                # 内容分析器
│   ├── learning/                      # 学习模块
│   │   ├── __init__.py
│   │   ├── bayesian.py                # 贝叶斯更新
│   │   ├── thompson.py                # Thompson Sampling
│   │   ├── timeseries.py              # 时间序列分析
│   │   ├── collaborative.py           # 协同过滤
│   │   └── reinforcement.py           # 强化学习
│   ├── database/                      # 数据库模块
│   │   ├── __init__.py
│   │   ├── models.py                  # 数据模型
│   │   └── operations.py              # 数据库操作
│   └── utils/                         # 工具模块
│       ├── __init__.py
│       ├── config.py                  # 配置管理
│       ├── logger.py                  # 日志管理
│       └── helpers.py                 # 辅助函数
├── scripts/                           # 脚本目录
│   ├── init_database.py               # 数据库初始化
│   ├── init_profiles.py               # 账号画像初始化
│   ├── daily_summary.py               # 每日汇总
│   ├── cross_validation.py            # 交叉验证
│   └── validate_cn_influencers.py     # 中文大佬验证
├── config/                            # 配置目录
│   ├── config.yaml                    # 主配置文件
│   └── profiles.json                  # 账号画像配置
├── docs/                              # 文档目录
│   ├── architecture.md                # 架构设计
│   ├── algorithms.md                  # 算法说明
│   ├── database.md                    # 数据库设计
│   └── api.md                         # API 文档
├── tests/                             # 测试目录
│   ├── __init__.py
│   ├── test_scheduler.py              # 调度器测试
│   ├── test_learning.py               # 学习算法测试
│   └── test_database.py               # 数据库测试
└── examples/                          # 示例目录
    ├── basic_usage.py                 # 基本用法
    ├── advanced_usage.py              # 高级用法
    └── custom_algorithm.py            # 自定义算法
```

---

## 🧠 自学习算法

### 1. 贝叶斯更新（Bayesian Update）

**用途**：估计账号在某个时段有新内容的概率

**算法**：
```
P(有新内容|时段) = (旧概率 × 旧次数 + 新证据) / (旧次数 + 1)
```

**应用场景**：
- 活跃时段概率估计
- 更新频率概率估计
- 内容质量概率估计

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

**应用场景**：
- 选择抓取哪个账号
- 平衡探索新账号和利用已知高质量账号
- 自适应调整抓取策略

### 3. 时间序列分析（Time Series Analysis）

**用途**：预测账号的更新时间和频率

**算法**：使用 Prophet 或 ARIMA 模型

**应用场景**：
- 预测账号的更新时间
- 识别更新周期（每天、每周、每月）
- 预测内容密度

### 4. 协同过滤（Collaborative Filtering）

**用途**：发现与你关注的账号相似的新账号

**算法**：使用基于用户的协同过滤

**应用场景**：
- 推荐相似账号
- 发现新账号
- 扩展关注列表

### 5. 强化学习（Reinforcement Learning）

**用途**：最大化长期收益（获取高质量内容）

**算法**：使用 Q-Learning 或 Policy Gradient

**应用场景**：
- 动态调整抓取策略
- 最大化长期收益
- 自适应学习

---

## 📊 数据结构

### 账号画像（account-profiles.json）

```json
{
  "version": "1.0",
  "last_updated": "2026-04-29T22:30:00",
  "accounts": {
    "karpathy": {
      "name": "Andrej Karpathy",
      "handle": "karpathy",
      "category": "core",
      "priority": 3,
      "frequency": "medium",
      "active_hours": [10, 11, 20, 21],
      "content_type": "education",
      "last_updated": "2026-04-29T22:15:00",
      "update_pattern": "每周 2-3 条，晚上居多",
      "interaction": "high",
      "status": "active",
      "tags": ["AI", "深度学习", "教育"]
    }
  }
}
```

### 学习数据库（learning.db）

**表结构**：

```sql
-- 抓取历史表
CREATE TABLE fetch_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    account TEXT NOT NULL,
    fetch_time TIMESTAMP NOT NULL,
    has_new_content BOOLEAN,
    tweets_count INTEGER DEFAULT 0,
    replies_count INTEGER DEFAULT 0,
    engagement_score FLOAT DEFAULT 0.0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 用户反馈表
CREATE TABLE user_feedback (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    account TEXT NOT NULL,
    feedback_type TEXT NOT NULL,
    feedback_time TIMESTAMP NOT NULL,
    reason TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 活跃时段统计表
CREATE TABLE active_hours_stats (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    account TEXT NOT NULL,
    hour INTEGER NOT NULL,
    fetch_count INTEGER DEFAULT 0,
    new_content_count INTEGER DEFAULT 0,
    probability FLOAT DEFAULT 0.0,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(account, hour)
);

-- 更新频率统计表
CREATE TABLE update_frequency_stats (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    account TEXT NOT NULL,
    frequency_type TEXT NOT NULL,
    observed_count INTEGER DEFAULT 0,
    probability FLOAT DEFAULT 0.0,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(account, frequency_type)
);

-- 调度策略表
CREATE TABLE schedule_strategy (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    strategy_name TEXT NOT NULL,
    strategy_value TEXT NOT NULL,
    success_count INTEGER DEFAULT 0,
    failure_count INTEGER DEFAULT 0,
    success_rate FLOAT DEFAULT 0.0,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(strategy_name, strategy_value)
);

-- 账号画像表
CREATE TABLE account_profiles (
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
);
```

### 配置文件（config.yaml）

```yaml
scheduler:
  behavior:
    min_interval_minutes: 10
    max_accounts_per_fetch: 5
    random_delay_seconds: [30, 120]
  
  time_weights:
    0: 0.1
    1: 0.1
    # ... 24小时权重
  
  priority_weights:
    3: 1.0
    2: 0.7
    1: 0.4

learning:
  enabled: true
  profile_update_frequency: "daily"
  
  priority_adjustment:
    positive_threshold: 3
    negative_threshold: 3
  
  frequency_adjustment:
    high_frequency_threshold: 5
    low_frequency_threshold: 7

output:
  daily_summary_time: "22:00"
  weekly_cross_validation_day: "sunday"
  log_retention_days: 30
```

---

## 📁 路径配置

### 优先级（从高到低）

1. `--data-dir` 命令行参数
2. `SMART_SCHEDULER_DATA_DIR` 环境变量
3. `settings.yaml` 配置文件
4. 项目根目录下的 `data/`（默认）

### settings.yaml 配置文件（推荐）

在项目根目录创建 `settings.yaml`：

```yaml
# 数据目录（绝对路径或相对路径）
data_dir: ~/AI/hermes/input/learn
```

### 目录结构

```
data_dir/
├── config.yaml        # 主配置文件
├── accounts.json      # 账号画像
├── learning.db        # 学习数据库
├── logs/              # 日志目录
├── fetch-logs/        # 抓取日志
└── content/           # 抓取内容
```

### 命令行参数

```bash
# 指定数据目录
python3 smart_scheduler.py --data-dir /path/to/data

# 查看当前路径配置
python3 smart_scheduler.py --show-paths
```

### 环境变量

```bash
export SMART_SCHEDULER_DATA_DIR=/path/to/data
python3 smart_scheduler.py
```

---

## 📝 日志系统

### 日志目录结构

```
logs/
├── scheduler.log          # 主日志（DEBUG 级别）
├── error.log              # 错误日志（ERROR 级别）
├── fetch.log              # 抓取日志（INFO 级别）
└── archive/               # 归档目录
    └── *.log.gz           # 压缩的旧日志
```

### 日志清理规范

| 时间范围 | 操作 | 说明 |
|---------|------|------|
| 0-3 天 | 保留原始日志 | 实时查看和调试 |
| 3-7 天 | 压缩为 `.gz` | 节省存储空间 |
| 7-30 天 | 移到 `archive/` | 归档保存 |
| 30 天以上 | 自动删除 | 清理过期日志 |

### 日志级别

- **DEBUG**：详细的调试信息
- **INFO**：一般信息（抓取成功、状态变更）
- **WARNING**：警告信息（非致命错误）
- **ERROR**：错误信息（抓取失败、配置错误）

### 使用方法

```python
from logger import logger, log_manager

# 记录日志
logger.info("这是一条信息")
logger.error("这是一条错误")

# 清理日志
stats = log_manager.cleanup_logs()
print(stats)

# 获取统计
stats = log_manager.get_log_stats()
print(stats)
```

### 定时清理

系统会自动在每天凌晨 2 点执行日志清理：

```bash
# 手动清理
python3 cleanup-logs.py

# 查看清理效果
python3 cleanup-logs.py --dry-run
```

---

## 🔧 配置说明

### 环境变量

```bash
# 可选：设置 autocli 路径
export AUTOCLI_PATH=/usr/local/bin/autocli

# 可选：设置数据库路径
export SMART_SCHEDULER_DB_PATH=/path/to/learning.db

# 可选：设置日志级别
export SMART_SCHEDULER_LOG_LEVEL=INFO
```

### 配置文件

主要配置文件位于 `config/config.yaml`，包含：

- **scheduler**: 调度行为配置
- **learning**: 学习算法配置
- **output**: 输出配置

---

## 📈 使用示例

### 基本用法

```python
from smart_scheduler import SmartScheduler

# 创建调度器
scheduler = SmartScheduler()

# 显示账号画像
scheduler.show_profiles()

# 执行一次智能抓取
scheduler.run_adaptive_fetch(with_replies=True)

# 分析账号内容
analysis = scheduler.analyze_account("karpathy")
print(analysis)
```

### 高级用法

```python
from smart_scheduler import SmartScheduler
from smart_scheduler.learning import LearningEngine

# 创建学习引擎
engine = LearningEngine()

# 从抓取结果学习
engine.learn_from_fetch(
    account="karpathy",
    fetch_time=datetime.now(),
    has_new_content=True,
    tweets_count=3,
    replies_count=15,
    engagement_score=85.5
)

# 预测更新模式
prediction = engine.predict_update_pattern("karpathy")
print(prediction)

# 推荐相似账号
recommendations = engine.recommend_accounts(
    target_account="karpathy",
    all_accounts=["sama", "AndrewYNg", "elonmusk"],
    top_n=5
)
print(recommendations)
```

### 自定义算法

```python
from smart_scheduler.learning import BayesianUpdater, ThompsonSampler

# 创建贝叶斯更新器
updater = BayesianUpdater()

# 更新概率
new_probability, new_count = updater.update_probability(
    old_probability=0.5,
    old_count=10,
    new_evidence=1.0
)

# 创建 Thompson Sampling 选择器
sampler = ThompsonSampler()

# 选择账号
accounts = [
    {'account': 'karpathy', 'success_count': 5, 'failure_count': 1},
    {'account': 'sama', 'success_count': 3, 'failure_count': 2},
]
selected = sampler.select_account(accounts)
```

---

## 🗺️ Roadmap

### 当前版本 (v1.0)

**Twitter 专用版** - 已完成 ✅

- ✅ 智能抓取调度
- ✅ 自学习算法（贝叶斯更新、Thompson Sampling、时间序列分析、协同过滤、强化学习）
- ✅ 内容分析（推文、评论区、互动数据）
- ✅ 动态调整（抓取时间、数量、间隔）
- ✅ 数据库存储（SQLite）

### 后续版本

#### v1.1 - 多平台支持

**目标**：支持更多社交媒体平台

```
smart-scheduler/
├── platforms/                  # 平台适配层
│   ├── __init__.py
│   ├── base.py                 # 平台适配器基类
│   ├── twitter.py              # Twitter 适配器（已完成）
│   ├── weibo.py                # 微博适配器
│   ├── xiaohongshu.py          # 小红书适配器
│   ├── bilibili.py             # B站适配器
│   └── wechat.py               # 微信公众号适配器
├── learning_algorithms.py      # 通用学习算法
└── ...
```

**平台适配器接口**：

```python
class PlatformAdapter:
    """平台适配器基类"""
    
    def fetch_account(self, account: str) -> Dict[str, Any]:
        """抓取账号内容"""
        raise NotImplementedError
    
    def fetch_replies(self, content_id: str) -> List[Dict[str, Any]]:
        """抓取评论区"""
        raise NotImplementedError
    
    def search_accounts(self, query: str) -> List[Dict[str, Any]]:
        """搜索账号"""
        raise NotImplementedError
    
    def get_account_info(self, account: str) -> Dict[str, Any]:
        """获取账号信息"""
        raise NotImplementedError
```

**扩展计划**：

| 阶段 | 平台 | 优先级 | 说明 |
|------|------|--------|------|
| **v1.0** | Twitter | ✅ 已完成 | 当前版本 |
| **v1.1** | 微博 | 高 | 中文内容主要来源 |
| **v1.2** | 小红书 | 中 | 生活方式内容 |
| **v1.3** | B站 | 中 | 视频内容 |
| **v1.4** | 微信公众号 | 低 | 深度文章 |

#### v1.2 - 统一仪表盘

**目标**：提供统一的 Web 界面管理所有平台

- 📊 数据可视化：抓取统计、学习进度、账号分析
- 🎛️ 配置管理：账号管理、调度配置、学习参数
- 📱 移动端支持：响应式设计，支持手机访问

#### v1.3 - 智能推荐

**目标**：基于用户兴趣的智能内容推荐

- 🎯 兴趣建模：分析用户阅读行为，建立兴趣模型
- 📈 内容推荐：基于兴趣模型推荐相关内容
- 🔍 跨平台发现：发现跨平台的相似内容

#### v2.0 - 社交图谱

**目标**：构建社交关系图谱

- 🕸️ 关系图谱：分析账号之间的关注、互动关系
- 👥 社群发现：发现兴趣社群和意见领袖
- 📊 影响力分析：评估账号的影响力和传播力

### 架构演进

```
v1.0 (当前)          v1.1 (多平台)         v2.0 (社交图谱)
    │                    │                    │
    ▼                    ▼                    ▼
┌─────────┐         ┌─────────┐         ┌─────────┐
│ Twitter │         │ 平台层  │         │ 社交层  │
│  专用   │         │ (多平台)│         │ (图谱)  │
└─────────┘         └─────────┘         └─────────┘
    │                    │                    │
    ▼                    ▼                    ▼
┌─────────┐         ┌─────────┐         ┌─────────┐
│ 学习层  │         │ 学习层  │         │ 学习层  │
│ (单平台)│         │ (跨平台)│         │ (图谱)  │
└─────────┘         └─────────┘         └─────────┘
    │                    │                    │
    ▼                    ▼                    ▼
┌─────────┐         ┌─────────┐         ┌─────────┐
│ 数据层  │         │ 数据层  │         │ 数据层  │
│ (SQLite)│         │ (Postgres)│       │ (Neo4j) │
└─────────┘         └─────────┘         └─────────┘
```

### 技术栈演进

| 版本 | 前端 | 后端 | 数据库 | 部署 |
|------|------|------|--------|------|
| v1.0 | CLI | Python | SQLite | 本地 |
| v1.1 | CLI | Python | SQLite | 本地 |
| v1.2 | React | FastAPI | PostgreSQL | Docker |
| v1.3 | React | FastAPI | PostgreSQL | Docker |
| v2.0 | React | FastAPI | PostgreSQL + Neo4j | K8s |

### 贡献指南

如果你想参与开发：

1. **v1.1 - 多平台支持**：实现新的平台适配器
2. **v1.2 - 统一仪表盘**：开发 Web 前端
3. **v1.3 - 智能推荐**：优化推荐算法
4. **v2.0 - 社交图谱**：设计图谱模型

欢迎提交 Issue 和 Pull Request！

---

## 🧪 测试

```bash
# 运行所有测试
python -m pytest tests/

# 运行特定测试
python -m pytest tests/test_scheduler.py

# 运行测试并生成覆盖率报告
python -m pytest tests/ --cov=smart_scheduler --cov-report=html
```

---

## 📦 打包发布

```bash
# 安装打包工具
pip install setuptools wheel twine

# 打包
python setup.py sdist bdist_wheel

# 上传到 PyPI
twine upload dist/*
```

---

## 🤝 贡献

欢迎贡献！请阅读 [CONTRIBUTING.md](CONTRIBUTING.md) 了解详情。

### 贡献方式

1. Fork 项目
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 创建 Pull Request

---

## 📄 许可证

本项目采用 MIT 许可证 - 详情请阅 [LICENSE](LICENSE)

---

## 🙏 致谢

- [AutoCLI](https://github.com/nashsu/AutoCLI) - 用于抓取 Twitter 数据
- [Prophet](https://facebook.github.io/prophet/) - 用于时间序列分析
- [NumPy](https://numpy.org/) - 用于数值计算
- [SciPy](https://scipy.org/) - 用于科学计算
- [scikit-learn](https://scikit-learn.org/) - 用于机器学习

---

## 📧 联系方式

- 作者：Your Name
- 邮箱：your.email@example.com
- GitHub：[@your-username](https://github.com/your-username)

---

## 🔗 相关项目

- [AutoCLI](https://github.com/nashsu/AutoCLI) - 自动化 CLI 工具
- [LLM Wiki](https://github.com/karpathy/llm-wiki) - LLM 知识管理
- [Smart Scheduler](https://github.com/your-username/smart-scheduler) - 本项目

---

*本项目由 AI 与人类共同开发，欢迎 Star 和 Fork！*
