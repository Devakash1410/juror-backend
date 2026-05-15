"""
Corrector Agent: Repairs responses that failed verdict verification.
"""
import asyncio
import time
from typing import List
from app.models.agent_models import CorrectorResult, AgentStatus
from app.services.claude_client import get_async_claude_client
from app.utils.parser import parse_agent_response
from app.utils.logger import get_logger
from app.config.settings import settings

logger = get_logger(__name__)


async def run_corrector_agent(
    original_response: str,
    hallucinations: List[str],
    math_errors: List[str],
    logic_flaws: List[str],
    query: str
) -> CorrectorResult:
    """
    Run the corrector agent to fix flagged issues.
    
    Args:
        original_response: Original response from generator
        hallucinations: Hallucinations from fact checker
        math_errors: Errors from math validator
        logic_flaws: Flaws from logic auditor
        query: Original user query
        
    Returns:
        CorrectorResult with corrected response
    """
    start_time = time.time()
    
    system_prompt = """You are the CORRECTOR AGENT in the JUROR multi-agent verification system.

Your role is to repair responses that failed verdict verification.

INSTRUCTIONS:
1. Review the original response
2. Review the jury findings (hallucinations, errors, logic flaws)
3. Rewrite the response to fix all identified issues
4. Maintain accuracy and clarity
5. Preserve the original intent where possible

RESPONSE FORMAT:
{
  "corrected_response": "The fixed and improved response",
  "changes_made": [
    "Fixed hallucination about X",
    "Corrected formula from Y to Z"
  ],
  "confidence_after_fix": 88,
  "reasoning": "Summary of corrections applied"
}

Your goal is to produce a response that will PASS jury verification.
Be thorough in addressing all flagged issues."""
    
    issues_text = ""
    if hallucinations:
        issues_text += f"\nHallucinations to fix: {hallucinations}\n"
    if math_errors:
        issues_text += f"Math errors to fix: {math_errors}\n"
    if logic_flaws:
        issues_text += f"Logic flaws to fix: {logic_flaws}\n"
    
    user_message = f"""Original Query: {query}

Original Response:
{original_response[:2000]}

Issues Flagged by Jury:
{issues_text}

Please rewrite the response fixing ALL flagged issues. Maintain professional tone and accuracy.
Respond in JSON format as specified."""
    
    try:
        logger.info("Corrector Agent starting")
        
        client = get_async_claude_client()
        response_text = await asyncio.wait_for(
            client.generate(
                system_prompt=system_prompt,
                user_message=user_message,
                temperature=settings.corrector_temperature,
                max_tokens=2000
            ),
            timeout=settings.agent_timeout
        )
        
        parsed = parse_agent_response(response_text)
        
        execution_time = time.time() - start_time
        
        result = CorrectorResult(
            agent_name="Corrector",
            status=AgentStatus.COMPLETED,
            applicable=True,
            corrected_response=parsed.get("corrected_response", response_text),
            changes_made=parsed.get("changes_made", []),
            confidence_after_fix=float(parsed.get("confidence_after_fix", 80)),
            reasoning=parsed.get("reasoning", "Response corrected"),
            findings=parsed.get("changes_made", []),
            execution_time=execution_time
        )
        
        logger.info(f"Corrector Agent completed in {execution_time:.2f}s")
        return result
        
    except asyncio.TimeoutError:
        logger.warning("Corrector Agent timeout")
        execution_time = time.time() - start_time
        return CorrectorResult(
            agent_name="Corrector",
            status=AgentStatus.FAILED,
            applicable=True,
            corrected_response=original_response,
            changes_made=[],
            confidence_after_fix=50,
            reasoning="Correction timeout",
            findings=["Timeout during correction"],
            execution_time=execution_time
        )
    except Exception as e:
        logger.error(f"Corrector Agent error: {e}")
        execution_time = time.time() - start_time
        return CorrectorResult(
            agent_name="Corrector",
            status=AgentStatus.FAILED,
            applicable=True,
            corrected_response=original_response,
            changes_made=[],
            confidence_after_fix=50,
            reasoning=f"Corrector failed: {str(e)}",
            findings=[str(e)],
            execution_time=execution_time
        )
