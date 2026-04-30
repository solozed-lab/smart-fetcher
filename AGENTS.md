# AGENTS.md — smart-fetcher/

智能抓取调度系统 — 根据账号习惯动态调整抓取时间。

## 核心理念

> 不是「我几点抓取」，而是「这个账号什么时候更新，我就什么时候去看」。

## 文件结构

```
smart-fetcher/
├── README.md              # 使用说明（英文）
├── README_zh.md           # 使用说明（中文）
├── AGENTS.md              # 本文件
├── DECISIONS.md           # 开发决策记录
├── CONTRIBUTING.md        # 贡献指南
├── LICENSE                # MIT 许可证
├── smart_scheduler.py     # 主脚本
├── scheduler-core.py      # 调度核心逻辑
├── learning_algorithms.py # 学习算法模块
├── paths.py               # 路径配置模块
├── logger.py              # 日志系统
├── cleanup-logs.py        # 日志清理脚本
├── daily_summary.py       # 每日汇总
├── cross_validation.py    # 交叉验证
├── validate_cn_influencers.py # 中文大佬验证
├── init-database.py       # 数据库初始化
├── test-all.py            # 测试脚本
├── install-dependencies.sh # 依赖安装
├── setup.py               # 项目打包配置
├── settings.yaml          # 数据目录配置
└── docs/                  # 文档目录
    ├── architecture.md
    ├── algorithms.md
    ├── database.md
    └── api.md
```

## 使用规则

### 1. 手动触发

```bash
# 执行一次智能抓取
python3 smart_scheduler.py

# 自适应模式（推荐）
python3 smart_scheduler.py --adaptive

# 指定抓取类型
python3 smart_scheduler.py --type scheduled
python3 smart_scheduler.py --type manual

# 指定账号
python3 smart_scheduler.py --accounts karpathy,AndrewYNg

# 查看账号画像
python3 smart_scheduler.py --show-profiles

# 更新账号画像
python3 smart_scheduler.py --update-profiles

# 查看路径配置
python3 smart_scheduler.py --show-paths
```

### 2. Cron Job 触发

```bash
# 每小时自适应抓取
0 * * * * cd /Users/yun-z/AI/hermes/programs/smart-fetcher && python3 smart_scheduler.py --adaptive

# 每天 22:00 生成日报
0 22 * * * cd /Users/yun-z/AI/hermes/programs/smart-fetcher && python3 daily_summary.py

# 每周日 22:00 交叉验证
0 22 * * 0 cd /Users/yun-z/AI/hermes/programs/smart-fetcher && python3 cross_validation.py

# 每天 02:00 清理日志
0 2 * * * cd /Users/yun-z/AI/hermes/programs/smart-fetcher && python3 cleanup-logs.py
```

## 调度逻辑

### 1. 时段选择

根据 `config.yaml` 中的 `time_weights` 和当前时间，计算当前时段的权重。

### 2. 账号选择

根据以下因素计算账号的抓取优先级：
- **优先级权重**：核心大佬 > 重要账号 > 关注账号
- **更新频率**：高频账号 > 低频账号
- **最后更新时间**：长时间未更新的账号优先
- **活跃时段**：当前时间是否在账号的活跃时段内

### 3. 抓取执行

- 每次抓取 3-5 个账号
- 账号之间间隔 10-15 分钟
- 有随机延迟（30-120 秒）

## 自学习机制

### 1. 更新频率学习

观察账号的实际更新频率，调整画像中的 `frequency` 字段。

### 2. 活跃时段学习

观察账号的实际更新时间，调整画像中的 `active_hours` 字段。

### 3. 优先级学习

根据用户的标注（「值得进 brain/」/「不感兴趣」），调整优先级。

## 输出

### 1. 抓取结果

- 存入 `~/AI/hermes/input/learn/content/x/YYYY-MM-DD/` 目录
- 每个账号一个 Markdown 文件（如 `karpathy.md`）
- 生成每日汇总 `summary.md`

### 2. 抓取日志

- 系统运行日志：`~/AI/hermes/input/learn/logs/scheduler.log`
- 抓取详细日志：`~/AI/hermes/input/learn/logs/fetch.log`
- 错误日志：`~/AI/hermes/input/learn/logs/error.log`
- 抓取统计：`~/AI/hermes/input/learn/fetch-logs/YYYY-MM-DD.json`

### 3. 学习数据

- SQLite 数据库：`~/AI/hermes/input/learn/learning.db`
- 账号画像：`~/AI/hermes/input/learn/account-profiles.json`
- 配置文件：`~/AI/hermes/input/learn/config.yaml`

### 4. 日志清理

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

## 配置

### 路径配置

数据目录优先级（从高到低）：
1. `--data-dir` 命令行参数
2. `SMART_SCHEDULER_DATA_DIR` 环境变量
3. `settings.yaml` 配置文件
4. 项目根目录下的 `data/`（默认）

### 配置文件

- `settings.yaml`：数据目录配置
- `config.yaml`：调度行为配置（在数据目录中）
- `accounts.json`：账号画像（在数据目录中）

主要配置项：
- `scheduler.behavior`：抓取行为配置
- `scheduler.time_weights`：时段权重配置
- `scheduler.priority_weights`：优先级权重配置
- `learning`：自学习配置
- `output`：输出配置

## 注意事项

1. **不要批量抓取**：每次抓取间隔 10-15 分钟，像真人行为
2. **不要固定时间**：根据账号习惯动态调整
3. **不要过度抓取**：每次 3-5 个账号，不要贪多
4. **保持人性化**：有随机性，不要完全规律化

## 操作日志

| 时间 | 操作 | 结果 |
|------|------|------|
| 2026-04-29 22:30 | 创建目录结构 | 完成 |
| 2026-04-29 22:31 | 创建 README.md | 完成 |
| 2026-04-29 22:32 | 创建 AGENTS.md | 完成 |
| 2026-04-29 22:33 | 待创建：smart-fetcher.py | 进行中 |
| 2026-04-29 22:34 | 待创建：scheduler-core.py | 待定 |
| 2026-04-29 22:35 | 待创建：requirements.txt | 待定 |
| 2026-04-30 10:15 | 修复 `--with-replies` bug：autocli 不支持此参数，改用 `--format json --limit 20` | 完成 |
| 2026-04-30 10:15 | 修复 DB schema 不匹配：查询列名改为实际存在的 `fetch_count`, `probability` | 完成 |
| 2026-04-30 10:15 | 添加 Bootstrap 模式：DB 数据 < 20 行时始终执行，积累学习数据 | 完成 |
| 2026-04-30 10:15 | 添加 `_record_fetch_to_db` 方法：每次抓取后记录到 learning.db | 完成 |
| 2026-04-30 10:17 | 验证修复：karpathy 抓取成功（7.13s），DB 学习记录正常 | 完成 |
| 2026-04-30 13:23 | 修复 validate_cn_influencers.py：autocli 偶尔返回非零 exit code 但 stdout 有有效 JSON，改为不检查 returncode | 完成 |
| 2026-04-30 12:35 | 统一目录结构：`x-收藏` 改为 `x`，按日期分目录 | 完成 |
| 2026-04-30 14:53 | 统一日志系统：清理旧目录，日志统一到 `input/learn/logs/` | 完成 |
| 2026-04-30 15:00 | 修复日志系统延迟初始化：logger.py 改为 `get_log_manager()` | 完成 |
| 2026-04-30 15:30 | 更新说明文档：README、AGENTS、architecture 日志说明 | 完成 |

## 已知限制

- **autocli 不支持 `--with-replies`**：`twitter search` 命令无此参数，`from:` 查询已包含用户所有推文
- **需要 `/usr/bin/python3`（系统 Python 3.9）**：Homebrew Python 3.14 缺少 `yaml` 模块
- **学习数据冷启动**：DB 数据量 < 20 行时使用 Bootstrap 模式，始终执行

---

*本文件由 AI 与用户共同维护*
