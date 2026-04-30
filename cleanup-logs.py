#!/usr/bin/env python3
"""
日志清理脚本

定期清理日志文件：
- 3天内：保留原始日志
- 3-7天：压缩为 .gz
- 7-30天：移到 archive/ 目录
- 30天以上：删除

使用方法：
    python cleanup-logs.py [--dry-run]
"""

import sys
from pathlib import Path

# 添加项目根目录到 path
sys.path.insert(0, str(Path(__file__).parent))

from logger import log_manager, get_logger

logger = get_logger("cleanup")


def main():
    """主函数"""
    dry_run = "--dry-run" in sys.argv
    
    if dry_run:
        logger.info("=== DRY RUN 模式 ===")
        logger.info("将显示会执行的操作，但不会实际执行")
        
        # 获取当前统计
        stats = log_manager.get_log_stats()
        logger.info(f"当前日志统计:")
        logger.info(f"  总文件数: {stats['total_files']}")
        logger.info(f"  总大小: {stats['total_size_mb']} MB")
        logger.info(f"  按年龄:")
        for age, info in stats['by_age'].items():
            logger.info(f"    {age}: {info['count']} 个文件, {info['size_mb']} MB")
        logger.info(f"  按类型:")
        for type_name, info in stats['by_type'].items():
            logger.info(f"    {type_name}: {info['count']} 个文件, {info['size_mb']} MB")
        
        logger.info("\n要执行清理，请运行: python cleanup-logs.py")
        return 0
    
    # 执行清理
    logger.info("开始日志清理任务")
    
    try:
        stats = log_manager.cleanup_logs()
        
        logger.info(f"清理完成:")
        logger.info(f"  压缩: {stats['compressed']} 个文件")
        logger.info(f"  归档: {stats['archived']} 个文件")
        logger.info(f"  删除: {stats['deleted']} 个文件")
        logger.info(f"  错误: {stats['errors']} 个")
        
        # 清理后统计
        after_stats = log_manager.get_log_stats()
        logger.info(f"清理后统计:")
        logger.info(f"  总文件数: {after_stats['total_files']}")
        logger.info(f"  总大小: {after_stats['total_size_mb']} MB")
        
        return 0
        
    except Exception as e:
        logger.error(f"清理任务失败: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
