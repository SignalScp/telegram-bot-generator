import httpx
import logging
from typing import Optional, List, Dict, Any
from config import config

logger = logging.getLogger(__name__)

class OnlySqClient:
    """Wrapper for OnlySq API (OpenAI compatible) - No API key required"""
    
    def __init__(self, base_url: Optional[str] = None):
        self.base_url = base_url or config.ONLYSQ_BASE_URL
        self.model = config.ONLYSQ_MODEL
        # OnlySq free tier doesn't require authentication
        self.client = httpx.Client(
            headers={
                'Content-Type': 'application/json'
            },
            timeout=30.0
        )
    
    async def generate_text(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 2000,
        model: Optional[str] = None
    ) -> str:
        """Generate text using OnlySq API"""
        try:
            model = model or self.model
            messages = []
            
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            
            messages.append({"role": "user", "content": prompt})
            
            response = await self._request(
                method='POST',
                endpoint='/chat/completions',
                json={
                    'model': model,
                    'messages': messages,
                    'temperature': temperature,
                    'max_tokens': max_tokens,
                    'top_p': 0.95
                }
            )
            
            if 'choices' in response and len(response['choices']) > 0:
                return response['choices'][0]['message']['content']
            else:
                raise Exception(f"Unexpected API response: {response}")
        
        except Exception as e:
            logger.error(f"Error generating text: {e}")
            # Return fallback response on error
            return self._fallback_response(prompt)
    
    async def _request(
        self,
        method: str,
        endpoint: str,
        **kwargs
    ) -> Dict[str, Any]:
        """Make request to OnlySq API"""
        url = f"{self.base_url}{endpoint}"
        
        try:
            response = self.client.request(
                method,
                url,
                **kwargs,
                timeout=30.0
            )
            response.raise_for_status()
            return response.json()
        
        except httpx.HTTPError as e:
            logger.error(f"HTTP Error: {e}")
            raise
        except Exception as e:
            logger.error(f"Request Error: {e}")
            raise
    
    def _fallback_response(self, prompt: str) -> str:
        """Return fallback response if API fails"""
        # Simple fallback for basic prompts
        if "name" in prompt.lower():
            return "WeatherBot"
        elif "logic" in prompt.lower() or "function" in prompt.lower():
            return "async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):\n    await update.message.reply_text('Thanks for your message!')"
        else:
            return "BasicBot"
    
    def list_models(self) -> List[str]:
        """List available models on OnlySq"""
        return [
            'gpt-4o',
            'gpt-4o-mini',
            'gpt-4-turbo',
            'gpt-3.5-turbo',
            'claude-3-5-sonnet',
            'claude-3-opus',
            'gemini-2.5-pro',
            'deepseek-r1',
            'llama-4-405b',
            'qwen3',
            'mistral-large'
        ]
    
    def close(self):
        """Close the client"""
        self.client.close()
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
