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
from database import db

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
        user_id = user.id
        
        welcome_text = (
            f"🤖 Welcome to Telegram Bot Generator, {user.first_name}!\n\n"
            "I can help you create custom Telegram bots using AI. "
            "Just describe what you want, and I'll generate and launch the bot for you!\n\n"
            "Available commands:\n"
            "/generate - Create a new bot\n"
            "/list - Show running bots\n"
            "/status - Check bot statuses\n"
            "/stop - Stop a bot\n"
            "/help - Show help\n"
            "/stats - Show database statistics"
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
            "Database:\n"
            "/stats - Show statistics\n\n"
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
                user_id=user_id,
                enhanced=True
            )
            
            # Save the generated code
            bot_id = str(uuid.uuid4())[:8]
            bot_file = f"{config.GENERATED_BOTS_DIR}/bot_{bot_id}.py"
            
            os.makedirs(config.GENERATED_BOTS_DIR, exist_ok=True)
            
            with open(bot_file, 'w', encoding='utf-8') as f:
                f.write(bot_code)
            
            # Save to database
            bot_data = {
                "bot_id": bot_id,
                "name": bot_name,
                "description": description,
                "user_id": user_id,
                "status": "generated",
                "code_file": bot_file,
                "code_length": len(bot_code)
            }
            db.add_bot(bot_id, bot_data)
            
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
                f"Bot ID: {bot_id}\n"
                f"Code Length: {len(bot_code)} characters\n\n"
                f"Code Preview:\n"
                f"```python\n{code_preview}\n```"
            )
            
            keyboard = [
                [InlineKeyboardButton("✅ Launch Bot", callback_data=f"launch_{bot_id}")],
                [InlineKeyboardButton("📄 Save for Later", callback_data=f"save_{bot_id}")],
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
        
        elif query.data.startswith("save_"):
            bot_id = query.data.replace("save_", "")
            session = self.user_sessions.get(user_id)
            
            if session and session.get("bot_id") == bot_id:
                # Update bot status in database
                db.update_bot(bot_id, {"status": "saved"})
                await query.edit_message_text(
                    f"📄 Bot '{session['bot_name']}' saved!\n"
                    f"You can launch it later with /list and /stop commands."
                )
            else:
                await query.edit_message_text("❌ Session expired.")
            
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
                
                # Update database
                db.update_bot(bot_id, {"status": "running", "process_id": bot_process.process.pid})
                
                success_text = (
                    f"✅ Bot '{session['bot_name']}' launched successfully!\n\n"
                    f"Bot ID: {bot_id}\n"
                    f"Status: {bot_process.status}\n"
                    f"Process ID: {bot_process.process.pid}\n"
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
                # Update database with error
                db.update_bot(bot_id, {"status": "error", "error": str(e)})
            
            return ConversationHandler.END
    
    async def list_bots(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """List all running bots"""
        user_id = update.effective_user.id
        bots = executor.list_running_bots()
        user_bots = db.get_bots_by_user(user_id)
        
        if not user_bots:
            await update.message.reply_text(
                "📭 No bots created yet.\n"
                "Use /generate to create a new bot!"
            )
            return
        
        text = f"📋 Your Bots ({len(user_bots)} total):\n\n"
        for bot_id, bot_data in user_bots.items():
            status = bot_data.get("status", "unknown")
            status_emoji = {
                "running": "🟢",
                "stopped": "🔴",
                "error": "❌",
                "saved": "📄",
                "generated": "🔨"
            }.get(status, "❓")
            
            text += (
                f"{status_emoji} {bot_data.get('name', 'Unknown')}\n"
                f"   ID: {bot_id}\n"
                f"   Status: {status}\n\n"
            )
        
        await update.message.reply_text(text)
    
    async def status_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Show all bots status"""
        user_id = update.effective_user.id
        user_bots = db.get_bots_by_user(user_id)
        
        if not user_bots:
            await update.message.reply_text(
                "📭 No bots created yet.\n"
                "Use /generate to create one!"
            )
            return
        
        text = "📊 All Your Bots Status:\n\n"
        for bot_id, bot_data in user_bots.items():
            status_emoji = {
                "running": "🟢",
                "stopped": "🔴",
                "error": "❌",
                "saved": "📄",
                "generated": "🔨"
            }.get(bot_data.get("status"), "❓")
            
            text += (
                f"{status_emoji} {bot_data.get('name', 'Unknown')}\n"
                f"   ID: {bot_id}\n"
                f"   Status: {bot_data.get('status', 'unknown')}\n"
                f"   Created: {bot_data.get('created_at', 'N/A')}\n"
            )
            
            if bot_data.get('error'):
                text += f"   Error: {bot_data['error']}\n"
            
            text += "\n"
        
        await update.message.reply_text(text)
    
    async def stats_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Show database statistics"""
        stats = db.get_statistics()
        user_id = update.effective_user.id
        user_bots = len(db.get_bots_by_user(user_id))
        
        text = (
            "📈 Database Statistics\n\n"
            f"Total bots: {stats.get('total_bots', 0)}\n"
            f"Your bots: {user_bots}\n"
            f"Database file: {stats.get('database_file', 'N/A')}\n"
            f"Database size: {stats.get('database_size_bytes', 0)} bytes\n\n"
            f"Bots by status:\n"
        )
        
        for status, count in stats.get('bots_by_status', {}).items():
            text += f"  {status}: {count}\n"
        
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
            # Update database
            db.update_bot(bot_to_stop, {"status": "stopped"})
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
        logger.info(f"Database file: {config.DATABASE_FILE}")
        
        # Create application
        app = Application.builder().token(config.MAIN_BOT_TOKEN).build()
        
        bot_instance = GeneratorBot()
        
        # Add handlers
        app.add_handler(CommandHandler("start", bot_instance.start))
        app.add_handler(CommandHandler("help", bot_instance.help_command))
        app.add_handler(CommandHandler("list", bot_instance.list_bots))
        app.add_handler(CommandHandler("status", bot_instance.status_command))
        app.add_handler(CommandHandler("stats", bot_instance.stats_command))
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
