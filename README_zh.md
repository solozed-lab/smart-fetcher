# Smart Fetcher

[![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Stars](https://img.shields.io/github/stars/solozed-lab/smart-fetcher.svg)](https://github.com/solozed-lab/smart-fetcher)

[English](README.md)

> 像真人一样阅读社交媒体的智能抓取工具。

Smart Fetcher 会根据每个账号的发帖习惯，自动调整抓取时间、频率和策略。用得越久，越聪明。

## 为什么需要它？

- **像真人一样**：随机间隔、自然阅读节奏、不批量操作
- **自学习**：自动适应每个账号的发帖规律
- **多平台**：Twitter/X、微信公众号、小红书、B站（基于 [autocli](https://github.com/nicepkg/autocli)）
- **零配置**：开箱即用，边用边学

## 快速开始

### 前置条件

- Python 3.9+
- 已安装并配置 [autocli](https://github.com/nicepkg/autocli)

### 安装

```bash
# 克隆仓库
git clone https://github.com/solozed-lab/smart-fetcher.git
cd smart-fetcher

# 安装依赖
./install-dependencies.sh
```

### 配置

在项目根目录创建 `settings.yaml`：

```yaml
# 数据目录（绝对路径或相对路径）
# 留空则默认使用 ./data/
data_dir: ~/my-data
```

### 使用

```bash
# 查看路径配置
python3 smart_fetcher.py --show-paths

# 运行自适应模式（推荐）
python3 smart_fetcher.py --adaptive

# 运行定时模式
python3 smart_fetcher.py --type scheduled

# 查看账号画像
python3 smart_fetcher.py --show-profiles

# 更新账号画像
python3 smart_fetcher.py --update-profiles
```

## 工作原理

```
账号发帖 → Smart Fetcher 学习 → 优化调度 → 更好的内容
      ↑                                        |
      └────────────── 反馈循环 ────────────────┘
```

### 学习算法

1. **贝叶斯更新**：追踪每个账号每小时的成功率
2. **Thompson Sampling**：平衡探索与利用
3. **时间序列分析**：识别发帖规律
4. **协同过滤**：发现相似账号

### 抓取模式

| 模式 | 说明 | 使用场景 |
|------|------|----------|
| **Bootstrap** | 频繁抓取以学习规律 | 前 20 次运行 |
| **Adaptive** | 使用学习数据优化 | 日常使用 |
| **Scheduled** | 固定调度 + 智能选择 | 手动控制 |

## 目录结构

```
data/
├── config.yaml          # 配置文件
├── accounts.json        # 账号画像
├── learning.db          # 学习数据库
├── logs/                # 系统运行日志
│   ├── scheduler.log   # 主日志（调度决策、学习算法）
│   ├── fetch.log       # 抓取日志（每次抓取的详细记录）
│   ├── error.log       # 错误日志（异常和错误）
│   └── archive/        # 归档目录（7天以上的日志）
├── fetch-logs/          # 抓取统计（JSON格式）
│   └── YYYY-MM-DD.json
└── content/             # 抓取内容
    └── x/               # Twitter/X 平台
        └── YYYY-MM-DD/  # 按日期分目录
            ├── summary.md
            └── <handle>.md
```

### 日志说明

| 日志类型 | 文件 | 内容 | 用途 |
|---------|------|------|------|
| 系统运行日志 | `logs/scheduler.log` | 调度决策、学习算法、账号选择 | 调试系统逻辑 |
| 抓取日志 | `logs/fetch.log` | 每次抓取的详细结果 | 监控抓取状态 |
| 错误日志 | `logs/error.log` | 异常和错误信息 | 排查问题 |
| 抓取统计 | `fetch-logs/*.json` | 每日抓取汇总 | 统计分析 |

### 日志清理策略

```bash
# 查看日志统计（预览模式）
python3 cleanup-logs.py --dry-run

# 执行清理
python3 cleanup-logs.py
```

清理规则：
- 3天内：保留原始日志
- 3-7天：压缩为 `.gz`
- 7-30天：移到 `archive/` 目录
- 30天以上：删除

## 配置说明

### 路径优先级

1. `--data-dir` 命令行参数
2. `SMART_FETCHER_DATA_DIR` 环境变量
3. `settings.yaml` 配置文件
4. `./data/` 目录（默认）

### 环境变量

```bash
# 自定义数据目录
export SMART_FETCHER_DATA_DIR=/path/to/data

# autocli 路径（如果不在 PATH 中）
export AUTOCLI_PATH=/usr/local/bin/autocli
```

## 定时任务

使用 cron 实现自动化调度：

```bash
# 每小时自适应抓取
0 * * * * cd /path/to/smart-fetcher && python3 smart_fetcher.py --adaptive

# 每天 22:00 生成日报
0 22 * * * cd /path/to/smart-fetcher && python3 daily_summary.py

# 每周日交叉验证
0 22 * * 0 cd /path/to/smart-fetcher && python3 cross_validation.py

# 每天 02:00 清理日志
0 2 * * * cd /path/to/smart-fetcher && python3 cleanup_logs.py
```

## 路线图

- [x] v0.2 - Twitter/X 支持 + 自学习
- [ ] v0.3 - 微信公众号支持
- [ ] v0.4 - 小红书支持
- [ ] v0.5 - B站支持
- [ ] v1.0 - Web UI 内容浏览
- [ ] v1.1 - AI 内容摘要

## 参与贡献

欢迎贡献！请先阅读 [贡献指南](CONTRIBUTING.md)。

## 开源协议

本项目基于 MIT 协议开源 - 详见 [LICENSE](LICENSE) 文件。

## 致谢

- [autocli](https://github.com/nicepkg/autocli) - 多平台 CLI 工具
- [loguru](https://github.com/Delgan/loguru) - Python 日志库

## 联系方式

- GitHub: [@solozed-lab](https://github.com/solozed-lab)
- 邮箱: i@solozed.com
- 官网: [solozed.com](https://solozed.com)
