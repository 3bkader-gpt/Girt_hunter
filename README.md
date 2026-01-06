<div align="center">

# 🎁 Gift Hunter Bot

### *Automated Telegram Gifts Buyer — Smart, Secure, Observable*

[![Python](https://img.shields.io/badge/Python-3.12+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![Telegram](https://img.shields.io/badge/Telegram-Bot-26A5E4?style=for-the-badge&logo=telegram&logoColor=white)](https://telegram.org)
[![Docker](https://img.shields.io/badge/Docker-Ready-2496ED?style=for-the-badge&logo=docker&logoColor=white)](https://docker.com)
[![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)](LICENSE)

<img src="https://capsule-render.vercel.app/api?type=waving&color=gradient&customColorList=6,11,20&height=180&section=header&text=Gift%20Hunter&fontSize=42&fontColor=fff&animation=twinkling&fontAlignY=32"/>

**Automatically snipe rare Telegram gifts before they sell out!**

[Features](#-features) •
[Quick Start](#-quick-start) •
[Configuration](#-configuration) •
[Docker](#-docker) •
[API](#-api)

</div>

---

## ✨ Features

<table>
<tr>
<td width="50%">

### 🎯 Smart Purchasing
- **Auto-detection** of new gifts
- **Priority system** for rare gifts
- **Multi-recipient** support
- **Partial purchases** when low balance

</td>
<td width="50%">

### 🔒 Security First
- **Environment variables** for secrets
- **No hardcoded credentials**
- **Non-root Docker** container
- **Encrypted sessions**

</td>
</tr>
<tr>
<td width="50%">

### 📊 Full Observability
- **Prometheus metrics** (`/metrics`)
- **Health endpoints** (`/health`)
- **Structured JSON logs**
- **Real-time notifications**

</td>
<td width="50%">

### ⚡ High Performance
- **Async architecture**
- **SQLite storage**
- **Rate limit handling**
- **Auto-reconnection**

</td>
</tr>
</table>

---

## 🚀 Quick Start

### Prerequisites
- Python 3.12+ or Docker
- Telegram API credentials from [my.telegram.org](https://my.telegram.org/apps)

### Installation

```bash
# Clone the repository
git clone https://github.com/3bkader-gpt/Girt_hunter.git
cd Girt_hunter

# Create environment file
cp .env.example .env
# Edit .env with your credentials

# Install dependencies
pip install -e .

# Run the bot
python -m src.main
```

---

## 🐳 Docker

The recommended way to run Gift Hunter in production:

```bash
# Build and start
docker compose up -d

# View logs
docker compose logs -f

# Stop
docker compose down
```

### Endpoints
| Endpoint | Port | Description |
|----------|------|-------------|
| `/health` | 8080 | Health check status |
| `/metrics` | 9090 | Prometheus metrics |

---

## ⚙️ Configuration

### Environment Variables (`.env`)

```env
TELEGRAM_API_ID=your_api_id
TELEGRAM_API_HASH=your_api_hash
TELEGRAM_PHONE_NUMBER=+1234567890
```

### Application Config (`config.yaml`)

```yaml
gifts:
  ranges:
    - name: "Budget Gifts"
      min_price: 1
      max_price: 500
      supply_limit: 500000
      recipients:
        - "@username"
  prioritize_low_supply: true

notifications:
  channel_id: -1001234567890
```

<details>
<summary>📋 Full Configuration Options</summary>

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `telegram.interval_seconds` | int | 10 | Polling interval |
| `telegram.max_retries` | int | 3 | Purchase retry attempts |
| `notifications.channel_id` | int | -100 | Notification channel |
| `gifts.prioritize_low_supply` | bool | true | Rare gifts first |
| `budget.daily_limit` | int | 0 | Max daily spend (0=unlimited) |
| `budget.reserve_balance` | int | 0 | Minimum balance to keep |

</details>

---

## 📁 Project Structure

```
gift_hunter/
├── src/
│   ├── config/          # Pydantic settings
│   ├── core/            # Telegram client, monitor, purchase engine
│   ├── storage/         # SQLite database layer
│   ├── observability/   # Logging, metrics, health
│   └── notifications/   # Telegram notifications
├── tests/               # Unit tests
├── scripts/             # Migration utilities
├── config.yaml          # Application config
├── .env.example         # Environment template
└── docker-compose.yml   # Docker deployment
```

---

## 📈 Metrics

Gift Hunter exposes Prometheus metrics for monitoring:

```
# Counters
gift_hunter_gifts_checked_total
gift_hunter_gifts_purchased_total

# Gauges  
gift_hunter_balance_stars
gift_hunter_monitoring_active

# Histograms
gift_hunter_purchase_duration_seconds
```

---

## 🔄 Migration from v1.0

```bash
# Backup your data
cp -r data data.backup

# Run migration script
python scripts/migrate_history.py

# Rebuild Docker
docker compose build --no-cache
docker compose up -d
```

---

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

<div align="center">

## 👨‍💻 Author

<img src="https://capsule-render.vercel.app/api?type=waving&color=gradient&customColorList=24&height=100&section=footer"/>

<a href="https://github.com/3bkader-gpt">
  <img src="https://img.shields.io/badge/Crafted%20with%20%E2%9D%A4%EF%B8%8F%20by-Mohamed%20Omar-FF6B6B?style=for-the-badge&labelColor=1a1a2e"/>
</a>

<br/>

**Mohamed Omar** © 2026

<sub>
🌟 Star this repo if you find it useful! 🌟
</sub>

<br/><br/>

[![GitHub](https://img.shields.io/badge/GitHub-Follow-181717?style=flat-square&logo=github)](https://github.com/3bkader-gpt)

</div>
