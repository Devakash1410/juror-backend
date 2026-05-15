"""
Logic Auditor Agent: Checks logical consistency and reasoning.
"""
import asyncio
import time
from app.models.agent_models import LogicAuditorResult, AgentStatus
from app.services.claude_client import get_async_claude_client
from app.utils.parser import parse_agent_response
from app.utils.logger import get_logger
from app.config.settings import settings

logger = get_logger(__name__)


async def run_logic_auditor_agent(generated_response: str) -> LogicAuditorResult:
    """
    Run the logic auditor agent to check reasoning consistency.
    
    Args:
        generated_response: Response from generator
        
    Returns:
        LogicAuditorResult with audit findings
    """
    start_time = time.time()
    
    system_prompt = """You are the LOGIC AUDITOR AGENT in the JUROR multi-agent verification system.

Your role is to:
1. Check logical consistency
2. Identify contradictions
3. Find unsupported claims
4. Verify reasoning validity
5. Check code logic if present

CRITICAL: If logic auditing is not meaningful:
{
  "applicable": false,
  "status": "skipped",
  "reason": "Minimal logical reasoning involved in this response"
}

RESPONSE FORMAT for logical content:
{
  "applicable": true,
  "status": "completed",
  "score": 88,
  "contradictions": [],
  "unsupported_claims": [],
  "logic_flaws": [],
  "reasoning": "Logical analysis of the response"
}

If issues found, return status: "warning" with issues listed.
Evaluate the logical structure, not just content accuracy."""
    
    user_message = f"""Response to audit for logical consistency:
{generated_response[:2000]}

Analyze for:
1. Internal contradictions
2. Logical fallacies
3. Unsupported claims
4. Reasoning flaws
5. Code logic issues (if any)"""
    
    try:
        logger.info("Logic Auditor Agent starting")
        
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
            return LogicAuditorResult(
                agent_name="Logic Auditor",
                status=AgentStatus.SKIPPED,
                applicable=False,
                score=100,
                reasoning=parsed.get("reason", "Minimal logical reasoning"),
                findings=[],
                execution_time=execution_time
            )
        
        execution_time = time.time() - start_time
        
        # Determine status based on issues found
        has_issues = bool(
            parsed.get("contradictions") or 
            parsed.get("unsupported_claims") or 
            parsed.get("logic_flaws")
        )
        status = AgentStatus.WARNING if has_issues else AgentStatus.COMPLETED
        
        result = LogicAuditorResult(
            agent_name="Logic Auditor",
            status=status,
            applicable=True,
            score=parsed.get("score", 80.0),
            contradictions=parsed.get("contradictions", []),
            unsupported_claims=parsed.get("unsupported_claims", []),
            logic_flaws=parsed.get("logic_flaws", []),
            reasoning=parsed.get("reasoning", "Logic audit completed"),
            findings=parsed.get("logic_flaws", []),
            confidence=parsed.get("confidence", 80),
            execution_time=execution_time
        )
        
        logger.info(f"Logic Auditor completed in {execution_time:.2f}s")
        return result
        
    except asyncio.TimeoutError:
        logger.warning("Logic Auditor timeout")
        execution_time = time.time() - start_time
        return LogicAuditorResult(
            agent_name="Logic Auditor",
            status=AgentStatus.FAILED,
            applicable=True,
            score=50,
            reasoning="Logic audit timeout",
            findings=["Timeout during audit"],
            execution_time=execution_time
        )
    except Exception as e:
        logger.error(f"Logic Auditor error: {e}")
        execution_time = time.time() - start_time
        return LogicAuditorResult(
            agent_name="Logic Auditor",
            status=AgentStatus.FAILED,
            applicable=True,
            score=50,
            reasoning=f"Logic auditor failed: {str(e)}",
            findings=[str(e)],
            execution_time=execution_time
        )
