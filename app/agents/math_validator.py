"""
Math Validator Agent: Validates mathematical content.
"""
import asyncio
import time
import re
from app.models.agent_models import MathValidatorResult, AgentStatus
from app.services.claude_client import get_async_claude_client
from app.utils.parser import parse_agent_response, extract_formulas
from app.utils.logger import get_logger
from app.config.settings import settings

logger = get_logger(__name__)


async def run_math_validator_agent(generated_response: str) -> MathValidatorResult:
    """
    Run the math validator agent to verify mathematical content.
    
    Args:
        generated_response: Response from generator
        
    Returns:
        MathValidatorResult with validation
    """
    start_time = time.time()
    
    system_prompt = """You are the MATH VALIDATOR AGENT in the JUROR multi-agent verification system.

Your role is to:
1. Detect mathematical formulas and calculations
2. Verify mathematical accuracy
3. Check for computational errors
4. Provide correct formulas if needed

CRITICAL: If NO mathematical content exists:
{
  "applicable": false,
  "status": "skipped",
  "reason": "No mathematical operations detected in this response"
}

RESPONSE FORMAT for mathematical content:
{
  "applicable": true,
  "status": "completed",
  "score": 90,
  "formulas_detected": ["Formula 1", "Formula 2"],
  "calculations_found": ["Calculation 1"],
  "math_errors": [],
  "correct_formula": "If applicable, provide the correct version",
  "reasoning": "Step-by-step verification"
}

If errors found, return status: "warning" with errors listed.
Use mathematical rigor. Show your work."""
    
    user_message = f"""Response to verify for mathematical accuracy:
{generated_response[:2000]}

Check all mathematical formulas, equations, and calculations."""
    
    try:
        logger.info("Math Validator Agent starting")
        
        # Quick check: does response contain math patterns?
        math_patterns = r'[\d\+\-\*\/\(\)\^\=\∑\∫√∂]+'
        has_math = bool(re.search(math_patterns, generated_response))
        
        if not has_math:
            logger.info("No math detected, skipping Math Validator")
            execution_time = time.time() - start_time
            return MathValidatorResult(
                agent_name="Math Validator",
                status=AgentStatus.SKIPPED,
                applicable=False,
                score=100,
                reasoning="No mathematical operations detected",
                findings=[],
                execution_time=execution_time
            )
        
        # Run Claude validation
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
            return MathValidatorResult(
                agent_name="Math Validator",
                status=AgentStatus.SKIPPED,
                applicable=False,
                score=100,
                reasoning=parsed.get("reason", "No math detected"),
                findings=[],
                execution_time=execution_time
            )
        
        # Extract formulas
        formulas = extract_formulas(generated_response)
        
        execution_time = time.time() - start_time
        
        result = MathValidatorResult(
            agent_name="Math Validator",
            status=AgentStatus.COMPLETED if not parsed.get("math_errors") else AgentStatus.WARNING,
            applicable=True,
            score=parsed.get("score", 80.0),
            formulas_detected=formulas,
            calculations=parsed.get("calculations_found", []),
            math_errors=parsed.get("math_errors", []),
            correct_formula=parsed.get("correct_formula"),
            reasoning=parsed.get("reasoning", "Math validation completed"),
            findings=parsed.get("math_errors", []),
            confidence=parsed.get("confidence", 80),
            execution_time=execution_time
        )
        
        logger.info(f"Math Validator completed in {execution_time:.2f}s")
        return result
        
    except asyncio.TimeoutError:
        logger.warning("Math Validator timeout")
        execution_time = time.time() - start_time
        return MathValidatorResult(
            agent_name="Math Validator",
            status=AgentStatus.FAILED,
            applicable=True,
            score=50,
            reasoning="Math validation timeout",
            findings=["Timeout during validation"],
            execution_time=execution_time
        )
    except Exception as e:
        logger.error(f"Math Validator error: {e}")
        execution_time = time.time() - start_time
        return MathValidatorResult(
            agent_name="Math Validator",
            status=AgentStatus.FAILED,
            applicable=True,
            score=50,
            reasoning=f"Math validator failed: {str(e)}",
            findings=[str(e)],
            execution_time=execution_time
        )
