# Smart Fetcher

[![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Stars](https://img.shields.io/github/stars/solozed-lab/smart-fetcher.svg)](https://github.com/solozed-lab/smart-fetcher)

[中文文档](README_zh.md)

> A self-learning social media fetcher that reads content like a human.

Smart Fetcher automatically adjusts fetch timing, frequency, and strategy based on each account's posting patterns. The more you use it, the smarter it gets.

## Why?

- **Human-like behavior**: Random intervals, natural reading patterns, no bulk operations
- **Self-learning**: Adapts to each account's schedule automatically
- **Multi-platform**: Twitter/X, WeChat, Xiaohongshu, Bilibili (via [autocli](https://github.com/nicepkg/autocli))
- **Zero config**: Works out of the box, learns as it goes

## Quick Start

### Prerequisites

- Python 3.9+
- [autocli](https://github.com/nicepkg/autocli) installed and configured

### Installation

```bash
# Clone the repository
git clone https://github.com/solozed-lab/smart-fetcher.git
cd smart-fetcher

# Install dependencies
./install-dependencies.sh
```

### Configuration

Create `settings.yaml` in the project root:

```yaml
# Data directory (absolute or relative path)
# Leave empty to use ./data/ by default
data_dir: ~/my-data
```

### Usage

```bash
# Show path configuration
python3 smart_fetcher.py --show-paths

# Run adaptive mode (recommended)
python3 smart_fetcher.py --adaptive

# Run scheduled mode
python3 smart_fetcher.py --type scheduled

# Show account profiles
python3 smart_fetcher.py --show-profiles

# Update account profiles
python3 smart_fetcher.py --update-profiles
```

## How It Works

```
Account Posts → Smart Fetcher Learns → Optimizes Schedule → Better Content
      ↑                                                          |
      └──────────────────── Feedback Loop ──────────────────────┘
```

### Learning Algorithm

1. **Bayesian Update**: Tracks success rate for each account per hour
2. **Thompson Sampling**: Balances exploration vs exploitation
3. **Time Series Analysis**: Identifies posting patterns over time
4. **Collaborative Filtering**: Discovers similar accounts

### Fetch Modes

| Mode | Description | Use Case |
|------|-------------|----------|
| **Bootstrap** | Fetches frequently to learn patterns | First 20 runs |
| **Adaptive** | Uses learned data to optimize | Daily use |
| **Scheduled** | Fixed schedule with smart selection | Manual control |

## Directory Structure

```
data/
├── config.yaml          # Configuration
├── accounts.json        # Account profiles
├── learning.db          # Learning database
├── logs/                # System logs
│   ├── scheduler.log   # Main log (scheduling decisions, learning algorithms)
│   ├── fetch.log       # Fetch log (detailed records of each fetch)
│   ├── error.log       # Error log (exceptions and errors)
│   └── archive/        # Archive directory (logs older than 7 days)
├── fetch-logs/          # Fetch statistics (JSON format)
│   └── YYYY-MM-DD.json
└── content/             # Fetched content
    └── x/               # Twitter/X platform
        └── YYYY-MM-DD/  # By date
            ├── summary.md
            └── <handle>.md
```

### Log Types

| Log Type | File | Content | Purpose |
|----------|------|---------|---------|
| System Log | `logs/scheduler.log` | Scheduling decisions, learning algorithms, account selection | Debug system logic |
| Fetch Log | `logs/fetch.log` | Detailed results of each fetch | Monitor fetch status |
| Error Log | `logs/error.log` | Exceptions and errors | Troubleshoot issues |
| Fetch Stats | `fetch-logs/*.json` | Daily fetch summary | Statistical analysis |

### Log Cleanup

```bash
# Preview cleanup (dry run)
python3 cleanup-logs.py --dry-run

# Execute cleanup
python3 cleanup-logs.py
```

Cleanup rules:
- Within 3 days: Keep original logs
- 3-7 days: Compress to `.gz`
- 7-30 days: Move to `archive/` directory
- Over 30 days: Delete

## Configuration

### Path Priority

1. `--data-dir` command line argument
2. `SMART_FETCHER_DATA_DIR` environment variable
3. `settings.yaml` config file
4. `./data/` directory (default)

### Environment Variables

```bash
# Custom data directory
export SMART_FETCHER_DATA_DIR=/path/to/data

# Autocli path (if not in PATH)
export AUTOCLI_PATH=/usr/local/bin/autocli
```

## Cron Jobs

Automated scheduling with cron:

```bash
# Hourly adaptive fetch
0 * * * * cd /path/to/smart-fetcher && python3 smart_fetcher.py --adaptive

# Daily summary at 22:00
0 22 * * * cd /path/to/smart-fetcher && python3 daily_summary.py

# Weekly cross-validation on Sunday
0 22 * * 0 cd /path/to/smart-fetcher && python3 cross_validation.py

# Log cleanup at 02:00
0 2 * * * cd /path/to/smart-fetcher && python3 cleanup_logs.py
```

## Roadmap

- [x] v0.2 - Twitter/X support with self-learning
- [ ] v0.3 - WeChat public account support
- [ ] v0.4 - Xiaohongshu support
- [ ] v0.5 - Bilibili support
- [ ] v1.0 - Web UI for content browsing
- [ ] v1.1 - AI-powered content summarization

## Contributing

Contributions are welcome! Please read our [Contributing Guide](CONTRIBUTING.md) first.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- [autocli](https://github.com/nicepkg/autocli) - Multi-platform CLI tool
- [loguru](https://github.com/Delgan/loguru) - Python logging made simple

## Contact

- GitHub: [@solozed-lab](https://github.com/solozed-lab)
- Email: i@solozed.com
- Website: [solozed.com](https://solozed.com)
