[![Plaza Casino](https://img.shields.io/badge/Plaza%20Casino-Demo%20Project-2D2D2D?style=for-the-badge&logo=telegram&logoColor=FFFFFF)](https://github.com/Lonewolf239/PlazaCasino)
[![Python](https://img.shields.io/badge/Python-3.10+-2D2D2D?style=for-the-badge&logo=python&logoColor=FFFFFF)](https://python.org)
[![aiogram](https://img.shields.io/badge/aiogram-3.x-2D2D2D?style=for-the-badge&logo=telegram&logoColor=FFFFFF)](https://docs.aiogram.dev/)
[![MIT](https://img.shields.io/badge/License-MIT-2D2D2D?style=for-the-badge&logo=heart&logoColor=FFFFFF)](LICENSE)

[![EN](https://img.shields.io/badge/README-EN-2D2D2D?style=for-the-badge&logo=github&logoColor=FFFFFF)](README.md)
[![RU](https://img.shields.io/badge/README-RU-2D2D2D?style=for-the-badge&logo=google-translate&logoColor=FFFFFF)](README-RU.md)

# Plaza Casino — Telegram Casino Bot (Demo)

> **⚠️ LEGAL DISCLAIMER:** This project is **purely educational** and **not intended for real-world use**.  
> All API keys and secrets have been removed. The code is provided to demonstrate architectural patterns, asynchronous programming, and integration with payment systems.  
> **Do not use this code to operate a real casino.** Gambling regulations vary by country; you are solely responsible for complying with your local laws.

Plaza Casino is a feature-rich Telegram bot that simulates a full-fledged casino experience. It includes multiple games, a referral system with clone bots, cryptocurrency payments (via Crypto Pay), an admin panel, and many other advanced features.

---

## Features

| | Feature | Details |
|---|---------|---------|
| 🎰 | **8+ Games** | Slots (classic and 3×3), Roulette, Dice, Lottery, Mines, Hi-Lo, Blackjack, Crash |
| 💰 | **Crypto Payments** | Integrated with Crypto Pay API (TON, USDT, BTC, etc.) — deposits and withdrawals |
| 👥 | **Referral System** | Create your own clone bots; earn 5% from bets and 2% from wins of referred users |
| 🛡️ | **Admin Panel** | Manage users, view logs, configure games, send announcements, and more |
| 🌐 | **Localization** | Full Russian/English language support |
| 👻 | **Phantom Players** | Simulated players post fake wins to keep the channel active |
| 📊 | **Profit Analytics** | Charts of casino profit and withdrawal history (matplotlib) |
| 🖼️ | **Rich Graphics** | Games with custom-generated PNG images (Pillow) |
| 🧩 | **Modular Architecture** | Clean separation of games, handlers, database, and payments |

---

## Tech Stack

- **Language:** Python 3.10+
- **Framework:** aiogram (3.x)
- **Asynchronous Server:** aiohttp (for webhooks)
- **Database:** aiosqlite (SQLite with async support)
- **Payments:** Crypto Pay API (via aiocryptopay)
- **Graphics:** Pillow, matplotlib
- **External APIs:** CoinGecko (exchange rates), googletrans
- **Environment:** python-dotenv

---

## Quick Start (Local Testing Only)

### 1. Clone the repository
```bash
git clone https://github.com/Lonewolf239/PlazaCasino.git
cd PlazaCasino
```

### 2. Set up a virtual environment
```bash
python -m venv venv
source venv/bin/activate   # Linux/macOS
venv\Scripts\activate      # Windows
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure environment variables
Copy `dotenv_template` to `.env` and fill in your **test** tokens:
- `BOT_TOKEN` – from [@BotFather](https://t.me/botfather)
- `CRYPTOPAY_API_TOKEN` – from [@CryptoBot](https://t.me/CryptoBot) (use testnet if available)
- `ADMIN_IDS` – your Telegram user ID
- etc. (see `dotenv_template` for all required variables)

> **Never commit your real `.env` file!** The repository only contains `dotenv_template`.

### 5. Run the bot
```bash
python main.py
```

---

## Legal Disclaimer (Important)

- This software is provided **“as is”** for **educational and demonstration purposes only**.
- It is **not intended to be used as a real gambling platform**. All payment integrations are demonstrated with test keys and should not be used with real funds.
- The author **disclaims any liability** for damages or legal issues arising from the use of this code.
- **Gambling laws vary by jurisdiction.** You are solely responsible for ensuring that your use of this code complies with applicable laws.
- By using this code, you agree that you will not deploy it to offer real-money gambling services.

---

## License

This project is licensed under the **MIT License** – see the [LICENSE](LICENSE) file for details.  
The license does not grant permission to use this software for unlawful purposes, including the operation of an unlicensed gambling business.

---

## Author

**Lonewolf239**  
[GitHub](https://github.com/Lonewolf239) | [NeoIni](https://github.com/Lonewolf239/NeoIni) (another project)

---

*If you find this project useful for learning, feel free to ⭐ the repository!*
