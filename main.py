#!/usr/bin/env python3
"""Main Telegram Bot Generator Application"""

import logging
import os
import uuid
from datetime import datetime
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import (
    Application, CommandHandler, MessageHandler, filters,
    ContextTypes, ConversationHandler, CallbackQueryHandler
)
from config import config
from bot_generator import BotGenerator
from bot_executor import BotExecutor

# Setup logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Conversation states
STATE_DESCRIBE_BOT, STATE_REVIEW_CODE = range(2)

# Global instances
generator = BotGenerator()
executor = BotExecutor()

class GeneratorBot:
    """Main bot generator Telegram bot"""
    
    def __init__(self):
        self.user_sessions = {}  # Store user generation sessions
    
    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /start command"""
        user = update.effective_user
        welcome_text = (
            f"🤖 Welcome to Telegram Bot Generator, {user.first_name}!\n\n"
            "I can help you create custom Telegram bots using AI. "
            "Just describe what you want, and I'll generate and launch the bot for you!\n\n"
            "Available commands:\n"
            "/generate - Create a new bot\n"
            "/list - Show running bots\n"
            "/status - Check bot statuses\n"
            "/stop - Stop a bot\n"
            "/help - Show help"
        )
        await update.message.reply_text(welcome_text)
    
    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /help command"""
        help_text = (
            "📖 Help - Bot Generator Guide\n\n"
            "Generate a bot:\n"
            "/generate - Start bot creation wizard\n\n"
            "Manage bots:\n"
            "/list - List all bots\n"
            "/status - Show detailed status\n"
            "/stop <bot_name> - Stop a specific bot\n\n"
            "Tips:\n"
            "• Describe your bot clearly and specifically\n"
            "• Include desired features in the description\n"
            "• Generated bots use python-telegram-bot library\n"
            "• Each bot gets a unique token placeholder\n\n"
            "Example description:\n"
            "'Create a weather bot that fetches weather for any city and shows '"
            "temperature, humidity, and wind speed with emojis'"
        )
        await update.message.reply_text(help_text)
    
    async def generate_start(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Start bot generation process"""
        user_id = update.effective_user.id
        
        # Initialize user session
        self.user_sessions[user_id] = {
            "status": "awaiting_description",
            "created_at": datetime.now()
        }
        
        prompt_text = (
            "🤖 Bot Generator - Describe Your Bot\n\n"
            "Tell me what kind of bot you want to create. Be specific about:\n"
            "• What the bot does\n"
            "• Main features\n"
            "• How users interact with it\n\n"
            "Example: 'Create a jokes bot that sends funny jokes when you '"
            "type /joke command and tracks user interaction count'"
        )
        
        await update.message.reply_text(prompt_text)
        return STATE_DESCRIBE_BOT
    
    async def handle_description(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Process bot description and generate code"""
        user_id = update.effective_user.id
        description = update.message.text
        
        if len(description) < 20:
            await update.message.reply_text(
                "❌ Description too short. Please provide more details (at least 20 characters)."
            )
            return STATE_DESCRIBE_BOT
        
        # Show generating status
        status_msg = await update.message.reply_text(
            "⏳ Generating bot code...\n\n"
            "This may take a few moments as I:\n"
            "1. Analyze your description\n"
            "2. Generate Python code\n"
            "3. Validate the code\n"
            "4. Prepare for launch"
        )
        
        try:
            # Generate bot code
            bot_code, bot_class_name, bot_name = await generator.generate_bot(
                description=description,
                enhanced=True
            )
            
            # Save the generated code
            bot_id = str(uuid.uuid4())[:8]
            bot_file = f"{config.GENERATED_BOTS_DIR}/bot_{bot_id}.py"
            
            os.makedirs(config.GENERATED_BOTS_DIR, exist_ok=True)
            
            with open(bot_file, 'w', encoding='utf-8') as f:
                f.write(bot_code)
            
            # Store session info
            self.user_sessions[user_id]["bot_code"] = bot_code
            self.user_sessions[user_id]["bot_file"] = bot_file
            self.user_sessions[user_id]["bot_id"] = bot_id
            self.user_sessions[user_id]["bot_name"] = bot_name
            self.user_sessions[user_id]["description"] = description
            self.user_sessions[user_id]["status"] = "code_generated"
            
            # Send code preview (first 1000 chars)
            code_preview = bot_code[:800] + "...\n\n[code truncated]" if len(bot_code) > 800 else bot_code
            
            preview_text = (
                f"✅ Bot code generated successfully!\n\n"
                f"Bot Name: {bot_name}\n"
                f"Code Length: {len(bot_code)} characters\n\n"
                f"Code Preview:\n"
                f"```python\n{code_preview}\n```"
            )
            
            keyboard = [
                [InlineKeyboardButton("✅ Launch Bot", callback_data=f"launch_{bot_id}")],
                [InlineKeyboardButton("❌ Cancel", callback_data="cancel")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await status_msg.edit_text(preview_text, reply_markup=reply_markup, parse_mode="Markdown")
            
            return STATE_REVIEW_CODE
        
        except Exception as e:
            logger.error(f"Error generating bot: {e}")
            error_text = f"❌ Error generating bot:\n{str(e)}"
            await status_msg.edit_text(error_text)
            return STATE_DESCRIBE_BOT
    
    async def handle_button(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Handle inline button presses"""
        query = update.callback_query
        user_id = update.effective_user.id
        await query.answer()
        
        if query.data == "cancel":
            await query.edit_message_text("❌ Bot generation cancelled.")
            return ConversationHandler.END
        
        elif query.data.startswith("launch_"):
            bot_id = query.data.replace("launch_", "")
            session = self.user_sessions.get(user_id)
            
            if not session or session.get("bot_id") != bot_id:
                await query.edit_message_text("❌ Session expired. Please generate a new bot.")
                return ConversationHandler.END
            
            # Launch the bot
            try:
                await query.edit_message_text(
                    "🚀 Launching bot...\n"
                    "Setting up process and preparing to handle messages..."
                )
                
                # TODO: In production, you would create a real Telegram bot token
                # For now, we'll simulate it
                bot_token = "1234567890:ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijk"  # Placeholder
                
                bot_process = executor.launch_bot(
                    bot_code_path=session["bot_file"],
                    bot_name=session["bot_name"],
                    bot_token=bot_token,
                    bot_id=bot_id
                )
                
                success_text = (
                    f"✅ Bot '{session['bot_name']}' launched successfully!\n\n"
                    f"Bot ID: {bot_id}\n"
                    f"Status: {bot_process.status}\n"
                    f"Created: {bot_process.created_at}\n\n"
                    f"💡 Next steps:\n"
                    f"1. Replace the token placeholder in the bot code\n"
                    f"2. Use /list to see all your bots\n"
                    f"3. Use /status to check bot details\n\n"
                    f"Token placeholder: {bot_token}"
                )
                
                await query.edit_message_text(success_text)
                session["status"] = "launched"
                
            except Exception as e:
                error_text = f"❌ Error launching bot:\n{str(e)}"
                await query.edit_message_text(error_text)
                logger.error(f"Error launching bot: {e}")
            
            return ConversationHandler.END
    
    async def list_bots(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """List all running bots"""
        bots = executor.list_running_bots()
        
        if not bots:
            await update.message.reply_text(
                "📭 No running bots.\n"
                "Use /generate to create a new bot!"
            )
            return
        
        text = "📋 Running Bots:\n\n"
        for bot in bots:
            text += (
                f"• {bot['name']} (ID: {bot['bot_id'][:8]})\n"
                f"  Status: {bot['status']}\n"
                f"  Started: {bot['started_at']}\n\n"
            )
        
        await update.message.reply_text(text)
    
    async def status_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Show all bots status"""
        bots = executor.list_bots()
        
        if not bots:
            await update.message.reply_text(
                "📭 No bots created yet.\n"
                "Use /generate to create one!"
            )
            return
        
        text = "📊 All Bots Status:\n\n"
        for bot in bots:
            status_emoji = {
                "running": "🟢",
                "stopped": "🔴",
                "error": "❌",
                "pending": "⏳"
            }.get(bot['status'], "❓")
            
            text += (
                f"{status_emoji} {bot['name']}\n"
                f"   ID: {bot['bot_id']}\n"
                f"   Status: {bot['status']}\n"
            )
            
            if bot['error_message']:
                text += f"   Error: {bot['error_message']}\n"
            
            text += "\n"
        
        await update.message.reply_text(text)
    
    async def stop_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Stop a bot"""
        if not context.args:
            await update.message.reply_text(
                "❌ Please specify bot name:\n"
                "/stop <bot_name>"
            )
            return
        
        bot_name = " ".join(context.args)
        
        # Find bot by name
        bot_to_stop = None
        for bot_id, bot in executor.bots.items():
            if bot.name.lower() == bot_name.lower():
                bot_to_stop = bot_id
                break
        
        if not bot_to_stop:
            await update.message.reply_text(
                f"❌ Bot '{bot_name}' not found."
            )
            return
        
        if executor.stop_bot(bot_to_stop):
            await update.message.reply_text(
                f"✅ Bot '{bot_name}' stopped successfully."
            )
        else:
            await update.message.reply_text(
                f"❌ Failed to stop bot '{bot_name}'."
            )

async def main():
    """Main entry point"""
    try:
        # Validate configuration
        config.validate()
        
        logger.info("Starting Telegram Bot Generator...")
        
        # Create application
        app = Application.builder().token(config.MAIN_BOT_TOKEN).build()
        
        bot_instance = GeneratorBot()
        
        # Add handlers
        app.add_handler(CommandHandler("start", bot_instance.start))
        app.add_handler(CommandHandler("help", bot_instance.help_command))
        app.add_handler(CommandHandler("list", bot_instance.list_bots))
        app.add_handler(CommandHandler("status", bot_instance.status_command))
        app.add_handler(CommandHandler("stop", bot_instance.stop_command))
        
        # Conversation handler for bot generation
        conv_handler = ConversationHandler(
            entry_points=[CommandHandler("generate", bot_instance.generate_start)],
            states={
                STATE_DESCRIBE_BOT: [
                    MessageHandler(filters.TEXT & ~filters.COMMAND, bot_instance.handle_description)
                ],
                STATE_REVIEW_CODE: [
                    CallbackQueryHandler(bot_instance.handle_button)
                ]
            },
            fallbacks=[]
        )
        
        app.add_handler(conv_handler)
        
        logger.info("Bot Generator started and ready to accept commands!")
        logger.info(f"Bot token: {config.MAIN_BOT_TOKEN[:20]}...")
        
        # Start polling
        await app.run_polling()
    
    except KeyboardInterrupt:
        logger.info("Keyboard interrupt received")
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        raise
    finally:
        # Cleanup
        executor.cleanup()
        generator.close()

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
