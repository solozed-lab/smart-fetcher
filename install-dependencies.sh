#!/bin/bash
# Smart Scheduler 依赖安装脚本
# Smart Scheduler Dependencies Installation Script

set -e  # 遇到错误立即退出

echo "========================================="
echo "Smart Scheduler 依赖安装"
echo "========================================="
echo ""

# 检查 Python 版本
echo "检查 Python 版本..."
python_version=$(python3 --version 2>&1)
echo "Python 版本: $python_version"

# 检查 pip 版本
echo "检查 pip 版本..."
pip_version=$(pip3 --version 2>&1)
echo "pip 版本: $pip_version"

echo ""
echo "========================================="
echo "安装依赖"
echo "========================================="
echo ""

# 升级 pip
echo "升级 pip..."
pip3 install --upgrade pip

# 安装核心依赖
echo "安装核心依赖..."
pip3 install pyyaml numpy scipy pandas

# 安装时间序列分析依赖
echo "安装时间序列分析依赖..."
pip3 install prophet statsmodels

# 安装机器学习依赖
echo "安装机器学习依赖..."
pip3 install scikit-learn

# 安装可视化依赖（可选）
echo "安装可视化依赖（可选）..."
pip3 install matplotlib seaborn

# 安装日志依赖
echo "安装日志依赖..."
pip3 install loguru

# 安装其他依赖
echo "安装其他依赖..."
pip3 install requests tqdm

echo ""
echo "========================================="
echo "验证安装"
echo "========================================="
echo ""

# 验证安装
echo "验证依赖安装..."
python3 -c "
import yaml
import numpy as np
import scipy
import pandas as pd
import prophet
import statsmodels
import sklearn
import matplotlib
import seaborn
import requests
from tqdm import tqdm
print('✅ 所有依赖安装成功！')
"

echo ""
echo "========================================="
echo "安装完成"
echo "========================================="
echo ""
echo "现在可以运行 Smart Scheduler 了："
echo "  python3 programs/smart-scheduler/smart-scheduler.py --help"
echo ""
