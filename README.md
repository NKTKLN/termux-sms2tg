# 📲 Termux SMS to Telegram

**termux_sms2tg** is a Python-based utility that monitors SMS messages and incoming calls on Android through **Termux API** and forwards new events to a **Telegram chat**.

The project runs in a polling loop, reads records from Termux commands, filters already processed events by hash, and sends notifications via a Telegram bot.

## 📦 Requirements

Before installation, make sure you have:

* An Android device
* [Termux](https://f-droid.org/packages/com.termux/)
* [Termux:API](https://f-droid.org/en/packages/com.termux.api/)
* Telegram bot token
* Telegram chat ID

## ⚙️ Setup

### 📱 Install Android apps

Install these applications from F-Droid:

* [Termux](https://f-droid.org/packages/com.termux/)
* [Termux:API](https://f-droid.org/en/packages/com.termux.api/)

After installation, open **Termux:API** and grant all required permissions, especially for:

* SMS
* Call logs
* Notifications, if requested

## 🛠️ Installation

### 💻 Prepare environment in Termux

Update packages:

```bash
pkg update
```

Install required system packages:

```bash
pkg install termux-api git python
```

Clone the repository:

```bash
git clone https://github.com/NKTKLN/termux-sms2tg
```

Go to the project directory:

```bash
cd termux-sms2tg
```

Create a virtual environment if desired:

```bash
python -m venv .venv
source .venv/bin/activate
```

Install Python dependencies:

```bash
pip install -r requirements.txt
```

If you use `pyproject.toml` instead of `requirements.txt`, install the project dependencies with:

```bash
pip install .
```

or for development:

```bash
pip install -e .
```

## 🔐 Configuration

Before running the application, configure the project variables.

Typically you need to set:

* Telegram bot token
* Telegram chat ID
* Termux command settings
* Optional Telegram proxy
* Path to the hash storage file

You can do this in `src/termux_sms2tg/config.py`:

```py
HASH_FILE = "hash.json"

BOT_TOKEN = "your_bot_token_here"
CHAT_ID = 123456789
```

Make sure the bot is added to the target chat and allowed to send messages.

## ▶️ Run

Start the application with Python:

```bash
python -m src.termux_sms2tg.main
```

## ⚠️ Notes

* `Termux:API` must be installed, otherwise Termux API commands will not work
* Android permissions must be granted manually
* The script uses polling, so it should remain running in Termux
* Processed records are stored using hashes to avoid duplicate notifications
* If Telegram is blocked in your region, you may need to configure a proxy

## 📜 License

This project is licensed under the MIT License. See the [LICENSE](./LICENSE.md) file for details.
