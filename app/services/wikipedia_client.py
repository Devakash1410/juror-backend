"""
Wikipedia API client for fact verification.
"""
import asyncio
import wikipedia
from typing import List, Dict, Any, Optional
from app.config.settings import settings
from app.utils.logger import get_logger

logger = get_logger(__name__)


class WikipediaClient:
    """Wikipedia search and content client."""
    
    def __init__(self):
        self.timeout = settings.wikipedia_timeout
    
    async def search(self, query: str, max_results: int = 5) -> List[str]:
        """
        Search Wikipedia for articles.
        
        Args:
            query: Search query
            max_results: Maximum results
            
        Returns:
            List of article titles
        """
        try:
            loop = asyncio.get_event_loop()
            results = await loop.run_in_executor(
                None,
                lambda: wikipedia.search(query, results=max_results)
            )
            return results
        except Exception as e:
            logger.warning(f"Wikipedia search error: {e}")
            return []
    
    async def get_summary(self, title: str) -> Optional[str]:
        """
        Get summary of a Wikipedia article.
        
        Args:
            title: Article title
            
        Returns:
            Article summary
        """
        try:
            loop = asyncio.get_event_loop()
            summary = await loop.run_in_executor(
                None,
                lambda: wikipedia.summary(title, sentences=3)
            )
            return summary
        except Exception as e:
            logger.debug(f"Wikipedia summary error for '{title}': {e}")
            return None
    
    async def verify_fact(self, fact: str) -> Dict[str, Any]:
        """
        Verify a fact against Wikipedia.
        
        Args:
            fact: Factual statement
            
        Returns:
            Verification result
        """
        articles = await self.search(fact, max_results=3)
        
        verified_articles = []
        for article in articles:
            summary = await self.get_summary(article)
            if summary:
                verified_articles.append({
                    "title": article,
                    "summary": summary[:200]
                })
        
        return {
            "fact": fact,
            "verified": len(verified_articles) > 0,
            "articles": verified_articles,
            "confidence": min(len(verified_articles) * 40, 100)
        }


def get_wikipedia_client() -> WikipediaClient:
    """Get Wikipedia client instance."""
    return WikipediaClient()
