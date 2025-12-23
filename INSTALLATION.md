# Installation & Setup Guide

## Prerequisites

Before you start, make sure you have:

- **Python 3.8 or higher** - [Download here](https://www.python.org/downloads/)
- **pip** - Usually comes with Python
- **git** - [Download here](https://git-scm.com/)
- **Telegram Bot Token** - Get it from [@BotFather](https://t.me/botfather) on Telegram
- **OnlySq API Key** - Get it free from [OnlySq Docs](https://docs.onlysq.ru/)

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
- `openai` - For OnlySq API compatibility
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
# Edit with your text editor

# On macOS/Linux
nano .env
```

**Fill in your credentials:**
```env
# Get this from @BotFather on Telegram
MAIN_BOT_TOKEN=YOUR_BOT_TOKEN_HERE

# Get this from https://docs.onlysq.ru/
ONLYSQ_API_KEY=YOUR_API_KEY_HERE

# Keep these as default
ONLYSQ_BASE_URL=https://api.onlysq.ru/v1
ONLYSQ_MODEL=gpt-4o

# Optional settings
BOT_PORT=8000
LOG_LEVEL=INFO
```

### 5. Verify Installation

```bash
python -c "import telegram; print('✓ python-telegram-bot installed')"
python -c "import openai; print('✓ openai installed')"
python -c "from dotenv import load_dotenv; print('✓ python-dotenv installed')"
```

If all commands show checkmarks, you're ready to go!

## Getting Required Tokens

### Telegram Bot Token

1. Open Telegram and search for **@BotFather**
2. Send `/start` command
3. Send `/newbot` command
4. Choose a name for your bot (e.g., "My Bot Generator")
5. Choose a username (must end with "bot", e.g., "my_bot_generator_bot")
6. Copy the token that BotFather gives you
7. Paste it in `.env` as `MAIN_BOT_TOKEN`

### OnlySq API Key

1. Visit [OnlySq Documentation](https://docs.onlysq.ru/)
2. Sign up for a free account (if not already signed up)
3. Get your API key from the dashboard
4. Paste it in `.env` as `ONLYSQ_API_KEY`

## Running the Application

### Option 1: Direct Python

```bash
python main.py
```

You should see output like:
```
2024-12-23 20:00:00,123 - root - INFO - Starting Telegram Bot Generator...
2024-12-23 20:00:01,456 - root - INFO - Bot Generator started and ready to accept commands!
2024-12-23 20:00:01,789 - root - INFO - Bot token: 1234567890:ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijk20...
```

### Option 2: With Logging

```bash
python main.py > bot.log 2>&1 &
```

## Troubleshooting

### Error: "ModuleNotFoundError: No module named 'telegram'"

**Solution:** Install dependencies again:
```bash
pip install -r requirements.txt
```

### Error: "MAIN_BOT_TOKEN is required"

**Solution:** Check your `.env` file:
1. Make sure `.env` file exists
2. Make sure you set `MAIN_BOT_TOKEN`
3. Make sure token format is correct (numbers:letters)
4. No spaces around the `=` sign

### Error: "ONLYSQ_API_KEY is required"

**Solution:**
1. Visit [OnlySq Docs](https://docs.onlysq.ru/)
2. Get your API key
3. Add it to `.env`

### Error: "Connection refused" or timeout

**Solution:**
1. Check your internet connection
2. Check if OnlySq API is accessible: `ping api.onlysq.ru`
3. Check if Telegram API is accessible

### Bot doesn't respond to commands

**Solution:**
1. Make sure bot is running (you should see logs)
2. In Telegram, send `/start` to your bot
3. Check that `MAIN_BOT_TOKEN` is correct
4. Look at console logs for errors

## Next Steps

1. **Test the bot:**
   - Start bot with `python main.py`
   - Open Telegram and find your bot
   - Send `/start` command
   - Send `/generate` to create your first bot
   - Describe what bot you want in 1-2 sentences

2. **View logs:**
   - Watch console output for any errors
   - Generated bots are saved in `generated_bots/` directory

3. **Advanced usage:**
   - Check `README.md` for more commands
   - Modify `bot_templates.py` for custom templates
   - Extend `bot_generator.py` for better generation

## Uninstallation

To remove the project:

```bash
# Deactivate virtual environment
deactivate

# Remove the directory
rm -rf telegram-bot-generator

# On Windows:
rmdir /s telegram-bot-generator
```

## Getting Help

- **Issues:** Open an issue on GitHub
- **Questions:** Check README.md first
- **OnlySq Support:** Visit [OnlySq Community](https://t.me/onlysq)
- **Telegram Bot Framework:** See [python-telegram-bot docs](https://python-telegram-bot.readthedocs.io/)

## Tips for Success

1. **Start simple** - Begin with basic bot descriptions
2. **Check logs** - Look at console output for errors
3. **Test locally** - Make sure everything works before deploying
4. **Use good descriptions** - More detailed = better generated code
5. **Review generated code** - Check the generated code before using in production

---

**Happy bot generating! 🤖**
