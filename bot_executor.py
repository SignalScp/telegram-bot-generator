import logging
import subprocess
import os
import signal
import time
from typing import Dict, Optional, List
from dataclasses import dataclass
from datetime import datetime
from config import config

logger = logging.getLogger(__name__)

@dataclass
class BotProcess:
    """Represents a running bot process"""
    name: str
    bot_id: str
    token: str
    process: Optional[subprocess.Popen]
    created_at: datetime
    started_at: Optional[datetime] = None
    stopped_at: Optional[datetime] = None
    status: str = "pending"  # pending, running, stopped, error
    error_message: Optional[str] = None

class BotExecutor:
    """Manages bot process lifecycle"""
    
    def __init__(self):
        self.bots: Dict[str, BotProcess] = {}
        self.max_bots = config.MAX_CONCURRENT_BOTS
    
    def launch_bot(
        self,
        bot_code_path: str,
        bot_name: str,
        bot_token: str,
        bot_id: str
    ) -> BotProcess:
        """
        Launch a new bot from generated code
        
        Args:
            bot_code_path: Path to the generated bot .py file
            bot_name: Human-readable bot name
            bot_token: Telegram bot token
            bot_id: Unique bot identifier
        
        Returns:
            BotProcess instance
        """
        try:
            # Check if we're at max capacity
            running_count = sum(1 for b in self.bots.values() if b.status == "running")
            if running_count >= self.max_bots:
                raise Exception(f"Maximum concurrent bots ({self.max_bots}) reached")
            
            # Check if code file exists
            if not os.path.exists(bot_code_path):
                raise FileNotFoundError(f"Bot code file not found: {bot_code_path}")
            
            # Prepare environment
            env = os.environ.copy()
            env['BOT_TOKEN'] = bot_token
            env['BOT_NAME'] = bot_name
            env['PYTHONUNBUFFERED'] = '1'
            
            # Create process
            process = subprocess.Popen(
                ['python', bot_code_path],
                env=env,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            bot_process = BotProcess(
                name=bot_name,
                bot_id=bot_id,
                token=bot_token,
                process=process,
                created_at=datetime.now(),
                started_at=datetime.now(),
                status="running"
            )
            
            self.bots[bot_id] = bot_process
            logger.info(f"Launched bot: {bot_name} (PID: {process.pid})")
            
            return bot_process
        
        except Exception as e:
            logger.error(f"Error launching bot: {e}")
            bot_process = BotProcess(
                name=bot_name,
                bot_id=bot_id,
                token=bot_token,
                process=None,
                created_at=datetime.now(),
                status="error",
                error_message=str(e)
            )
            self.bots[bot_id] = bot_process
            raise
    
    def stop_bot(self, bot_id: str, force: bool = False) -> bool:
        """
        Stop a running bot
        
        Args:
            bot_id: Bot identifier
            force: Use SIGKILL instead of SIGTERM
        
        Returns:
            True if successful
        """
        try:
            if bot_id not in self.bots:
                logger.warning(f"Bot not found: {bot_id}")
                return False
            
            bot = self.bots[bot_id]
            
            if bot.process is None:
                logger.warning(f"Bot process is None: {bot_id}")
                return False
            
            if bot.status != "running":
                logger.warning(f"Bot is not running: {bot_id} (status: {bot.status})")
                return False
            
            # Try graceful shutdown
            try:
                bot.process.terminate()
                bot.process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                if force:
                    bot.process.kill()
                    bot.process.wait()
                else:
                    logger.warning(f"Bot {bot_id} did not terminate gracefully")
                    return False
            
            bot.status = "stopped"
            bot.stopped_at = datetime.now()
            logger.info(f"Stopped bot: {bot.name} (ID: {bot_id})")
            
            return True
        
        except Exception as e:
            logger.error(f"Error stopping bot: {e}")
            return False
    
    def get_bot_status(self, bot_id: str) -> Dict:
        """
        Get detailed status of a bot
        
        Returns:
            Dict with bot information
        """
        if bot_id not in self.bots:
            return {"error": "Bot not found"}
        
        bot = self.bots[bot_id]
        
        # Check if process is still alive
        if bot.process and bot.status == "running":
            if bot.process.poll() is not None:
                bot.status = "stopped"
                bot.stopped_at = datetime.now()
        
        uptime = None
        if bot.started_at:
            uptime = (datetime.now() - bot.started_at).total_seconds()
        
        return {
            "name": bot.name,
            "bot_id": bot.bot_id,
            "status": bot.status,
            "created_at": bot.created_at.isoformat() if bot.created_at else None,
            "started_at": bot.started_at.isoformat() if bot.started_at else None,
            "uptime_seconds": uptime,
            "error_message": bot.error_message
        }
    
    def list_bots(self) -> List[Dict]:
        """
        List all bots and their status
        
        Returns:
            List of bot status dicts
        """
        return [self.get_bot_status(bot_id) for bot_id in self.bots.keys()]
    
    def list_running_bots(self) -> List[Dict]:
        """
        List only running bots
        
        Returns:
            List of running bot status dicts
        """
        return [status for status in self.list_bots() if status.get("status") == "running"]
    
    def cleanup(self):
        """
        Cleanup: stop all running bots
        """
        logger.info("Cleaning up all bots...")
        for bot_id in list(self.bots.keys()):
            try:
                self.stop_bot(bot_id, force=False)
            except Exception as e:
                logger.error(f"Error cleaning up bot {bot_id}: {e}")
                try:
                    self.stop_bot(bot_id, force=True)
                except Exception as e2:
                    logger.error(f"Force cleanup failed for {bot_id}: {e2}")
    
    def __del__(self):
        """Ensure cleanup on deletion"""
        self.cleanup()
