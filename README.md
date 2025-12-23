# 🤖 Telegram Bot Generator

AI-powered Telegram bot generation and hosting platform. Create custom Telegram bots in seconds using natural language prompts!

## 🎯 Features

- 🧠 **AI-Powered Bot Generation** - Generate Telegram bots from text descriptions using OnlySq API
- 🚀 **Instant Deployment** - Automatically create, configure, and launch new bots
- 📦 **Bot Management** - List, monitor, and control all generated bots
- 🔌 **OpenAI-Compatible API** - Uses free OnlySq API with 40+ AI models (no API key needed!)
- 🔓 **JSON Database** - All bot metadata stored locally in JSON file on your PC
- 🧩 **Modular Architecture** - Easy to extend and customize
- 🛡️ **Secure Execution** - Generated code validation and security checks
- 🎨 **Smart Code Generation** - Intelligent bot code generation with error handling

## 🔐 Why No API Key?

OnlySq provides a **free tier** that doesn't require an API key! You get instant access to:
- GPT-4o
- Claude 3.5 Sonnet
- Gemini 2.5
- DeepSeek-R1
- Llama 4
- And 35+ other models

No registration, no API key, completely free.

## Quick Start

### Prerequisites

- Python 3.8+
- pip
- Telegram Bot Token (from [@BotFather](https://t.me/botfather))

### Installation

```bash
# Clone repository
git clone https://github.com/SignalScp/telegram-bot-generator.git
cd telegram-bot-generator

# Install dependencies
pip install -r requirements.txt

# Copy and configure environment
cp .env.example .env
# Edit .env with your Telegram bot token
```

### Configuration

Edit `.env` file:

```env
# Get this from @BotFather on Telegram
MAIN_BOT_TOKEN=your_main_bot_token_here

# OnlySq API (free tier - no key needed!)
ONLYSQ_BASE_URL=https://api.onlysq.ru/v1
ONLYSQ_MODEL=gpt-4o-mini

# Database will be created automatically
DATABASE_FILE=bots_database.json
```

### Usage

```bash
python main.py
```

Then in Telegram:

```
/start       - Show welcome message
/generate    - Create a new bot
/list        - Show your bots
/status      - Show detailed status
/stop <name> - Stop a bot
/stats       - Show database statistics
/help        - Show help
```

## How It Works

### 1. Generate Bot
```
User: /generate
Bot: "Describe your bot"
User: "Create a weather bot that shows temperature and humidity"
```

### 2. AI Creates Code
```
BotGenerator (using OnlySq free tier):
✓ Parse description
✓ Generate Python code
✓ Validate syntax
✓ Save to database
```

### 3. Launch Bot
```
User: [clicks Launch]

Executor:
✓ Save code file
✓ Create process
✓ Update database
✓ Bot is running!
```

### 4. Manage Bots
```
User: /list
Bot shows all your bots with status

User: /stop WeatherBot
Bot gracefully terminates the bot
```

## Database Structure

Your bots are stored in `bots_database.json` on your PC:

```json
{
  "metadata": {
    "version": "1.0",
    "created_at": "2024-12-23T20:00:00",
    "updated_at": "2024-12-23T20:15:00"
  },
  "bots": {
    "a1b2c3d4": {
      "bot_id": "a1b2c3d4",
      "name": "WeatherBot",
      "description": "Shows weather data",
      "user_id": 123456789,
      "status": "running",
      "code_file": "generated_bots/bot_a1b2c3d4.py",
      "code_length": 3847,
      "created_at": "2024-12-23T20:00:00",
      "updated_at": "2024-12-23T20:05:00"
    }
  }
}
```

## Example Bot Descriptions

### Weather Bot
```
Create a weather bot that:
- Accepts city names from users
- Shows temperature in °C and °F
- Shows weather emoji (☀️ 🌧️ 🜋)
- Shows humidity and wind speed
- Keeps query history
```

### Joke Bot
```
Create a joke bot that:
- Sends random jokes with /joke
- Has joke categories
- Tracks jokes per user
- Shows statistics with /stats
- Rates jokes you like/dislike
```

### Code Helper Bot
```
Create a Python code review bot that:
- Takes code snippets
- Suggests optimizations
- Points out bugs
- Explains complex code
- Rates code quality
```

## Architecture

```
┌─────────────────┐
│  Main Generator Bot │ (/generate, /list, /status)
└────────┬────────┘
         │
    ┌─────────────────────┐
    │  BotGenerator (OnlySq API)│
    │  - Parse description    │
    │  - Generate code         │
    │  - Validate syntax       │
    └────────┬───────────┘
         │
    ┌─────────────────────┐
    │  JSONDatabase           │
    │  - Store bot metadata    │
    │  - Track status          │
    │  - User bot association  │
    └────────┬───────────┘
         │
    ┌─────────────────────┐
    │  BotExecutor            │
    │  - Launch processes      │
    │  - Monitor bots          │
    │  - Stop/terminate        │
    └─────────────────────┘
```

## Project Structure

```
telegram-bot-generator/
├── main.py                 # Main bot application
├── config.py              # Configuration
├── database.py            # JSON database manager
├── bot_generator.py       # AI code generation
├── bot_executor.py        # Bot process manager
├── bot_templates.py       # Code templates
├── onlysq_client.py       # OnlySq API wrapper
├── utils.py               # Utilities
├── generated_bots/        # Generated bot files
├── bots_database.json     # Bot database (auto-created)
├── requirements.txt       # Python dependencies
├── .env.example          # Configuration template
├── .gitignore            # Git ignore
├── README.md             # This file
├── INSTALLATION.md       # Setup guide
├── USAGE.md              # Usage guide
├── LICENSE               # MIT License
└── PROJECT_SUMMARY.md    # Architecture overview
```

## Key Features

### 🔗 OnlySq Free API
- No API key required
- 40+ AI models
- Free tier fully functional
- Fast responses

### 📁 JSON Database
- All data stored locally
- No cloud dependencies
- Easy backup (just copy the file)
- Human-readable format
- Database statistics

### 🤠 User Management
- Each user has their own bots
- Isolated bot management
- Per-user statistics
- Private bot data

### 💾 Bot Control
- Create bots from descriptions
- Save for later use
- Launch with one click
- Real-time status monitoring
- Graceful shutdown

## Commands Reference

| Command | Description | Example |
|---------|-------------|----------|
| `/start` | Welcome message | `/start` |
| `/generate` | Create new bot | `/generate` |
| `/list` | Show your bots | `/list` |
| `/status` | Detailed bot status | `/status` |
| `/stop` | Stop a bot | `/stop WeatherBot` |
| `/stats` | Database statistics | `/stats` |
| `/help` | Show help | `/help` |

## Requirements

- Python 3.8+
- python-telegram-bot 21.1+
- httpx
- python-dotenv
- Other dependencies in requirements.txt

## Installation

See [INSTALLATION.md](INSTALLATION.md) for detailed setup instructions.

## Usage Guide

See [USAGE.md](USAGE.md) for examples and detailed usage.

## Security

⚠️ **Important:**
- Generated code is validated before execution
- Dangerous imports are detected
- Your bot tokens are not stored in the database
- All data stays on your PC

## Troubleshooting

**Bot token not working?**
- Verify it's correct from @BotFather
- Check .env file has no spaces around `=`

**OnlySq API not responding?**
- Check internet connection
- Verify `ONLYSQ_BASE_URL` is correct
- Try again (API may be temporarily slow)

**Database file corrupted?**
- Delete `bots_database.json`
- Restart the bot (it will recreate it)

## Contributing

Contributions welcome!

## License

MIT License - Free for personal and commercial use

## Support

- 📧 GitHub Issues: Report bugs
- 💬 GitHub Discussions: Ask questions
- 📚 Documentation: Check README, USAGE, INSTALLATION

## Future Enhancements

- [ ] Web dashboard for bot management
- [ ] Bot templates marketplace
- [ ] Multi-language bot generation
- [ ] Docker containerization
- [ ] Kubernetes deployment
- [ ] Advanced analytics
- [ ] Bot versioning
- [ ] Automated backups

---

**Made with ❤️ by SignalScp**

**Version:** 2.0 (JSON Database Edition)
