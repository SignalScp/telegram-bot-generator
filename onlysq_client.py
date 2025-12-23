import httpx
import logging
from typing import Optional, List, Dict, Any
from config import config

logger = logging.getLogger(__name__)

class OnlySqClient:
    """Wrapper for OnlySq API (OpenAI compatible)"""
    
    def __init__(self, api_key: Optional[str] = None, base_url: Optional[str] = None):
        self.api_key = api_key or config.ONLYSQ_API_KEY
        self.base_url = base_url or config.ONLYSQ_BASE_URL
        self.model = config.ONLYSQ_MODEL
        self.client = httpx.Client(
            headers={
                'Authorization': f'Bearer {self.api_key}',
                'Content-Type': 'application/json'
            }
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
            raise
    
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
    
    def list_models(self) -> List[str]:
        """List available models"""
        return [
            'gpt-4o',
            'gpt-4-turbo',
            'gpt-3.5-turbo',
            'claude-3-5-sonnet',
            'claude-3-opus',
            'gemini-2.5-pro',
            'deepseek-r1',
            'llama-4-405b',
            'qwen3'
        ]
    
    def close(self):
        """Close the client"""
        self.client.close()
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
