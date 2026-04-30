# 贡献指南

感谢您对 Smart Scheduler 项目的关注！我们欢迎任何形式的贡献。

## 如何贡献

### 1. 报告 Bug

如果您发现了 Bug，请通过以下方式报告：

1. 在 GitHub 上创建 Issue
2. 详细描述问题
3. 提供复现步骤
4. 提供错误日志（如果有）

### 2. 提出新功能

如果您有新功能建议，请通过以下方式提出：

1. 在 GitHub 上创建 Issue
2. 详细描述功能需求
3. 说明使用场景
4. 提供实现思路（如果有）

### 3. 提交代码

如果您想提交代码，请按照以下步骤操作：

1. Fork 项目
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 创建 Pull Request

### 代码规范

- 遵循 PEP 8 代码规范
- 添加适当的注释
- 编写单元测试
- 更新文档

### 提交信息规范

提交信息应该清晰明了，格式如下：

```
<类型>(<范围>): <描述>

<详细说明>

<关联 Issue>
```

类型包括：
- `feat`: 新功能
- `fix`: Bug 修复
- `docs`: 文档更新
- `style`: 代码格式调整
- `refactor`: 代码重构
- `test`: 测试相关
- `chore`: 构建/工具相关

示例：
```
feat(learning): 添加 Thompson Sampling 算法

实现了 Thompson Sampling 算法，用于平衡探索与利用。

Closes #123
```

## 开发环境

### 1. 克隆项目

```bash
git clone https://github.com/your-username/smart-fetcher.git
cd smart-fetcher
```

### 2. 安装依赖

```bash
./install-dependencies.sh
```

### 3. 初始化数据库

```bash
python3 scripts/init_database.py
```

### 4. 运行测试

```bash
python -m pytest tests/
```

## 项目结构

```
smart-fetcher/
├── README.md                          # 项目说明
├── LICENSE                            # MIT 许可证
├── .gitignore                         # Git 忽略文件
├── requirements.txt                   # Python 依赖
├── install-dependencies.sh            # 依赖安装脚本
├── setup.py                           # 包安装配置
├── smart_scheduler/                   # 主包
│   ├── __init__.py
│   ├── core/                          # 核心模块
│   ├── learning/                      # 学习模块
│   ├── database/                      # 数据库模块
│   └── utils/                         # 工具模块
├── scripts/                           # 脚本目录
├── config/                            # 配置目录
├── docs/                              # 文档目录
├── tests/                             # 测试目录
└── examples/                          # 示例目录
```

## 核心模块

### 1. 核心模块（core）

- `scheduler.py`: 智能调度器
- `fetcher.py`: 内容抓取器
- `analyzer.py`: 内容分析器

### 2. 学习模块（learning）

- `bayesian.py`: 贝叶斯更新算法
- `thompson.py`: Thompson Sampling 算法
- `timeseries.py`: 时间序列分析算法
- `collaborative.py`: 协同过滤算法
- `reinforcement.py`: 强化学习算法

### 3. 数据库模块（database）

- `models.py`: 数据模型定义
- `operations.py`: 数据库操作

### 4. 工具模块（utils）

- `config.py`: 配置管理
- `logger.py`: 日志管理
- `helpers.py`: 辅助函数

## 添加新算法

如果您想添加新的学习算法，请按照以下步骤操作：

1. 在 `smart_scheduler/learning/` 目录下创建新文件
2. 实现算法类
3. 在 `smart_scheduler/learning/__init__.py` 中导出
4. 在 `smart_scheduler/learning/engine.py` 中集成
5. 编写单元测试
6. 更新文档

示例：

```python
# smart_scheduler/learning/new_algorithm.py

class NewAlgorithm:
    """新算法实现"""
    
    def __init__(self):
        pass
    
    def learn(self, data):
        """学习"""
        pass
    
    def predict(self, input_data):
        """预测"""
        pass
```

## 添加新数据源

如果您想添加新的数据源，请按照以下步骤操作：

1. 在 `smart_scheduler/core/fetcher.py` 中添加新的抓取方法
2. 在 `smart_scheduler/database/models.py` 中添加新的数据模型
3. 在 `smart_scheduler/database/operations.py` 中添加新的数据库操作
4. 更新配置文件
5. 编写单元测试
6. 更新文档

## 文档规范

- 使用 Markdown 格式
- 添加代码示例
- 保持文档更新
- 使用中文或英文

## 行为准则

- 尊重他人
- 保持专业
- 接受批评
- 帮助新人

## 联系方式

如有任何问题，请通过以下方式联系我们：

- GitHub Issues
- 邮箱：your.email@example.com

感谢您的贡献！
