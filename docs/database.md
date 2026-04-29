# 数据库设计

## 概述

Smart Scheduler 使用 SQLite 作为数据库，存储学习数据、账号画像、抓取历史等信息。

## 数据库文件

- **路径**: `input/learn/learning.db`
- **类型**: SQLite
- **版本**: 1.0

## 表结构

### 1. 抓取历史表 (fetch_history)

记录每次抓取的结果。

```sql
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

-- 索引
CREATE INDEX idx_fetch_history_account ON fetch_history(account);
CREATE INDEX idx_fetch_history_time ON fetch_history(fetch_time);
```

**字段说明**：

| 字段 | 类型 | 说明 |
|------|------|------|
| id | INTEGER | 主键 |
| account | TEXT | 账号名 |
| fetch_time | TIMESTAMP | 抓取时间 |
| has_new_content | BOOLEAN | 是否有新内容 |
| tweets_count | INTEGER | 推文数量 |
| replies_count | INTEGER | 评论数量 |
| engagement_score | FLOAT | 互动分数 |
| created_at | TIMESTAMP | 创建时间 |

**示例数据**：

```json
{
    "id": 1,
    "account": "karpathy",
    "fetch_time": "2026-04-29 10:15:00",
    "has_new_content": true,
    "tweets_count": 3,
    "replies_count": 15,
    "engagement_score": 85.5,
    "created_at": "2026-04-29 10:15:00"
}
```

### 2. 用户反馈表 (user_feedback)

记录用户对账号的反馈。

```sql
CREATE TABLE user_feedback (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    account TEXT NOT NULL,
    feedback_type TEXT NOT NULL,
    feedback_time TIMESTAMP NOT NULL,
    reason TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 索引
CREATE INDEX idx_user_feedback_account ON user_feedback(account);
```

**字段说明**：

| 字段 | 类型 | 说明 |
|------|------|------|
| id | INTEGER | 主键 |
| account | TEXT | 账号名 |
| feedback_type | TEXT | 反馈类型（positive, negative, neutral） |
| feedback_time | TIMESTAMP | 反馈时间 |
| reason | TEXT | 原因 |
| created_at | TIMESTAMP | 创建时间 |

**示例数据**：

```json
{
    "id": 1,
    "account": "karpathy",
    "feedback_type": "positive",
    "feedback_time": "2026-04-29 10:20:00",
    "reason": "内容质量高",
    "created_at": "2026-04-29 10:20:00"
}
```

### 3. 活跃时段统计表 (active_hours_stats)

统计账号在每个时段的活跃情况。

```sql
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

-- 索引
CREATE INDEX idx_active_hours_account ON active_hours_stats(account);
```

**字段说明**：

| 字段 | 类型 | 说明 |
|------|------|------|
| id | INTEGER | 主键 |
| account | TEXT | 账号名 |
| hour | INTEGER | 小时（0-23） |
| fetch_count | INTEGER | 抓取次数 |
| new_content_count | INTEGER | 有新内容的次数 |
| probability | FLOAT | 有新内容的概率 |
| updated_at | TIMESTAMP | 更新时间 |

**示例数据**：

```json
{
    "id": 1,
    "account": "karpathy",
    "hour": 10,
    "fetch_count": 5,
    "new_content_count": 4,
    "probability": 0.8,
    "updated_at": "2026-04-29 10:15:00"
}
```

### 4. 更新频率统计表 (update_frequency_stats)

统计账号的更新频率。

```sql
CREATE TABLE update_frequency_stats (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    account TEXT NOT NULL,
    frequency_type TEXT NOT NULL,
    observed_count INTEGER DEFAULT 0,
    probability FLOAT DEFAULT 0.0,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(account, frequency_type)
);

-- 索引
CREATE INDEX idx_update_frequency_account ON update_frequency_stats(account);
```

**字段说明**：

| 字段 | 类型 | 说明 |
|------|------|------|
| id | INTEGER | 主键 |
| account | TEXT | 账号名 |
| frequency_type | TEXT | 频率类型（daily, weekly, monthly） |
| observed_count | INTEGER | 观测次数 |
| probability | FLOAT | 概率 |
| updated_at | TIMESTAMP | 更新时间 |

**示例数据**：

```json
{
    "id": 1,
    "account": "karpathy",
    "frequency_type": "daily",
    "observed_count": 3,
    "probability": 0.3,
    "updated_at": "2026-04-29 10:15:00"
}
```

### 5. 调度策略表 (schedule_strategy)

记录调度策略的效果。

```sql
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
```

**字段说明**：

| 字段 | 类型 | 说明 |
|------|------|------|
| id | INTEGER | 主键 |
| strategy_name | TEXT | 策略名称 |
| strategy_value | TEXT | 策略值 |
| success_count | INTEGER | 成功次数 |
| failure_count | INTEGER | 失败次数 |
| success_rate | FLOAT | 成功率 |
| updated_at | TIMESTAMP | 更新时间 |

**示例数据**：

```json
{
    "id": 1,
    "strategy_name": "fetch_count",
    "strategy_value": "5",
    "success_count": 10,
    "failure_count": 2,
    "success_rate": 0.83,
    "updated_at": "2026-04-29 10:15:00"
}
```

### 6. 账号画像表 (account_profiles)

存储账号的基本信息和画像。

```sql
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

**字段说明**：

| 字段 | 类型 | 说明 |
|------|------|------|
| id | INTEGER | 主键 |
| account | TEXT | 账号名（唯一） |
| name | TEXT | 昵称 |
| category | TEXT | 分类（core, cn_influencer, en_influencer, self_follow） |
| priority | INTEGER | 优先级（1-3） |
| frequency | TEXT | 更新频率（high, medium, low） |
| content_type | TEXT | 内容类型（education, opinion, technical, mixed） |
| status | TEXT | 状态（active, pending, paused, removed） |
| last_updated | TIMESTAMP | 最后更新时间 |
| created_at | TIMESTAMP | 创建时间 |
| updated_at | TIMESTAMP | 更新时间 |

**示例数据**：

```json
{
    "id": 1,
    "account": "karpathy",
    "name": "Andrej Karpathy",
    "category": "core",
    "priority": 3,
    "frequency": "medium",
    "content_type": "education",
    "status": "active",
    "last_updated": "2026-04-29 22:15:00",
    "created_at": "2026-04-29 22:30:00",
    "updated_at": "2026-04-29 22:30:00"
}
```

## 数据库操作

### 连接数据库

```python
import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).parent.parent.parent / "input" / "learn" / "learning.db"

def get_connection():
    """获取数据库连接"""
    return sqlite3.connect(DB_PATH)
```

### 插入数据

```python
def insert_fetch_history(account: str, fetch_time: datetime, 
                        has_new_content: bool, tweets_count: int,
                        replies_count: int, engagement_score: float):
    """插入抓取历史"""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        INSERT INTO fetch_history (account, fetch_time, has_new_content, 
                                  tweets_count, replies_count, engagement_score)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (account, fetch_time.isoformat(), has_new_content, 
          tweets_count, replies_count, engagement_score))
    
    conn.commit()
    conn.close()
```

### 查询数据

```python
def get_active_hours_stats(account: str, hour: int) -> Dict[str, Any]:
    """获取活跃时段统计"""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT fetch_count, new_content_count, probability
        FROM active_hours_stats
        WHERE account = ? AND hour = ?
    ''', (account, hour))
    
    result = cursor.fetchone()
    conn.close()
    
    if result:
        return {
            'fetch_count': result[0],
            'new_content_count': result[1],
            'probability': result[2]
        }
    
    return None
```

### 更新数据

```python
def update_active_hours_stats(account: str, hour: int, 
                             fetch_count: int, new_content_count: int,
                             probability: float):
    """更新活跃时段统计"""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        UPDATE active_hours_stats
        SET fetch_count = ?, new_content_count = ?, probability = ?, updated_at = ?
        WHERE account = ? AND hour = ?
    ''', (fetch_count, new_content_count, probability, 
          datetime.now().isoformat(), account, hour))
    
    conn.commit()
    conn.close()
```

### 删除数据

```python
def delete_old_fetch_history(days: int = 30):
    """删除旧的抓取历史"""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        DELETE FROM fetch_history
        WHERE fetch_time < datetime('now', ?)
    ''', (f'-{days} days',))
    
    conn.commit()
    conn.close()
```

## 数据库维护

### 备份

```python
import shutil

def backup_database(backup_path: str):
    """备份数据库"""
    shutil.copy2(DB_PATH, backup_path)
```

### 清理

```python
def cleanup_database():
    """清理数据库"""
    # 删除 30 天前的抓取历史
    delete_old_fetch_history(30)
    
    # 删除 90 天前的用户反馈
    delete_old_user_feedback(90)
    
    # 优化数据库
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('VACUUM')
    conn.close()
```

### 迁移

```python
def migrate_database():
    """数据库迁移"""
    conn = get_connection()
    cursor = conn.cursor()
    
    # 检查表是否存在
    cursor.execute('''
        SELECT name FROM sqlite_master WHERE type='table' AND name='fetch_history'
    ''')
    
    if not cursor.fetchone():
        # 创建表
        cursor.execute('''
            CREATE TABLE fetch_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                account TEXT NOT NULL,
                fetch_time TIMESTAMP NOT NULL,
                has_new_content BOOLEAN,
                tweets_count INTEGER DEFAULT 0,
                replies_count INTEGER DEFAULT 0,
                engagement_score FLOAT DEFAULT 0.0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
    
    conn.commit()
    conn.close()
```

## 性能优化

### 索引

为常用查询字段创建索引：

```sql
CREATE INDEX idx_fetch_history_account ON fetch_history(account);
CREATE INDEX idx_fetch_history_time ON fetch_history(fetch_time);
CREATE INDEX idx_user_feedback_account ON user_feedback(account);
CREATE INDEX idx_active_hours_account ON active_hours_stats(account);
CREATE INDEX idx_update_frequency_account ON update_frequency_stats(account);
```

### 批量操作

使用批量操作减少数据库交互：

```python
def batch_insert_fetch_history(records: List[Dict[str, Any]]):
    """批量插入抓取历史"""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.executemany('''
        INSERT INTO fetch_history (account, fetch_time, has_new_content, 
                                  tweets_count, replies_count, engagement_score)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', [(r['account'], r['fetch_time'].isoformat(), r['has_new_content'],
           r['tweets_count'], r['replies_count'], r['engagement_score'])
          for r in records])
    
    conn.commit()
    conn.close()
```

### 连接池

使用连接池减少连接开销：

```python
from contextlib import contextmanager

@contextmanager
def get_db_connection():
    """获取数据库连接（上下文管理器）"""
    conn = sqlite3.connect(DB_PATH)
    try:
        yield conn
    finally:
        conn.close()
```

## 数据安全

### 加密

SQLite 本身不支持加密，可以使用 SQLCipher 进行加密：

```python
import pysqlcipher3

def get_encrypted_connection():
    """获取加密连接"""
    conn = pysqlcipher3.connect(DB_PATH)
    conn.execute("PRAGMA key='your-secret-key'")
    return conn
```

### 访问控制

使用文件系统权限控制数据库访问：

```bash
chmod 600 input/learn/learning.db
```

### 备份策略

定期备份数据库：

```bash
# 每天备份
0 0 * * * cp /path/to/learning.db /path/to/backup/learning_$(date +\%Y\%m\%d).db
```

## 监控

### 性能监控

监控数据库性能：

```python
def monitor_database_performance():
    """监控数据库性能"""
    conn = get_connection()
    cursor = conn.cursor()
    
    # 获取表大小
    cursor.execute('''
        SELECT name, SUM(pgsize) FROM dbstat GROUP BY name
    ''')
    
    # 获取索引使用情况
    cursor.execute('''
        SELECT * FROM sqlite_stat1
    ''')
    
    conn.close()
```

### 数据质量

监控数据质量：

```python
def check_data_quality():
    """检查数据质量"""
    conn = get_connection()
    cursor = conn.cursor()
    
    # 检查空值
    cursor.execute('''
        SELECT COUNT(*) FROM fetch_history WHERE account IS NULL
    ''')
    
    # 检查重复
    cursor.execute('''
        SELECT account, fetch_time, COUNT(*) 
        FROM fetch_history 
        GROUP BY account, fetch_time 
        HAVING COUNT(*) > 1
    ''')
    
    conn.close()
```
