"""
路径配置模块

默认数据目录：项目根目录下的 data/
支持（优先级从高到低）：
1. --data-dir 命令行参数
2. SMART_SCHEDULER_DATA_DIR 环境变量
3. settings.yaml 配置文件
4. 项目根目录下的 data/
"""

import os
import yaml
from pathlib import Path


# 项目根目录
PROJECT_ROOT = Path(__file__).parent


def load_settings() -> dict:
    """加载 settings.yaml 配置文件"""
    settings_file = PROJECT_ROOT / "settings.yaml"
    
    if not settings_file.exists():
        return {}
    
    try:
        with open(settings_file, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f) or {}
    except Exception:
        return {}


def get_data_dir(custom_dir: str = None) -> Path:
    """
    获取数据目录
    
    优先级（从高到低）：
    1. 命令行参数 --data-dir
    2. 环境变量 SMART_SCHEDULER_DATA_DIR
    3. settings.yaml 配置文件
    4. 项目根目录下的 data/
    """
    # 1. 命令行参数
    if custom_dir:
        return Path(custom_dir).expanduser().resolve()
    
    # 2. 环境变量
    env_dir = os.environ.get("SMART_SCHEDULER_DATA_DIR")
    if env_dir:
        return Path(env_dir).expanduser().resolve()
    
    # 3. settings.yaml 配置文件
    settings = load_settings()
    settings_dir = settings.get("data_dir")
    if settings_dir:
        return Path(settings_dir).expanduser().resolve()
    
    # 4. 项目根目录下的 data/
    return PROJECT_ROOT / "data"


def ensure_dirs(data_dir: Path) -> dict:
    """
    确保所有必要的目录存在
    
    返回目录结构字典
    """
    dirs = {
        "data": data_dir,
        "config": data_dir,
        "logs": data_dir / "logs",
        "logs_archive": data_dir / "logs" / "archive",
        "fetch_logs": data_dir / "fetch-logs",
        "content": data_dir / "content",  # x-收藏内容
    }
    
    for dir_path in dirs.values():
        dir_path.mkdir(parents=True, exist_ok=True)
    
    return dirs


def get_paths(custom_dir: str = None) -> dict:
    """
    获取所有路径配置
    
    返回完整的路径字典
    """
    data_dir = get_data_dir(custom_dir)
    dirs = ensure_dirs(data_dir)
    
    return {
        # 基础目录
        "data_dir": dirs["data"],
        
        # 配置文件
        "config_file": dirs["config"] / "config.yaml",
        "profiles_file": dirs["config"] / "accounts.json",
        
        # 数据库
        "db_file": dirs["data"] / "learning.db",
        
        # 日志
        "log_dir": dirs["logs"],
        "log_archive_dir": dirs["logs_archive"],
        "scheduler_log": dirs["logs"] / "scheduler.log",
        "error_log": dirs["logs"] / "error.log",
        "fetch_log": dirs["logs"] / "fetch.log",
        
        # 抓取日志
        "fetch_log_dir": dirs["fetch_logs"],
        
        # 内容目录
        "content_dir": dirs["content"],
    }


def print_paths(custom_dir: str = None):
    """打印路径配置（调试用）"""
    paths = get_paths(custom_dir)
    settings = load_settings()
    
    print("=" * 50)
    print("Smart Scheduler 路径配置")
    print("=" * 50)
    print(f"数据目录: {paths['data_dir']}")
    
    # 显示配置来源
    if custom_dir:
        print("来源: 命令行参数 --data-dir")
    elif os.environ.get("SMART_SCHEDULER_DATA_DIR"):
        print("来源: 环境变量 SMART_SCHEDULER_DATA_DIR")
    elif settings.get("data_dir"):
        print(f"来源: settings.yaml (data_dir: {settings['data_dir']})")
    else:
        print("来源: 默认 (项目内 data/)")
    
    print()
    print("配置文件:")
    print(f"  - {paths['config_file']}")
    print(f"  - {paths['profiles_file']}")
    print()
    print("数据库:")
    print(f"  - {paths['db_file']}")
    print()
    print("日志:")
    print(f"  - {paths['scheduler_log']}")
    print(f"  - {paths['error_log']}")
    print(f"  - {paths['fetch_log']}")
    print("=" * 50)


if __name__ == "__main__":
    # 测试路径配置
    print_paths()
