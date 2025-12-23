import os
from dotenv import load_dotenv
from typing import Optional

load_dotenv()

class Config:
    """Application configuration"""
    
    # Telegram
    MAIN_BOT_TOKEN: str = os.getenv('MAIN_BOT_TOKEN', '')
    
    # OnlySq API (no key needed - using free tier)
    ONLYSQ_BASE_URL: str = os.getenv('ONLYSQ_BASE_URL', 'https://api.onlysq.ru/v1')
    ONLYSQ_MODEL: str = os.getenv('ONLYSQ_MODEL', 'gpt-4o-mini')
    
    # Bot Execution
    BOT_PORT: int = int(os.getenv('BOT_PORT', 8000))
    BOT_WEBHOOK_URL: Optional[str] = os.getenv('BOT_WEBHOOK_URL')
    
    # Database (JSON)
    DATABASE_FILE: str = os.getenv('DATABASE_FILE', 'bots_database.json')
    
    # Logging
    LOG_LEVEL: str = os.getenv('LOG_LEVEL', 'INFO')
    
    # Bot Generation Limits
    MAX_CONCURRENT_BOTS: int = 10
    MAX_BOT_CODE_LENGTH: int = 50000
    BOT_GENERATION_TIMEOUT: int = 30
    
    # Generated Bots Storage
    GENERATED_BOTS_DIR: str = 'generated_bots'
    
    @classmethod
    def validate(cls) -> bool:
        """Validate configuration"""
        if not cls.MAIN_BOT_TOKEN:
            raise ValueError('MAIN_BOT_TOKEN is required')
        return True

config = Config()
