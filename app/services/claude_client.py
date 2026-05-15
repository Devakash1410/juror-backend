"""
Claude AI client for agent interactions.
"""
import asyncio
from anthropic import Anthropic, AsyncAnthropic
from app.config.settings import settings
from app.utils.logger import get_logger

logger = get_logger(__name__)


class ClaudeClient:
    """Synchronous Claude client."""
    
    def __init__(self):
        self.client = Anthropic(api_key=settings.anthropic_api_key)
    
    def generate(
        self,
        system_prompt: str,
        user_message: str,
        temperature: float = 0.7,
        max_tokens: int = 2000
    ) -> str:
        """Generate response from Claude."""
        try:
            message = self.client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=max_tokens,
                temperature=temperature,
                system=system_prompt,
                messages=[
                    {"role": "user", "content": user_message}
                ]
            )
            return message.content[0].text
        except Exception as e:
            logger.error(f"Claude API error: {e}")
            raise


class AsyncClaudeClient:
    """Asynchronous Claude client for concurrent requests."""
    
    def __init__(self):
        self.client = AsyncAnthropic(api_key=settings.anthropic_api_key)
    
    async def generate(
        self,
        system_prompt: str,
        user_message: str,
        temperature: float = 0.7,
        max_tokens: int = 2000
    ) -> str:
        """Asynchronously generate response from Claude."""
        try:
            message = await self.client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=max_tokens,
                temperature=temperature,
                system=system_prompt,
                messages=[
                    {"role": "user", "content": user_message}
                ]
            )
            return message.content[0].text
        except asyncio.TimeoutError:
            logger.warning("Claude request timeout")
            return ""
        except Exception as e:
            logger.error(f"Claude API error: {e}")
            raise


# Global async client instance
_async_claude = None


def get_async_claude_client() -> AsyncClaudeClient:
    """Get or create async Claude client."""
    global _async_claude
    if _async_claude is None:
        _async_claude = AsyncClaudeClient()
    return _async_claude
