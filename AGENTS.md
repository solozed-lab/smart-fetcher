# AGENTS.md — smart-scheduler/

智能抓取调度系统 — 根据账号习惯动态调整抓取时间。

## 核心理念

> 不是「我几点抓取」，而是「这个账号什么时候更新，我就什么时候去看」。

## 文件结构

```
smart-scheduler/
├── README.md              # 使用说明
├── AGENTS.md              # 本文件
├── smart-scheduler.py     # 主脚本
├── scheduler-core.py      # 调度核心逻辑
└── requirements.txt       # 依赖
```

## 使用规则

### 1. 手动触发

```bash
# 执行一次智能抓取
python3 smart-scheduler.py

# 指定抓取类型
python3 smart-scheduler.py --type scheduled
python3 smart-scheduler.py --type manual
python3 smart-scheduler.py --type cross_validation

# 指定账号
python3 smart-scheduler.py --accounts karpathy,AndrewYNg

# 查看账号画像
python3 smart-scheduler.py --show-profiles

# 更新账号画像
python3 smart-scheduler.py --update-profiles
```

### 2. Cron Job 触发

```bash
# 每小时执行一次智能调度
0 * * * * cd /Users/yun-z/AI/hermes && python3 programs/smart-scheduler/smart-scheduler.py
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

- 存入 `input/x-大佬/`、`input/x-热点/` 等目录
- 生成每日汇总 `input/每日汇总/YYYY-MM-DD.md`

### 2. 抓取日志

- 记录到 `input/fetch-log.json`
- 包含抓取时间、账号、成功/失败数量等

### 3. 画像更新

- 更新 `input/account-profiles.json`
- 记录最后更新时间、更新频率等

## 配置

配置文件位置：`input/config.yaml`

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
| 2026-04-29 22:33 | 待创建：smart-scheduler.py | 进行中 |
| 2026-04-29 22:34 | 待创建：scheduler-core.py | 待定 |
| 2026-04-29 22:35 | 待创建：requirements.txt | 待定 |
| 2026-04-30 10:15 | 修复 `--with-replies` bug：autocli 不支持此参数，改用 `--format json --limit 20` | 完成 |
| 2026-04-30 10:15 | 修复 DB schema 不匹配：查询列名改为实际存在的 `fetch_count`, `probability` | 完成 |
| 2026-04-30 10:15 | 添加 Bootstrap 模式：DB 数据 < 20 行时始终执行，积累学习数据 | 完成 |
| 2026-04-30 10:15 | 添加 `_record_fetch_to_db` 方法：每次抓取后记录到 learning.db | 完成 |
| 2026-04-30 10:17 | 验证修复：karpathy 抓取成功（7.13s），DB 学习记录正常 | 完成 |

## 已知限制

- **autocli 不支持 `--with-replies`**：`twitter search` 命令无此参数，`from:` 查询已包含用户所有推文
- **需要 `/usr/bin/python3`（系统 Python 3.9）**：Homebrew Python 3.14 缺少 `yaml` 模块
- **学习数据冷启动**：DB 数据量 < 20 行时使用 Bootstrap 模式，始终执行

---

*本文件由 AI 与用户共同维护*
