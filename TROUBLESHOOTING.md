# Troubleshooting Guide

## Common Issues & Solutions

### ❌ RuntimeError: "Cannot close a running event loop"

**Error Message:**
```
RuntimeError: This event loop is already running
RuntimeError: Cannot close a running event loop
sys:1: RuntimeWarning: coroutine 'Application.shutdown' was never awaited
sys:1: RuntimeWarning: coroutine 'Application.initialize' was never awaited
```

**Cause:** This is a known issue with `python-telegram-bot` library and asyncio event loops on **Windows with Python 3.10+**. The problem occurs because the event loop is already running when the library tries to manage it.

**Solutions:**

#### Solution 1: Update to Latest Version (✅ RECOMMENDED)

Update both Python and the telegram library:

```bash
# Update Python to 3.12.1+
python --version

# Update python-telegram-bot
pip install --upgrade python-telegram-bot
```

#### Solution 2: Use Selector Event Loop (Already Fixed in v2.0)

The main.py now includes automatic fix for Windows:

```python
if sys.platform == 'win32':
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
```

This is **already implemented** in the latest version. Just update with:

```bash
git pull origin main
```

#### Solution 3: Downgrade to Python 3.9 (Temporary)

If you can't update, use Python 3.9:

```bash
# Uninstall current Python
# Download and install Python 3.9 from https://www.python.org/

# Verify
python --version
# Output: Python 3.9.x
```

#### Solution 4: Use ProactorEventLoop

Edit main.py and replace the Windows fix with:

```python
if sys.platform == 'win32':
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
```

**Note:** ProactorEventLoop is sometimes slower but more stable on older Windows versions.

### Step-by-Step Fix for Your Case

You're using **Python 3.12 on Windows**. Here's the exact fix:

#### Option A: Update Code (Quick Fix - Already Done)

✅ The latest version already includes the fix! Just update:

```bash
git pull origin main
pip install --upgrade -r requirements.txt
python main.py
```

#### Option B: Update Python (Permanent Fix)

1. **Check current version:**
   ```bash
   python --version
   # Shows: Python 3.12.x
   ```

2. **Download Python 3.12.1+** from [python.org](https://www.python.org/downloads/)

3. **Install with "Add Python to PATH" checked**

4. **Verify installation:**
   ```bash
   python --version
   # Should show: Python 3.12.1+
   ```

5. **Reinstall dependencies:**
   ```bash
   pip install --upgrade pip setuptools
   pip install -r requirements.txt
   ```

6. **Test it:**
   ```bash
   python main.py
   ```

#### Option C: Switch to Python 3.11 or 3.9

```bash
# Download Python 3.11 or 3.9 from python.org
# Install it

# Then run:
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python main.py
```

---

## Other Common Issues

### ❌ ModuleNotFoundError: No module named 'telegram'

**Fix:**
```bash
pip install python-telegram-bot httpx python-dotenv
```

Or reinstall from requirements:
```bash
pip install -r requirements.txt
```

### ❌ FileNotFoundError: .env file not found

**Fix:**
```bash
cp .env.example .env
# Edit .env with your bot token
```

### ❌ Error: "MAIN_BOT_TOKEN is required"

**Check:**
1. `.env` file exists in project directory
2. `MAIN_BOT_TOKEN` is set (not `TELEGRAM_BOT_TOKEN`)
3. Token format is correct: `1234567890:ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijk`
4. No spaces around `=` sign

**Example .env:**
```env
MAIN_BOT_TOKEN=1234567890:ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijk
ONLYSQ_BASE_URL=https://api.onlysq.ru/v1
ONLYSQ_MODEL=gpt-4o-mini
DATABASE_FILE=bots_database.json
```

### ❌ ConnectionError: API connection failed

**Possible causes:**
- Internet connection down
- OnlySq API temporarily unavailable
- Firewall blocking connection

**Fix:**
```bash
# Check internet connection
python -c "import socket; socket.create_connection(('8.8.8.8', 53))"

# Test OnlySq API
python -c "import httpx; print(httpx.get('https://api.onlysq.ru/v1/models').status_code)"

# Restart bot
python main.py
```

### ❌ Database file corrupted

**Fix:**
```bash
# Backup existing database
rename bots_database.json bots_database.json.bak

# Restart bot (will create new clean database)
python main.py
```

### ❌ Bot doesn't respond to commands

**Check:**
1. Bot is running (you see logs in console)
2. Bot token is correct (from @BotFather)
3. Internet connection is working
4. Try sending `/start` command
5. Wait 5 seconds and try again

**Debug:**
```bash
# Enable verbose logging
# Edit main.py and change:
logging.basicConfig(
    ...
    level=logging.DEBUG  # Change from INFO to DEBUG
)
```

### ❌ Permission denied on .env file

**Windows Fix:**
```bash
# Set permissions
icacls ".env" /grant:r %username%:F
```

**Linux/Mac Fix:**
```bash
chmod 600 .env
```

### ❌ Port already in use

**Windows:**
```bash
# Find process using port
netstat -ano | findstr :8000

# Kill process (replace PID with actual number)
taskkill /PID <PID> /F
```

**Linux/Mac:**
```bash
# Find process
lsof -i :8000

# Kill process
kill -9 <PID>
```

---

## Performance Issues

### Bot is slow to respond

**Causes:**
- OnlySq API is busy
- Network connection is slow
- Code generation taking too long

**Solutions:**
```bash
# 1. Use faster model
# Edit .env:
ONLYSQ_MODEL=gpt-4o-mini  # Use mini for faster responses

# 2. Check internet speed
# Test: https://speedtest.net

# 3. Reduce code generation complexity
# Use simpler bot descriptions
```

### High memory usage

**Causes:**
- Too many running bots
- Memory leak in generated code
- Large database file

**Solutions:**
```bash
# 1. Stop unnecessary bots
/stop BotName

# 2. Backup and recreate database
rename bots_database.json bots_database.json.bak
python main.py

# 3. Monitor resource usage
# Windows Task Manager → Performance tab
# Linux: top or htop
```

---

## Still Having Issues?

### Get Help

1. **Check documentation:**
   - [README.md](README.md) - Overview
   - [INSTALLATION.md](INSTALLATION.md) - Setup guide
   - [USAGE.md](USAGE.md) - Usage examples

2. **Search GitHub Issues:**
   - Visit [Issues](https://github.com/SignalScp/telegram-bot-generator/issues)
   - Search for your error

3. **Report Bug:**
   - Create new issue with:
     - Python version: `python --version`
     - OS: Windows/Mac/Linux
     - Error message (full traceback)
     - Steps to reproduce

4. **Provide Debug Info:**
   ```bash
   # Collect debug info
   python --version > debug.txt
   pip list >> debug.txt
   dir .env >> debug.txt
   
   # Attach debug.txt to issue
   ```

---

## Quick Reference

| Issue | Command |
|-------|----------|
| Update Python | Visit https://www.python.org/ |
| Update packages | `pip install --upgrade -r requirements.txt` |
| Reset database | `rename bots_database.json bots_database.json.bak` |
| Check Python version | `python --version` |
| Check pip packages | `pip list` |
| Test internet | `python -c "import socket; socket.create_connection(('8.8.8.8', 53))"`|
| Verify OnlySq API | `python -c "import httpx; print(httpx.get('https://api.onlysq.ru/v1/models').status_code)"` |
| Test bot token | `/start` command in Telegram to your bot |
| View logs | Check console output while running `python main.py` |

---

## Windows-Specific Issues

### Python not found

```bash
# Add Python to PATH
setx PATH "%PATH%;C:\Users\<YourUsername>\AppData\Local\Programs\Python\Python312"

# Restart terminal and try:
python --version
```

### Antivirus blocking execution

1. Open Windows Defender
2. Go to Virus & threat protection
3. Add telegram-bot-generator folder to exclusions

### Visual C++ Redistributable missing

```bash
# Download and install from:
# https://support.microsoft.com/en-us/help/2977003
```

---

## Linux/Mac-Specific Issues

### Permission denied

```bash
# Make executable
chmod +x main.py

# Set file permissions
chmod 755 .
chmod 600 .env
```

### Python 3 not found

```bash
# Install Python 3
sudo apt-get install python3 python3-pip  # Ubuntu/Debian
brew install python3  # macOS

# Or create alias
alias python=python3
```

### Virtual environment issues

```bash
# Remove old venv
rm -rf venv

# Create new one
python3 -m venv venv
source venv/bin/activate
```

---

## Development Tips

### Enable Debug Logging

```python
# In main.py, change:
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.DEBUG  # Changed from INFO
)
```

### Save Logs to File

```bash
# Windows
python main.py > bot.log 2>&1

# Linux/Mac
python main.py > bot.log 2>&1 &
```

### Monitor Running Bots

```bash
# Windows Task Manager
# Ctrl + Shift + Esc → Processes tab

# Linux
top
htop
ps aux | grep python

# macOS
Activity Monitor
```

---

**Last Updated:** December 23, 2024

**For the latest fixes, check:** [GitHub Issues](https://github.com/SignalScp/telegram-bot-generator/issues)
