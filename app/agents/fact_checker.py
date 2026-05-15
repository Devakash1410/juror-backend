"""
Fact Checker Agent: Verifies factual claims in the generated response.
"""
import asyncio
import time
from app.models.agent_models import FactCheckerResult, AgentStatus
from app.services.claude_client import get_async_claude_client
from app.services.tavily_client import get_tavily_client
from app.services.wikipedia_client import get_wikipedia_client
from app.utils.parser import parse_agent_response, extract_factual_claims
from app.utils.logger import get_logger
from app.config.settings import settings

logger = get_logger(__name__)


async def run_fact_checker_agent(generated_response: str, query: str) -> FactCheckerResult:
    """
    Run the fact checker agent to verify claims.
    
    Args:
        generated_response: Response from generator
        query: Original user query
        
    Returns:
        FactCheckerResult with verification
    """
    start_time = time.time()
    
    system_prompt = """You are the FACT CHECKER AGENT in the JUROR multi-agent verification system.

Your role is to:
1. Identify factual claims in the response
2. Assess the accuracy of these claims
3. Flag potential hallucinations or inaccuracies
4. Provide sources when available

CRITICAL: If NO factual claims exist in the input, respond with:
{
  "applicable": false,
  "status": "skipped",
  "reason": "No factual claims require external verification"
}

RESPONSE FORMAT for factual content:
{
  "applicable": true,
  "status": "completed",
  "score": 85,
  "factual_claims_identified": ["Claim 1", "Claim 2"],
  "verified_facts": ["Fact that checks out"],
  "hallucinations": ["Fact that appears incorrect or unverifiable"],
  "sources_checked": ["Wikipedia", "Tavily Search"],
  "reasoning": "Explanation of findings",
  "confidence": 80
}

Be objective and evidence-based. Only flag actual inaccuracies."""
    
    user_message = f"""Response to verify:
{generated_response[:2000]}

Original query: {query}

Analyze this response for factual accuracy and identify any hallucinations."""
    
    try:
        logger.info("Fact Checker Agent starting")
        
        # Get initial assessment from Claude
        client = get_async_claude_client()
        response_text = await asyncio.wait_for(
            client.generate(
                system_prompt=system_prompt,
                user_message=user_message,
                temperature=settings.jury_temperature,
                max_tokens=1500
            ),
            timeout=settings.agent_timeout
        )
        
        parsed = parse_agent_response(response_text)
        
        # Check if applicable
        if not parsed.get("applicable", True):
            execution_time = time.time() - start_time
            return FactCheckerResult(
                agent_name="Fact Checker",
                status=AgentStatus.SKIPPED,
                applicable=False,
                score=100,
                reasoning=parsed.get("reason", "No factual claims"),
                findings=[],
                execution_time=execution_time
            )
        
        # If applicable, verify some claims with external APIs
        claims = extract_factual_claims(generated_response)
        verified_facts = []
        hallucinations = []
        sources = set()
        
        # Verify top claims (limit to 3 for speed)
        tavily = get_tavily_client()
        wikipedia = get_wikipedia_client()
        
        for claim in claims[:3]:
            # Try Wikipedia first
            wp_result = await wikipedia.verify_fact(claim)
            if wp_result["verified"]:
                verified_facts.append(claim)
                sources.add("Wikipedia")
            else:
                # Try Tavily
                tavily_result = await tavily.verify_claim(claim)
                if tavily_result["verified"]:
                    verified_facts.append(claim)
                    sources.add("Tavily Search")
        
        # Calculate score based on verification
        if verified_facts or not claims:
            score = 85.0
        else:
            score = 60.0
        
        execution_time = time.time() - start_time
        
        result = FactCheckerResult(
            agent_name="Fact Checker",
            status=AgentStatus.COMPLETED,
            applicable=True,
            score=score,
            factual_claims=claims,
            verified_facts=verified_facts,
            hallucinations=parsed.get("hallucinations", []),
            sources_checked=list(sources),
            reasoning=parsed.get("reasoning", "Fact verification completed"),
            findings=parsed.get("hallucinations", []),
            confidence=parsed.get("confidence", 75),
            execution_time=execution_time
        )
        
        logger.info(f"Fact Checker completed in {execution_time:.2f}s")
        return result
        
    except asyncio.TimeoutError:
        logger.warning("Fact Checker timeout")
        execution_time = time.time() - start_time
        return FactCheckerResult(
            agent_name="Fact Checker",
            status=AgentStatus.FAILED,
            applicable=True,
            score=50,
            reasoning="Fact checking timeout",
            findings=["Timeout during verification"],
            execution_time=execution_time
        )
    except Exception as e:
        logger.error(f"Fact Checker error: {e}")
        execution_time = time.time() - start_time
        return FactCheckerResult(
            agent_name="Fact Checker",
            status=AgentStatus.FAILED,
            applicable=True,
            score=50,
            reasoning=f"Fact checker failed: {str(e)}",
            findings=[str(e)],
            execution_time=execution_time
        )
