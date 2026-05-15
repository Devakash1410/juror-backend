"""
Tavily search API client for fact verification.
"""
import httpx
import asyncio
from typing import List, Dict, Any, Optional
from app.config.settings import settings
from app.utils.logger import get_logger

logger = get_logger(__name__)


class TavilyClient:
    """Tavily search API client."""
    
    def __init__(self):
        self.api_key = settings.tavily_api_key
        self.base_url = "https://api.tavily.com"
    
    async def search(self, query: str, max_results: int = 5) -> List[Dict[str, Any]]:
        """
        Search for information about a query.
        
        Args:
            query: Search query string
            max_results: Maximum number of results
            
        Returns:
            List of search results
        """
        if not self.api_key:
            logger.warning("Tavily API key not configured")
            return []
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/search",
                    json={
                        "api_key": self.api_key,
                        "query": query,
                        "max_results": max_results,
                        "include_answer": True
                    },
                    timeout=10.0
                )
                
                if response.status_code == 200:
                    data = response.json()
                    return data.get("results", [])
                else:
                    logger.error(f"Tavily API error: {response.status_code}")
                    return []
        except asyncio.TimeoutError:
            logger.warning(f"Tavily search timeout for query: {query}")
            return []
        except Exception as e:
            logger.error(f"Tavily search error: {e}")
            return []
    
    async def verify_claim(self, claim: str) -> Dict[str, Any]:
        """
        Verify a specific claim through search.
        
        Args:
            claim: Factual claim to verify
            
        Returns:
            Verification result
        """
        results = await self.search(claim, max_results=3)
        
        return {
            "claim": claim,
            "verified": len(results) > 0,
            "sources": [r.get("title", "") for r in results],
            "confidence": min(len(results) * 30, 100)
        }


def get_tavily_client() -> TavilyClient:
    """Get Tavily client instance."""
    return TavilyClient()
