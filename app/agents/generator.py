"""
Generator Agent: Creates initial response to user query.
"""
import asyncio
import time
from app.models.agent_models import GeneratorResult, AgentStatus
from app.services.claude_client import get_async_claude_client
from app.utils.parser import parse_agent_response
from app.utils.logger import get_logger
from app.config.settings import settings

logger = get_logger(__name__)


async def run_generator_agent(query: str) -> GeneratorResult:
    """
    Run the generator agent to create initial response.
    
    Args:
        query: User query
        
    Returns:
        GeneratorResult with initial response
    """
    start_time = time.time()
    
    system_prompt = """You are the GENERATOR AGENT in a multi-agent AI verification system called JUROR.

Your role is to generate an initial, thoughtful response to user queries.

CRITICAL GUIDELINES:
1. Avoid hallucinating facts - admit uncertainty when you don't know
2. Explain your reasoning clearly
3. Be technically accurate
4. Provide confidence level (0-100) for your response
5. Cite sources when applicable
6. Flag uncertain claims explicitly

RESPONSE FORMAT:
You MUST respond with valid JSON in this exact format:
{
  "response": "Your detailed response here",
  "confidence": 75,
  "reasoning": "Step-by-step reasoning for your answer",
  "uncertain_claims": ["Any claim you're uncertain about"],
  "key_assumptions": ["Any assumptions you made"]
}

Remember: The jury will verify your response, so be honest about limitations."""
    
    user_message = f"Query: {query}\n\nProvide a comprehensive response following the JSON format specified."
    
    try:
        logger.info(f"Generator Agent starting for query: {query[:100]}")
        
        client = get_async_claude_client()
        response_text = await asyncio.wait_for(
            client.generate(
                system_prompt=system_prompt,
                user_message=user_message,
                temperature=settings.generator_temperature,
                max_tokens=2000
            ),
            timeout=settings.agent_timeout
        )
        
        # Parse response
        parsed = parse_agent_response(response_text)
        
        confidence = parsed.get("confidence", 70)
        response_content = parsed.get("response", response_text)
        reasoning = parsed.get("reasoning", "Generated response")
        
        execution_time = time.time() - start_time
        
        result = GeneratorResult(
            agent_name="Generator",
            status=AgentStatus.COMPLETED,
            applicable=True,
            response=response_content,
            confidence=float(confidence),
            reasoning=reasoning,
            findings=parsed.get("uncertain_claims", []),
            metadata={
                "assumptions": parsed.get("key_assumptions", []),
                "raw_response": response_text[:500]
            },
            execution_time=execution_time
        )
        
        logger.info(f"Generator Agent completed in {execution_time:.2f}s")
        return result
        
    except asyncio.TimeoutError:
        logger.error("Generator Agent timeout")
        return GeneratorResult(
            agent_name="Generator",
            status=AgentStatus.FAILED,
            applicable=True,
            response="Error: Generator timeout",
            confidence=0,
            reasoning="Failed to generate response within timeout",
            findings=["Timeout during generation"],
            execution_time=time.time() - start_time
        )
    except Exception as e:
        logger.error(f"Generator Agent error: {e}")
        return GeneratorResult(
            agent_name="Generator",
            status=AgentStatus.FAILED,
            applicable=True,
            response=f"Error: {str(e)}",
            confidence=0,
            reasoning=f"Generator failed: {str(e)}",
            findings=[str(e)],
            execution_time=time.time() - start_time
        )
