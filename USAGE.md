# Usage Guide - Bot Generator

## Quick Start

### 1. Start the Generator Bot

```bash
python main.py
```

### 2. Open Telegram

- Find your bot (username you set)
- Send `/start`
- You'll see the welcome menu

## Available Commands

### `/start`
Show welcome message and command list.

```
🤖 Welcome to Telegram Bot Generator!
I can help you create custom Telegram bots using AI.
```

### `/generate`
Start the bot generation wizard.

```
Usage: /generate
Then describe your bot in the next message
```

### `/list`
Show all currently running bots.

```
📋 Running Bots:
• WeatherBot (ID: a1b2c3d4)
  Status: running
  Started: 2024-12-23 20:15:30
```

### `/status`
Show detailed status of all bots.

```
📊 All Bots Status:
🟢 WeatherBot
   ID: a1b2c3d4
   Status: running
```

### `/stop <bot_name>`
Stop a running bot.

```
Usage: /stop WeatherBot
Response: ✅ Bot 'WeatherBot' stopped successfully.
```

### `/help`
Show detailed help message.

## Bot Generation Workflow

### Step 1: Send `/generate`

```
User: /generate
```

### Step 2: Wait for Prompt

```
Bot: 🤖 Bot Generator - Describe Your Bot

Tell me what kind of bot you want to create. Be specific about:
• What the bot does
• Main features
• How users interact with it
```

### Step 3: Describe Your Bot

Be specific and detailed. The better your description, the better the generated bot.

```
User: Create a joke bot that:
- Sends a random joke when user types /joke
- Tracks how many jokes each user has requested
- Shows statistics with /stats command
- Makes users laugh with different joke categories
```

### Step 4: Wait for Generation

The bot will:
1. Parse your description
2. Generate Python code
3. Validate the code
4. Show you a preview

```
Bot: ⏳ Generating bot code...
This may take a few moments as I:
1. Analyze your description
2. Generate Python code
3. Validate the code
4. Prepare for launch
```

### Step 5: Review & Launch

You'll see:
- Generated code preview
- Two buttons: ✅ Launch Bot and ❌ Cancel

```
Bot: ✅ Bot code generated successfully!

Bot Name: JokeBot
Code Length: 3,847 characters

Code Preview:
```python
[code snippet...]
```
```

Click **✅ Launch Bot** to deploy it.

### Step 6: Bot is Live!

You'll get confirmation:

```
Bot: ✅ Bot 'JokeBot' launched successfully!

Bot ID: a1b2c3d4
Status: running
Created: 2024-12-23 20:15:30

💡 Next steps:
1. Replace the token placeholder in the bot code
2. Use /list to see all your bots
3. Use /status to check bot details
```

## Example Bot Descriptions

### Example 1: Weather Bot 🌤️

```
Create a weather bot that:
- Accepts city names from users
- Fetches real weather data (or simulates it)
- Shows temperature in both Celsius and Fahrenheit
- Displays weather condition with appropriate emoji (☀️ for sunny, 🌧️ for rainy, etc.)
- Provides humidity and wind speed information
- Keeps a history of user queries
- Has /help command explaining usage
```

### Example 2: Quote Bot 📖

```
Create an inspirational quotes bot that:
- Sends a random quote when user types /quote
- Lets users search quotes by author with /author <name>
- Shows quote statistics with /stats
- Allows users to favorite quotes with inline buttons
- Tracks favorited quotes per user
- Sends daily inspirational quote at noon
- Has command suggestions in /help
```

### Example 3: Code Review Bot 💻

```
Create a code review helper bot that:
- Takes Python code snippets from users
- Analyzes code quality and suggests improvements
- Points out potential bugs and security issues
- Provides optimization suggestions
- Explains what complex code does in simple terms
- Shows better approaches with examples
- Rates code quality on a scale of 1-10
- Saves review history per user
```

### Example 4: Music Recommendation Bot 🎵

```
Create a music recommendation bot that:
- Accepts artist names from users
- Returns 5 similar artists for each input
- Shows album covers as emoji if available
- Keeps conversation history
- Learns user preferences (rock, pop, etc.)
- Provides playlist suggestions
- Rates recommendations user gives feedback on
- Shares top recommended artists
```

### Example 5: Todo List Bot ✅

```
Create a todo list bot where users can:
- Add tasks with /add <task>
- View tasks with /list
- Mark tasks done with /done <task_id>
- Remove tasks with /remove <task_id>
- Get a summary with /summary
- Set task priorities (high, medium, low)
- Get reminders for high-priority tasks
- Export todo list as text
```

## Tips for Better Bots

### 1. Be Specific

❌ Bad: "Create a bot"
✅ Good: "Create a translator bot that translates user input to English and Spanish"

### 2. Describe Features Clearly

❌ Bad: "Bot that does stuff"
✅ Good: "Bot with /start, /help, /translate commands that..."

### 3. Include User Interaction Flow

❌ Bad: "Weather bot"
✅ Good: "Weather bot where user types city name, bot returns temperature and conditions"

### 4. Add Specific Requirements

❌ Bad: "Music bot"
✅ Good: "Music bot with search, playlists, favorites, and user statistics"

### 5. Mention Output Format

❌ Bad: "Show info"
✅ Good: "Show info with emojis, formatted as: 🌡️ Temp: 20°C, 💨 Wind: 5m/s"

## Managing Generated Bots

### View All Bots

```bash
/list
```

Shows running bots with:
- Bot name
- Status
- Start time

### Check Detailed Status

```bash
/status
```

Shows for each bot:
- Status indicator (🟢 running, 🔴 stopped, ❌ error)
- Bot name and ID
- Creation and start times
- Uptime
- Any error messages

### Stop a Bot

```bash
/stop BotName
```

Gracefully terminates the bot process.

### View Generated Code

Generated bot files are saved in `generated_bots/` directory:

```
generated_bots/
├── bot_weatherbot_20241223_201530.py
├── bot_jokebot_20241223_202015.py
└── bot_quotebot_20241223_203000.py
```

You can:
- Review the generated code
- Modify it for production use
- Share it with others
- Deploy it elsewhere

## Customization

### Edit Generated Bot Code

1. Find the bot file in `generated_bots/` folder
2. Open with your text editor
3. Modify as needed
4. Test locally

### Add Custom Features

Edit the generated bot file to:
- Add more commands
- Integrate external APIs
- Add database storage
- Implement user authentication
- Add more complex logic

### Replace Token Placeholder

Generated bots include a placeholder token:

```python
token = "1234567890:ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijk"
```

Replace with your actual bot token from @BotFather.

## Advanced Usage

### Deploy Bot Elsewhere

Generated bots are standalone Python scripts that can be:
- Run on VPS/dedicated server
- Deployed on cloud platforms (Heroku, AWS, DigitalOcean)
- Containerized with Docker
- Integrated into larger systems

### Monitor Bots

Check logs for each bot:

```bash
# View bot output
tail -f generated_bots/bot_*.log
```

### Backup Bots

```bash
# Backup generated bots
cp -r generated_bots/ backup_bots_$(date +%Y%m%d)
```

## Troubleshooting

### Bot Generation Failed

**Check:**
- Internet connection
- OnlySq API key validity
- Bot description (too short?)

**Try:**
- Rewrite description more clearly
- Use simpler language
- Be more specific

### Bot Won't Start

**Check:**
- Bot code is valid Python
- All imports are available
- Token format is correct

**Fix:**
- Review generated code for errors
- Install missing dependencies
- Check token from @BotFather

### Bot Stops Unexpectedly

**Check:**
- System logs for errors
- Bot code for infinite loops
- Resource usage (CPU/memory)

**Fix:**
- Restart the bot
- Optimize the code
- Add error handling

## Performance Notes

- Each bot runs as separate process
- Default limit: 10 concurrent bots
- Modify `MAX_CONCURRENT_BOTS` in `config.py` to increase
- More bots = higher system resource usage

## Security Notes

⚠️ **Important:**
- Always review generated code before production use
- Never expose bot tokens in public repositories
- Use environment variables for sensitive data
- Validate user inputs in bots
- Implement rate limiting if needed

---

**Ready to generate awesome bots? Start with `/generate`! 🚀**
