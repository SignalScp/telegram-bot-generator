"""Base templates for generated bots"""

BASE_BOT_TEMPLATE = '''"""Auto-generated Telegram bot"""
import logging
import os
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

class {bot_class_name}:
    """Generated bot class"""
    
    def __init__(self, token: str):
        self.token = token
        self.application = None
    
    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /start command"""
        await update.message.reply_text(
            "Hello! I'm a Telegram bot created by the Bot Generator.\\n"
            "Created at: {creation_time}"
        )
    
    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /help command"""
        await update.message.reply_text(
            "Available commands:\\n"
            "/start - Start the bot\\n"
            "/help - Show this message\\n"
            "/info - Bot information"
        )
    
    async def info_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /info command"""
        await update.message.reply_text(
            "🤖 Bot Information\\n"
            "Name: {bot_name}\\n"
            "Type: Generated Bot\\n"
            "Created: {creation_time}\\n"
            "Description: {bot_description}"
        )
    
    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle regular messages"""
        # Custom bot logic goes here
        await update.message.reply_text(
            "Thanks for your message! This is a basic response.\\n"
            "Custom logic can be added here."
        )
    
    def run(self):
        """Run the bot"""
        self.application = Application.builder().token(self.token).build()
        
        # Add handlers
        self.application.add_handler(CommandHandler("start", self.start))
        self.application.add_handler(CommandHandler("help", self.help_command))
        self.application.add_handler(CommandHandler("info", self.info_command))
        self.application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_message))
        
        logger.info("Starting bot...")
        self.application.run_polling()

if __name__ == "__main__":
    token = os.getenv("BOT_TOKEN", "{bot_token}")
    bot = {bot_class_name}(token)
    bot.run()
'''

ENHANCED_BOT_TEMPLATE = '''"""Enhanced auto-generated Telegram bot with custom functionality"""
import logging
import os
import asyncio
from datetime import datetime
from typing import Optional
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import (
    Application, CommandHandler, MessageHandler, filters,
    ContextTypes, ConversationHandler, CallbackQueryHandler
)

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Conversation states
STATE_MAIN, STATE_INPUT = range(2)

class {bot_class_name}:
    """Enhanced generated bot class"""
    
    def __init__(self, token: str):
        self.token = token
        self.application = None
        self.users_data = {{}}
        self.start_time = datetime.now()
    
    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /start command with inline keyboard"""
        user = update.effective_user
        keyboard = [
            [InlineKeyboardButton("About", callback_data="about")],
            [InlineKeyboardButton("Help", callback_data="help")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            f"Welcome, {{user.first_name}}! 👋\\n"
            f"I'm {{self.get_bot_name()}}",
            reply_markup=reply_markup
        )
    
    async def button_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle button presses"""
        query = update.callback_query
        await query.answer()
        
        if query.data == "about":
            text = f"🤖 About This Bot\\nName: {{self.get_bot_name()}}\\nUptime: {{self.get_uptime()}}"
        elif query.data == "help":
            text = "Commands available:\\n/start - Start\\n/help - Help\\n/status - Status"
        else:
            text = "Unknown command"
        
        await query.edit_message_text(text=text)
    
    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle regular messages"""
        user_id = update.effective_user.id
        
        if user_id not in self.users_data:
            self.users_data[user_id] = {"messages": 0}
        
        self.users_data[user_id]["messages"] += 1
        
        await update.message.reply_text(
            "Message received! Thanks for interacting with me. 😊"
        )
    
    async def status_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Show bot status"""
        status_text = (
            f"📊 Bot Status\\n"
            f"Uptime: {{self.get_uptime()}}\\n"
            f"Active Users: {{len(self.users_data)}}\\n"
            f"Total Messages: {{sum(u.get('messages', 0) for u in self.users_data.values())}}"
        )
        await update.message.reply_text(status_text)
    
    def get_bot_name(self) -> str:
        return "{bot_name}"
    
    def get_uptime(self) -> str:
        delta = datetime.now() - self.start_time
        hours, remainder = divmod(int(delta.total_seconds()), 3600)
        minutes, seconds = divmod(remainder, 60)
        return f"{{hours}}h {{minutes}}m {{seconds}}s"
    
    def run(self):
        """Run the bot"""
        self.application = Application.builder().token(self.token).build()
        
        # Add handlers
        self.application.add_handler(CommandHandler("start", self.start))
        self.application.add_handler(CommandHandler("status", self.status_command))
        self.application.add_handler(CallbackQueryHandler(self.button_callback))
        self.application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_message))
        
        logger.info(f"Starting bot: {{self.get_bot_name()}}")
        self.application.run_polling()

if __name__ == "__main__":
    token = os.getenv("BOT_TOKEN", "{bot_token}")
    bot = {bot_class_name}(token)
    bot.run()
'''

def get_template(enhanced: bool = False) -> str:
    """Get appropriate template"""
    return ENHANCED_BOT_TEMPLATE if enhanced else BASE_BOT_TEMPLATE
