# Installation & Setup Guide

## Prerequisites

Before you start, make sure you have:

- **Python 3.8 or higher** - [Download here](https://www.python.org/downloads/)
- **pip** - Usually comes with Python
- **git** - [Download here](https://git-scm.com/)
- **Telegram Bot Token** - Get it from [@BotFather](https://t.me/botfather) on Telegram

## Step-by-Step Installation

### 1. Clone the Repository

```bash
git clone https://github.com/SignalScp/telegram-bot-generator.git
cd telegram-bot-generator
```

### 2. Create Virtual Environment (Recommended)

**On Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

**On macOS/Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

You should see `(venv)` at the beginning of your terminal line.

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

This will install:
- `python-telegram-bot` - Telegram bot framework
- `httpx` - HTTP client for OnlySq API
- `python-dotenv` - Environment variable management
- And other required packages

### 4. Setup Environment Variables

**Copy the example file:**
```bash
cp .env.example .env
```

**Edit `.env` file with your credentials:**
```bash
# On Windows
echo. > .env
# Then edit with your text editor

# On macOS/Linux
nano .env
```

**Fill in your credentials:**
```env
# Get this from @BotFather on Telegram
MAIN_BOT_TOKEN=YOUR_BOT_TOKEN_HERE

# OnlySq API (free tier - no API key needed!)
ONLYSQ_BASE_URL=https://api.onlysq.ru/v1
ONLYSQ_MODEL=gpt-4o-mini

# Database will be created automatically
DATABASE_FILE=bots_database.json

# Optional settings
BOT_PORT=8000
LOG_LEVEL=INFO
```

### 5. Verify Installation

```bash
python -c "import telegram; print('✓ python-telegram-bot installed')"
python -c "import httpx; print('✓ httpx installed')"
python -c "from dotenv import load_dotenv; print('✓ python-dotenv installed')"
```

If all commands show checkmarks, you're ready to go!

## Getting Telegram Bot Token

### Step-by-Step

1. Open Telegram and search for **@BotFather**
2. Send `/start` command
3. Send `/newbot` command
4. Choose a name for your bot (e.g., "My Bot Generator")
5. Choose a username (must end with "bot", e.g., "my_bot_generator_bot")
6. Copy the token that BotFather gives you
7. Paste it in `.env` as `MAIN_BOT_TOKEN`

**Token Format Example:**
```
1234567890:ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijk
```

## Why No API Key?

OnlySq provides a **completely free tier** that doesn't require:
- ✅ API key registration
- ✅ Credit card
- ✅ Account creation
- ✅ Any authentication

Just use the free endpoint and you get access to 40+ AI models!

## Database Setup

The JSON database will be created automatically:

```json
bots_database.json  // Created on first run
```

This file stores:
- All bot metadata
- User-bot associations
- Bot status information
- Creation/modification timestamps

**Note:** The database is stored locally on your PC - no cloud storage needed!

## Running the Application

### Option 1: Direct Python

```bash
python main.py
```

You should see output like:
```
2024-12-23 20:00:00,123 - root - INFO - Starting Telegram Bot Generator...
2024-12-23 20:00:00,456 - root - INFO - Database file: bots_database.json
2024-12-23 20:00:01,789 - root - INFO - Bot Generator started and ready!
```

### Option 2: With Logging to File

```bash
python main.py > bot.log 2>&1 &
```

### Option 3: Using Python Module

```bash
python -m main
```

## Troubleshooting

### Error: "ModuleNotFoundError: No module named 'telegram'"

**Solution:** Install dependencies again:
```bash
pip install -r requirements.txt
```

If that doesn't work, try:
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### Error: "MAIN_BOT_TOKEN is required"

**Solution:** Check your `.env` file:
1. Make sure `.env` file exists in the same folder as `main.py`
2. Make sure you set `MAIN_BOT_TOKEN` (not `TELEGRAM_BOT_TOKEN`)
3. Make sure token format is correct (numbers:letters)
4. Make sure no spaces around the `=` sign

**Example correct format:**
```env
MAIN_BOT_TOKEN=1234567890:ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijk
```

### Error: "Connection refused" or timeout

**Solution:**
1. Check your internet connection
2. Check if OnlySq API is accessible: `ping api.onlysq.ru`
3. Try again (API may be temporarily busy)

### Error: "Database file corrupted"

**Solution:**
1. Delete `bots_database.json`
2. Restart the bot
3. Database will be recreated automatically

### Bot doesn't respond to commands

**Solution:**
1. Make sure bot is running (you should see logs)
2. In Telegram, send `/start` to your bot
3. Check that `MAIN_BOT_TOKEN` is correct
4. Look at console logs for errors
5. Try restarting the bot

## Next Steps

1. **Test the bot:**
   - Start bot with `python main.py`
   - Open Telegram and find your bot
   - Send `/start` command
   - Send `/generate` to create your first bot
   - Describe what bot you want in 1-2 sentences

2. **Check the database:**
   - Open `bots_database.json` with any text editor
   - You'll see your bot metadata in JSON format

3. **View logs:**
   - Watch console output for any errors
   - Generated bots are saved in `generated_bots/` directory

4. **Explore features:**
   - Use `/list` to see all your bots
   - Use `/status` for detailed information
   - Use `/stats` to see database statistics

## Deactivating Virtual Environment

When you're done:

```bash
deactivate
```

## Uninstallation

To remove the project:

```bash
# Deactivate virtual environment first
deactivate

# Remove the directory
rm -rf telegram-bot-generator

# On Windows:
rmdir /s telegram-bot-generator
```

## Getting Help

- **Issues:** Open an issue on GitHub
- **Questions:** Check README.md and USAGE.md first
- **OnlySq Support:** Visit [OnlySq Community](https://t.me/onlysq)
- **Telegram Bot Framework:** See [python-telegram-bot docs](https://python-telegram-bot.readthedocs.io/)

## Tips for Success

1. **Start simple** - Begin with basic bot descriptions
2. **Check logs** - Look at console output for errors
3. **Test locally** - Make sure everything works before using
4. **Use good descriptions** - More detailed = better generated code
5. **Review generated code** - Check the code before production use
6. **Backup database** - Keep copies of `bots_database.json`

## System Requirements

### Minimum
- Python 3.8
- 50MB free disk space
- 256MB RAM
- Internet connection

### Recommended
- Python 3.10+
- 200MB free disk space
- 512MB RAM
- Fast internet connection

## File Permissions

Make sure the bot has permission to:
- Read `.env` file
- Write to current directory (for database and bot files)
- Execute Python scripts

---

**Ready to start? Run `python main.py`! 🚀**
