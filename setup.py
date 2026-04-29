from setuptools import setup, find_packages
import os

# 读取 README.md
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

# 读取 requirements.txt
with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="smart-scheduler",
    version="1.0.0",
    author="Your Name",
    author_email="your.email@example.com",
    description="智能抓取调度系统 - 根据账号习惯动态调整抓取时间",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/your-username/smart-scheduler",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Internet :: WWW/HTTP :: Dynamic Content",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
    ],
    python_requires=">=3.9",
    install_requires=requirements,
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
            "black>=23.0.0",
            "flake8>=6.0.0",
            "mypy>=1.0.0",
        ],
        "docs": [
            "sphinx>=6.0.0",
            "sphinx-rtd-theme>=1.0.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "smart-scheduler=smart_scheduler.cli:main",
        ],
    },
    include_package_data=True,
    package_data={
        "smart_scheduler": [
            "config/*.yaml",
            "config/*.json",
            "data/*.sql",
        ],
    },
    keywords=[
        "ai",
        "machine-learning",
        "twitter",
        "social-media",
        "scheduler",
        "automation",
        "self-learning",
        "adaptive",
    ],
    project_urls={
        "Bug Reports": "https://github.com/your-username/smart-scheduler/issues",
        "Source": "https://github.com/your-username/smart-scheduler",
        "Documentation": "https://github.com/your-username/smart-scheduler#readme",
    },
)
