# 🤖 Telegram Bot Generator

AI-powered Telegram bot generation and hosting platform. Create custom Telegram bots in seconds using natural language prompts!

## Features

- 🧠 **AI-Powered Bot Generation** - Generate Telegram bots from text descriptions using OnlySq API
- 🚀 **Instant Deployment** - Automatically create, configure, and launch new bots
- 📦 **Bot Management** - List, monitor, and control all generated bots
- 🔌 **OpenAI-Compatible API** - Uses free OnlySq API with 40+ AI models
- 🧩 **Modular Architecture** - Easy to extend and customize
- 🛡️ **Sandbox Execution** - Secure isolated execution of generated bots
- 🎨 **Code Generation** - Intelligent bot code generation with error handling

## Quick Start

### Prerequisites

- Python 3.8+
- pip
- Telegram Bot Token (for the generator bot)
- OnlySq API Key (free at https://docs.onlysq.ru)

### Installation

```bash
# Clone repository
git clone https://github.com/SignalScp/telegram-bot-generator.git
cd telegram-bot-generator

# Install dependencies
pip install -r requirements.txt

# Copy and configure environment
cp .env.example .env
# Edit .env with your tokens
```

### Configuration

Create `.env` file:

```env
# Main Bot Token (the bot that generates other bots)
MAIN_BOT_TOKEN=your_main_bot_token_here

# OnlySq API Configuration
ONLYSQ_API_KEY=your_onlysq_api_key_here
ONLYSQ_BASE_URL=https://api.onlysq.ru/v1
ONLYSQ_MODEL=gpt-4o  # or any other available model

# Optional: Bot hosting configuration
BOT_PORT=8000
BOT_WEBHOOK_URL=https://your-domain.com  # For webhook mode
```

### Usage

#### Running the Main Bot

```bash
python main.py
```

The generator bot will start and listen for commands:

- `/start` - Show main menu
- `/generate` - Generate a new bot from description
- `/list` - List all running bots
- `/stop <bot_name>` - Stop a specific bot
- `/status` - Show all bots status

#### Example: Generate a Bot

Send to the bot:
```
/generate
```

Then describe what you want:
```
Create a weather bot that fetches current weather for any city and 
shows temperature, humidity, and wind speed in emoji format
```

The bot will:
1. Generate Python code using AI
2. Validate the generated code
3. Create bot configuration
4. Launch the bot
5. Report status and token

## Architecture

```
telegram-bot-generator/
├── main.py                 # Main generator bot entry point
├── config.py              # Configuration management
├── bot_generator.py       # AI-powered bot code generation
├── bot_executor.py        # Bot process management
├── bot_templates.py       # Base templates for generated bots
├── onlysq_client.py       # OnlySq API wrapper
├── database.py            # Bot metadata storage
├── utils.py               # Helper functions
├── generated_bots/        # Storage for generated bot files
│   └── bot_<timestamp>.py # Generated bot code
└── requirements.txt       # Python dependencies
```

## Core Components

### 1. Bot Generator (`bot_generator.py`)
Uses OnlySq API with GPT-4o to generate bot code from natural language prompts.

### 2. OnlySq Client (`onlysq_client.py`)
Wrapper around OnlySq API for easy model access.

### 3. Bot Executor (`bot_executor.py`)
Manages bot lifecycle: spawn, monitor, terminate processes.

### 4. Database (`database.py`)
SQLite database for tracking generated bots metadata.

## API Models Available

OnlySq API provides access to 40+ models:
- GPT-4o
- Claude 3.5 Sonnet
- Gemini 2.5
- DeepSeek-R1
- Llama 4
- Qwen3
- And more...

## Examples

### Example 1: Music Bot

```
/generate
Create a music recommendation bot that:
- Accepts artist names
- Returns 5 similar artists
- Shows album covers as emojis
- Keeps conversation history
```

### Example 2: Code Helper Bot

```
/generate
Create a Python code review bot that:
- Takes code snippets
- Provides optimization suggestions
- Explains what the code does
- Shows better approaches with examples
```

## Limitations

- Generated bots run on the same machine/process
- Maximum concurrent bots limited by system resources
- Generated code is sandboxed but untrusted code should be reviewed
- Each bot requires unique token management

## Advanced Usage

### Custom Bot Templates

Extend `bot_templates.py` to add custom base templates for specific bot types.

### Integration with External APIs

Generated bots can be configured to use external APIs (weather, crypto, etc.)

### Webhook Mode

Configure webhook URL in `.env` for production deployment instead of polling.

## Security Considerations

⚠️ **Important:**
- Generated code from AI should be reviewed before production use
- Implement rate limiting for bot generation
- Validate all user inputs
- Use strong API keys and tokens
- Consider sandbox execution for untrusted prompts

## Contributing

Contributions welcome! Areas for improvement:
- Better error handling and validation
- More sophisticated code generation
- Bot versioning and rollback
- Web dashboard for bot management
- Kubernetes deployment support
- Multi-language bot generation

## License

MIT License - see LICENSE file

## Support

- 📧 Issues & Questions: GitHub Issues
- 💬 Discussions: GitHub Discussions
- 📱 Telegram: Join our community

## Roadmap

- [ ] Web dashboard for bot management
- [ ] Bot templates marketplace
- [ ] Advanced code generation with tree search
- [ ] Multi-language support
- [ ] Docker containerization
- [ ] Kubernetes deployment
- [ ] Analytics and monitoring dashboard
- [ ] Bot monetization framework

---

**Made with ❤️ by SignalScp**
