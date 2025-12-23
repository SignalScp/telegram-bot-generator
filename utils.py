"""Utility functions for bot generation and execution"""

import logging
import re
import json
from typing import Optional, Dict, Any
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

def format_uptime(seconds: float) -> str:
    """
    Format seconds into human-readable uptime
    
    Args:
        seconds: Total seconds
    
    Returns:
        Formatted uptime string (e.g., "2d 3h 45m 30s")
    """
    try:
        duration = timedelta(seconds=int(seconds))
        days = duration.days
        hours, remainder = divmod(duration.seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        
        parts = []
        if days > 0:
            parts.append(f"{days}d")
        if hours > 0:
            parts.append(f"{hours}h")
        if minutes > 0:
            parts.append(f"{minutes}m")
        if seconds > 0 or not parts:
            parts.append(f"{seconds}s")
        
        return " ".join(parts)
    except Exception as e:
        logger.error(f"Error formatting uptime: {e}")
        return "N/A"

def extract_function_names(code: str) -> list:
    """
    Extract function names from Python code
    
    Args:
        code: Python code string
    
    Returns:
        List of function names
    """
    try:
        # Match function definitions: async def name(...) or def name(...)
        pattern = r'(?:async\s+)?def\s+([a-zA-Z_][a-zA-Z0-9_]*)\s*\('
        matches = re.findall(pattern, code)
        return matches
    except Exception as e:
        logger.error(f"Error extracting function names: {e}")
        return []

def extract_imports(code: str) -> list:
    """
    Extract import statements from Python code
    
    Args:
        code: Python code string
    
    Returns:
        List of import statements
    """
    try:
        # Match import lines
        pattern = r'^(?:import|from)\s+.*$'
        matches = re.findall(pattern, code, re.MULTILINE)
        return matches
    except Exception as e:
        logger.error(f"Error extracting imports: {e}")
        return []

def truncate_text(text: str, max_length: int = 1000, suffix: str = "...") -> str:
    """
    Truncate text to maximum length
    
    Args:
        text: Text to truncate
        max_length: Maximum length
        suffix: Suffix to add if truncated
    
    Returns:
        Truncated text
    """
    if len(text) <= max_length:
        return text
    
    return text[:max_length - len(suffix)] + suffix

def sanitize_log_text(text: str, max_lines: int = 10) -> str:
    """
    Sanitize and truncate log text for display
    
    Args:
        text: Log text
        max_lines: Maximum number of lines
    
    Returns:
        Sanitized text
    """
    try:
        lines = text.split('\n')[:max_lines]
        result = '\n'.join(lines)
        if len(text.split('\n')) > max_lines:
            result += f"\n... ({len(text.split(chr(10))) - max_lines} more lines)"
        return result
    except Exception as e:
        logger.error(f"Error sanitizing log: {e}")
        return text[:500]

def generate_bot_id() -> str:
    """
    Generate a unique bot ID
    
    Returns:
        Unique bot ID string
    """
    import uuid
    return str(uuid.uuid4())[:12]

def generate_bot_filename(bot_name: str) -> str:
    """
    Generate a safe filename for bot code
    
    Args:
        bot_name: Bot name
    
    Returns:
        Safe filename
    """
    # Replace non-alphanumeric characters with underscores
    safe_name = re.sub(r'[^a-zA-Z0-9_]', '_', bot_name.lower())
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    return f"bot_{safe_name}_{timestamp}.py"

def estimate_bot_complexity(description: str) -> str:
    """
    Estimate bot complexity from description
    
    Args:
        description: Bot description
    
    Returns:
        Complexity level: 'simple', 'medium', or 'complex'
    """
    keywords = {
        'simple': ['echo', 'greet', 'hello', 'basic'],
        'complex': ['api', 'database', 'ml', 'neural', 'learning', 'advanced', 'crypto']
    }
    
    desc_lower = description.lower()
    
    for keyword in keywords['complex']:
        if keyword in desc_lower:
            return 'complex'
    
    for keyword in keywords['simple']:
        if keyword in desc_lower:
            return 'simple'
    
    return 'medium'

def create_status_message(bot_info: Dict[str, Any]) -> str:
    """
    Create a formatted status message for a bot
    
    Args:
        bot_info: Bot information dictionary
    
    Returns:
        Formatted status message
    """
    try:
        status_emoji = {
            'running': '🟢',
            'stopped': '🔴',
            'error': '❌',
            'pending': '⏳'
        }.get(bot_info.get('status'), '❓')
        
        message = f"{status_emoji} Bot: {bot_info.get('name', 'Unknown')}\n"
        message += f"ID: {bot_info.get('bot_id', 'N/A')}\n"
        message += f"Status: {bot_info.get('status', 'unknown')}\n"
        
        if bot_info.get('created_at'):
            message += f"Created: {bot_info['created_at']}\n"
        
        if bot_info.get('uptime_seconds'):
            message += f"Uptime: {format_uptime(bot_info['uptime_seconds'])}\n"
        
        if bot_info.get('error_message'):
            message += f"Error: {bot_info['error_message']}\n"
        
        return message
    
    except Exception as e:
        logger.error(f"Error creating status message: {e}")
        return "Error creating status message"
