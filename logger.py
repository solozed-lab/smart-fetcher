"""
smart-scheduler 日志系统

基于 loguru 实现专业的日志管理：
- 按天分割日志
- 自动压缩旧日志
- 分层保留策略
- 结构化日志格式

日志清理规范：
- 3天内：保留原始日志
- 3-7天：压缩为 .gz
- 7-30天：移到 archive/ 目录
- 30天以上：删除
"""

import os
import sys
import gzip
import shutil
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional

from loguru import logger


class LogManager:
    """日志管理器"""
    
    def __init__(self, log_dir: str = None):
        # 如果没有指定日志目录，使用默认路径
        if log_dir is None:
            from paths import get_paths
            paths = get_paths()
            self.log_dir = paths['log_dir']
        else:
            self.log_dir = Path(log_dir)
        
        self.log_dir.mkdir(parents=True, exist_ok=True)
        
        # 子目录
        self.archive_dir = self.log_dir / "archive"
        self.archive_dir.mkdir(exist_ok=True)
        
        # 日志文件路径
        self.scheduler_log = self.log_dir / "scheduler.log"
        self.error_log = self.log_dir / "error.log"
        self.fetch_log = self.log_dir / "fetch.log"
        
        # 配置 loguru
        self._setup_logger()
    
    def _setup_logger(self):
        """配置 loguru logger"""
        # 移除默认的 stderr handler
        logger.remove()
        
        # 控制台输出（INFO 级别）
        logger.add(
            sys.stderr,
            format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
                   "<level>{level: <8}</level> | "
                   "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> | "
                   "<level>{message}</level>",
            level="INFO",
            colorize=True
        )
        
        # 主日志文件（DEBUG 级别，按天轮转）
        logger.add(
            str(self.scheduler_log),
            format="{time:YYYY-MM-DD HH:mm:ss.SSS} | "
                   "{level: <8} | "
                   "{name}:{function}:{line} | "
                   "{message}",
            level="DEBUG",
            rotation="00:00",  # 每天午夜轮转
            retention="3 days",  # 保留3天原始日志
            compression=None,  # 不自动压缩，由清理脚本处理
            encoding="utf-8",
            enqueue=True  # 线程安全
        )
        
        # 错误日志文件（ERROR 级别）
        logger.add(
            str(self.error_log),
            format="{time:YYYY-MM-DD HH:mm:ss.SSS} | "
                   "{level: <8} | "
                   "{name}:{function}:{line} | "
                   "{message}",
            level="ERROR",
            rotation="00:00",
            retention="7 days",
            compression="gz",
            encoding="utf-8",
            enqueue=True
        )
        
        # 抓取日志文件（INFO 级别，记录抓取操作）
        logger.add(
            str(self.fetch_log),
            format="{time:YYYY-MM-DD HH:mm:ss.SSS} | "
                   "{level: <8} | "
                   "{message}",
            level="INFO",
            rotation="00:00",
            retention="3 days",
            compression=None,
            encoding="utf-8",
            enqueue=True
        )
    
    def cleanup_logs(self):
        """
        清理日志文件
        
        规范：
        - 3天内：保留原始日志
        - 3-7天：压缩为 .gz
        - 7-30天：移到 archive/ 目录
        - 30天以上：删除
        """
        now = datetime.now()
        logger.info(f"开始清理日志，当前时间: {now}")
        
        # 统计
        stats = {
            "compressed": 0,
            "archived": 0,
            "deleted": 0,
            "errors": 0
        }
        
        # 处理主日志目录
        for log_file in self.log_dir.glob("*.log"):
            try:
                # 获取文件修改时间
                mtime = datetime.fromtimestamp(log_file.stat().st_mtime)
                age_days = (now - mtime).days
                
                if age_days > 30:
                    # 超过30天：删除
                    log_file.unlink()
                    stats["deleted"] += 1
                    logger.debug(f"删除日志: {log_file.name} (存在 {age_days} 天)")
                    
                elif age_days > 7:
                    # 7-30天：移到归档目录
                    archive_path = self.archive_dir / log_file.name
                    shutil.move(str(log_file), str(archive_path))
                    stats["archived"] += 1
                    logger.debug(f"归档日志: {log_file.name} (存在 {age_days} 天)")
                    
                elif age_days > 3:
                    # 3-7天：压缩
                    gz_path = log_file.with_suffix('.log.gz')
                    with open(log_file, 'rb') as f_in:
                        with gzip.open(gz_path, 'wb') as f_out:
                            shutil.copyfileobj(f_in, f_out)
                    log_file.unlink()
                    stats["compressed"] += 1
                    logger.debug(f"压缩日志: {log_file.name} (存在 {age_days} 天)")
                    
            except Exception as e:
                stats["errors"] += 1
                logger.error(f"处理日志文件失败 {log_file}: {e}")
        
        # 处理归档目录中的压缩文件
        for gz_file in self.archive_dir.glob("*.gz"):
            try:
                mtime = datetime.fromtimestamp(gz_file.stat().st_mtime)
                age_days = (now - mtime).days
                
                if age_days > 30:
                    gz_file.unlink()
                    stats["deleted"] += 1
                    logger.debug(f"删除归档: {gz_file.name} (存在 {age_days} 天)")
                    
            except Exception as e:
                stats["errors"] += 1
                logger.error(f"处理归档文件失败 {gz_file}: {e}")
        
        logger.info(f"日志清理完成: 压缩 {stats['compressed']}, "
                   f"归档 {stats['archived']}, "
                   f"删除 {stats['deleted']}, "
                   f"错误 {stats['errors']}")
        
        return stats
    
    def get_log_stats(self) -> dict:
        """获取日志统计信息"""
        now = datetime.now()
        
        stats = {
            "total_files": 0,
            "total_size_mb": 0,
            "by_age": {
                "0-3天": {"count": 0, "size_mb": 0},
                "3-7天": {"count": 0, "size_mb": 0},
                "7-30天": {"count": 0, "size_mb": 0},
                "30天+": {"count": 0, "size_mb": 0}
            },
            "by_type": {
                "原始日志": {"count": 0, "size_mb": 0},
                "压缩日志": {"count": 0, "size_mb": 0},
                "归档日志": {"count": 0, "size_mb": 0}
            }
        }
        
        # 统计主目录
        for f in self.log_dir.iterdir():
            if f.is_file():
                stats["total_files"] += 1
                size_mb = f.stat().st_size / (1024 * 1024)
                stats["total_size_mb"] += size_mb
                
                # 按类型
                if f.suffix == '.gz':
                    stats["by_type"]["压缩日志"]["count"] += 1
                    stats["by_type"]["压缩日志"]["size_mb"] += size_mb
                elif f.suffix == '.log':
                    stats["by_type"]["原始日志"]["count"] += 1
                    stats["by_type"]["原始日志"]["size_mb"] += size_mb
                
                # 按年龄
                mtime = datetime.fromtimestamp(f.stat().st_mtime)
                age_days = (now - mtime).days
                
                if age_days <= 3:
                    stats["by_age"]["0-3天"]["count"] += 1
                    stats["by_age"]["0-3天"]["size_mb"] += size_mb
                elif age_days <= 7:
                    stats["by_age"]["3-7天"]["count"] += 1
                    stats["by_age"]["3-7天"]["size_mb"] += size_mb
                elif age_days <= 30:
                    stats["by_age"]["7-30天"]["count"] += 1
                    stats["by_age"]["7-30天"]["size_mb"] += size_mb
                else:
                    stats["by_age"]["30天+"]["count"] += 1
                    stats["by_age"]["30天+"]["size_mb"] += size_mb
        
        # 统计归档目录
        for f in self.archive_dir.iterdir():
            if f.is_file():
                stats["total_files"] += 1
                size_mb = f.stat().st_size / (1024 * 1024)
                stats["total_size_mb"] += size_mb
                stats["by_type"]["归档日志"]["count"] += 1
                stats["by_type"]["归档日志"]["size_mb"] += size_mb
        
        # 四舍五入
        stats["total_size_mb"] = round(stats["total_size_mb"], 2)
        for category in ["by_age", "by_type"]:
            for key in stats[category]:
                stats[category][key]["size_mb"] = round(stats[category][key]["size_mb"], 2)
        
        return stats


# 全局日志管理器实例（延迟初始化）
log_manager = None


def get_log_manager():
    """获取全局日志管理器（延迟初始化）"""
    global log_manager
    if log_manager is None:
        log_manager = LogManager()
    return log_manager


# 便捷的日志函数
def get_logger(name: str = None):
    """获取 logger 实例"""
    # 确保日志管理器已初始化
    get_log_manager()
    if name:
        return logger.bind(name=name)
    return logger


# 示例用法
if __name__ == "__main__":
    # 测试日志
    test_logger = get_logger("test")
    
    test_logger.debug("这是一条 DEBUG 日志")
    test_logger.info("这是一条 INFO 日志")
    test_logger.warning("这是一条 WARNING 日志")
    test_logger.error("这是一条 ERROR 日志")
    
    # 测试清理
    stats = log_manager.cleanup_logs()
    print(f"\n清理结果: {stats}")
    
    # 获取统计
    log_stats = log_manager.get_log_stats()
    print(f"\n日志统计: {log_stats}")
