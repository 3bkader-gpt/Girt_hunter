<div align="center">

# 🎁 Girt Hunter

### Automated Telegram Userbot for Gift Purchasing

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/)
[![Pyrogram](https://img.shields.io/badge/Pyrogram-Latest-green.svg)](https://docs.pyrogram.org/)
[![Docker](https://img.shields.io/badge/Docker-Ready-blue.svg)](https://www.docker.com/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

**Smart Prioritization • Multiple Recipients • Intelligent Balance Management**

[Features](#-features) • [Installation](#-installation) • [Usage](#-usage) • [Contributing](#-contributing)

[العربية](README-ar.md) | [English](#-girt-hunter)

</div>

---

## 📋 Table of Contents

- [Overview](#-overview)
- [Features](#-features)
- [Requirements](#-requirements)
- [Installation](#-installation)
- [Configuration](#-configuration)
- [Usage](#-usage)
- [Project Structure](#-project-structure)
- [Technologies Used](#-technologies-used)
- [Contributing](#-contributing)
- [License](#-license)

---

## 🎯 Overview

**Girt Hunter** is an advanced automated Telegram userbot for purchasing gifts with smart prioritization, multiple recipients support, and intelligent balance management. Built with Python and Pyrogram with full Docker support and modern observability features.

### ✨ Why Girt Hunter?

- 🤖 **Fully Automated** - No manual intervention needed
- 🎯 **Smart Prioritization** - Fully customizable priority system
- 💰 **Smart Management** - Automatic balance and transaction tracking
- 🐳 **Easy Deployment** - Full Docker support

---

## 🌟 Features

### 🚀 Main Features

| Feature | Description |
|---------|-------------|
| 🤖 **Automated Purchasing** | Automatically purchase gifts without manual intervention |
| 🎯 **Smart Priority System** | Customizable purchase priorities based on configurable criteria |
| 👥 **Multiple Recipients** | Send gifts to multiple people simultaneously |
| 💰 **Smart Balance Management** | Automatic balance tracking and management |
| 📊 **Monitoring & Observability** | Structured logging and performance monitoring |
| 🔒 **Secure** | Data validation using Pydantic |

### 🛠️ Technical Features

- ✅ Docker and Docker Compose support
- ✅ Structured Logging
- ✅ SQLite Database
- ✅ Multi-language Support
- ✅ Configuration Management

---

## 📦 Requirements

Before starting, make sure you have installed:

- **Python** 3.8 or higher
- **Docker** (optional for deployment)
- **Telegram API** credentials
- **Git**

---

## 🚀 Installation

### Method 1: Standard Installation

```bash
# 1. Clone the repository
git clone https://github.com/3bkader-gpt/Girt_hunter.git
cd Girt_hunter

# 2. Create a virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# 3. Install requirements
pip install -r requirements.txt

# 4. Set up environment file
cp .env.example .env
# Edit .env file with your credentials

# 5. Run the bot
python main.py
```

### Method 2: Using Docker (Recommended)

```bash
# Clone the repository
git clone https://github.com/3bkader-gpt/Girt_hunter.git
cd Girt_hunter

# Set up environment file
cp .env.example .env
# Edit .env file

# Run using Docker Compose
docker-compose up -d

# View logs
docker-compose logs -f
```

---

## ⚙️ Configuration

### `.env` File

```env
# Telegram API
API_ID=your_api_id
API_HASH=your_api_hash
PHONE_NUMBER=your_phone_number

# Database
DATABASE_PATH=./data/girt_hunter.db

# Logging
LOG_LEVEL=INFO
```

### `config.yaml` File

Edit `config.yaml` to customize bot behavior:

```yaml
priorities:
  - criteria: "price"
    weight: 0.5
  - criteria: "availability"
    weight: 0.3

recipients:
  - user_id: 123456789
    priority: high
  - user_id: 987654321
    priority: medium

balance:
  min_threshold: 100
  auto_refill: true
```

---

## 📖 Usage

### After Starting

After running the bot, it will automatically:

1. ✅ **Monitor Available Gifts** - Continuous checking for new gifts
2. ✅ **Automatic Purchasing** - Purchase gifts according to set priorities
3. ✅ **Automatic Sending** - Send gifts to recipients
4. ✅ **Balance Tracking** - Monitor balance and transactions

### Available Commands

| Command | Description |
|--------|-------------|
| `/start` | Start the bot |
| `/status` | Current bot status |
| `/balance` | Show current balance |
| `/history` | Transaction history |
| `/settings` | Bot settings |

---

## 📁 Project Structure

```
Girt_hunter/
├── 📂 app/                 # Main application code
│   ├── handlers/           # Event handlers
│   ├── services/           # Services
│   └── utils/              # Utilities
├── 📂 src/                 # Source code
├── 📂 data/                # Data files
├── 📂 locales/             # Translation files
├── 📂 scripts/             # Helper scripts
├── 📂 tests/               # Tests
├── 📄 config.yaml          # Configuration file
├── 📄 main.py              # Main entry point
├── 📄 requirements.txt     # Requirements
├── 🐳 Dockerfile           # Docker file
└── 🐳 docker-compose.yml   # Docker Compose setup
```

---

## 🛠️ Technologies Used

<div align="center">

| Technology | Description |
|------------|-------------|
| ![Python](https://img.shields.io/badge/Python-3.8+-3776AB?logo=python&logoColor=white) | Main programming language |
| ![Pyrogram](https://img.shields.io/badge/Pyrogram-Latest-0088CC?logo=telegram&logoColor=white) | Telegram API library |
| ![Pydantic](https://img.shields.io/badge/Pydantic-Latest-E92063?logo=pydantic&logoColor=white) | Data validation |
| ![SQLite](https://img.shields.io/badge/SQLite-3-003B57?logo=sqlite&logoColor=white) | Database |
| ![Docker](https://img.shields.io/badge/Docker-Ready-2496ED?logo=docker&logoColor=white) | Containers |

</div>

---

## 🤝 Contributing

Contributions are welcome! 🎉

### How to Contribute

1. 🍴 Fork the project
2. 🌿 Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. 💾 Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. 📤 Push to the branch (`git push origin feature/AmazingFeature`)
5. 🔄 Open a Pull Request

### Contribution Guidelines

- Follow existing code standards
- Add tests for new features
- Ensure all tests pass
- Update documentation as needed

---

## 📄 License

This project is licensed under the [MIT License](LICENSE) - see the LICENSE file for details.

---

## 📞 Contact & Support

- 🐛 **Report Issues**: [Open an Issue](https://github.com/3bkader-gpt/Girt_hunter/issues)
- 💡 **Suggest Features**: [Open an Issue](https://github.com/3bkader-gpt/Girt_hunter/issues)
- 📧 **Email**: medo.omar.salama@gmail.com

---

<div align="center">

**Made with ❤️ by [Mohamed Omar](https://github.com/3bkader-gpt)**

⭐ If you like this project, don't forget to give it a star!

[⬆ Back to Top](#-girt-hunter)

</div>