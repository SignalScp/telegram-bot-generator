import logging
import re
import ast
from datetime import datetime
from typing import Tuple, Optional
from onlysq_client import OnlySqClient
from bot_templates import get_template
from config import config

logger = logging.getLogger(__name__)

class BotGenerator:
    """AI-powered bot code generator using OnlySq API"""
    
    def __init__(self):
        self.client = OnlySqClient()
    
    async def generate_bot(
        self,
        description: str,
        bot_name: Optional[str] = None,
        enhanced: bool = True
    ) -> Tuple[str, str, str]:
        """
        Generate bot code from description
        
        Returns:
            Tuple of (bot_code, bot_class_name, bot_token_placeholder)
        """
        try:
            # Generate bot class name from description
            if not bot_name:
                bot_name = await self._generate_bot_name(description)
            
            bot_class_name = self._sanitize_class_name(bot_name)
            
            # Generate custom bot code/logic
            custom_code = await self._generate_custom_logic(description, bot_class_name)
            
            # Get template
            template = get_template(enhanced=enhanced)
            
            # Format template with bot info
            bot_code = template.format(
                bot_class_name=bot_class_name,
                bot_name=bot_name,
                bot_token="YOUR_BOT_TOKEN_HERE",
                creation_time=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                bot_description=description[:100]
            )
            
            # Merge custom logic if generated
            if custom_code and len(custom_code) > 20:
                bot_code = self._merge_custom_logic(bot_code, custom_code, bot_class_name)
            
            # Validate generated code
            await self._validate_code(bot_code)
            
            logger.info(f"Successfully generated bot: {bot_name}")
            return bot_code, bot_class_name, bot_name
        
        except Exception as e:
            logger.error(f"Error generating bot: {e}")
            raise
    
    async def _generate_bot_name(self, description: str) -> str:
        """Generate bot name from description using AI"""
        try:
            prompt = f"""Based on this bot description, generate a short, catchy bot name (2-3 words max).
            Description: {description}
            
            Return ONLY the bot name, nothing else.
            Example: WeatherBot, MusicHelper, CodeReviewer"""
            
            response = await self.client.generate_text(
                prompt=prompt,
                temperature=0.7,
                max_tokens=50
            )
            
            name = response.strip().split('\n')[0][:30]
            return name or "GeneratedBot"
        
        except Exception as e:
            logger.warning(f"Failed to generate bot name: {e}")
            return "GeneratedBot"
    
    async def _generate_custom_logic(self, description: str, class_name: str) -> str:
        """Generate custom bot logic from description"""
        try:
            system_prompt = """You are an expert Python developer specializing in Telegram bots.
            Generate ONLY Python code for custom async methods that can be added to a Telegram bot class.
            Use python-telegram-bot library patterns.
            Return only the method definitions, no explanations.
            Methods should be async and use the pattern: async def method_name(self, update: Update, context: ContextTypes.DEFAULT_TYPE)
            """
            
            prompt = f"""Generate 1-2 custom handler methods for a Telegram bot with this description:
            {description}
            
            Requirements:
            - Use async/await patterns
            - Include proper error handling
            - Add logging statements
            - Return exactly what would go in the class (method definitions only)
            - Use realistic Telegram API calls
            
            Example format:
            async def handle_weather(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
                # Implementation here
                pass
            """
            
            response = await self.client.generate_text(
                prompt=prompt,
                system_prompt=system_prompt,
                temperature=0.6,
                max_tokens=1000
            )
            
            return response.strip()
        
        except Exception as e:
            logger.warning(f"Failed to generate custom logic: {e}")
            return ""
    
    def _merge_custom_logic(self, template_code: str, custom_logic: str, class_name: str) -> str:
        """Merge custom logic into bot template"""
        try:
            # Find the insertion point (after __init__)
            insert_point = template_code.find("    def run(self):")
            
            if insert_point > 0:
                # Insert custom methods before run()
                merged = template_code[:insert_point] + custom_logic + "\n\n    " + template_code[insert_point:]
                return merged
            
            return template_code
        
        except Exception as e:
            logger.warning(f"Failed to merge custom logic: {e}")
            return template_code
    
    async def _validate_code(self, code: str) -> bool:
        """Validate generated Python code"""
        try:
            # Try to parse the code as valid Python
            ast.parse(code)
            
            # Check code length
            if len(code) > config.MAX_BOT_CODE_LENGTH:
                raise ValueError("Generated code exceeds maximum length")
            
            # Check for dangerous imports
            dangerous_imports = ['os.system', 'exec', 'eval', '__import__']
            for dangerous in dangerous_imports:
                if dangerous in code:
                    logger.warning(f"Potential security issue: {dangerous} found in generated code")
            
            return True
        
        except SyntaxError as e:
            logger.error(f"Syntax error in generated code: {e}")
            raise ValueError(f"Generated code has syntax errors: {e}")
        except Exception as e:
            logger.error(f"Code validation error: {e}")
            raise
    
    @staticmethod
    def _sanitize_class_name(name: str) -> str:
        """Convert name to valid Python class name"""
        # Remove non-alphanumeric characters
        name = re.sub(r'[^a-zA-Z0-9_]', '', name)
        # Ensure it starts with a letter
        if name and not name[0].isalpha():
            name = 'Bot' + name
        # Ensure it's not empty
        if not name:
            name = 'GeneratedBot'
        # Convert to proper class name format
        return ''.join(word.capitalize() for word in name.split('_'))
    
    def close(self):
        """Close the client"""
        self.client.close()
