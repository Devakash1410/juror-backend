"""
Verdict Agent: Aggregates jury results and renders final verdict.
"""
import asyncio
import time
from typing import Optional
from app.models.agent_models import (
    VerdictResult, AgentStatus, Verdict, RiskLevel,
    FactCheckerResult, MathValidatorResult, LogicAuditorResult,
    GeneratorResult
)
from app.services.claude_client import get_async_claude_client
from app.utils.parser import parse_agent_response
from app.utils.scoring import calculate_consensus_score, determine_risk_level
from app.utils.logger import get_logger
from app.config.settings import settings

logger = get_logger(__name__)


async def run_verdict_agent(
    generator_result: GeneratorResult,
    fact_checker_result: Optional[FactCheckerResult],
    math_validator_result: Optional[MathValidatorResult],
    logic_auditor_result: Optional[LogicAuditorResult]
) -> VerdictResult:
    """
    Run the verdict agent to aggregate jury findings.
    
    Args:
        generator_result: Result from generator
        fact_checker_result: Result from fact checker
        math_validator_result: Result from math validator
        logic_auditor_result: Result from logic auditor
        
    Returns:
        VerdictResult with final verdict
    """
    start_time = time.time()
    
    # Collect jury scores
    fact_check_score = fact_checker_result.score if fact_checker_result and fact_checker_result.applicable else 100
    math_score = math_validator_result.score if math_validator_result and math_validator_result.applicable else 100
    logic_score = logic_auditor_result.score if logic_auditor_result and logic_auditor_result.applicable else 100
    
    # Calculate consensus
    consensus_score = calculate_consensus_score(fact_check_score, math_score, logic_score)
    risk_level_str = determine_risk_level(consensus_score)
    
    # Build jury breakdown
    jury_breakdown = {}
    if fact_checker_result and fact_checker_result.applicable:
        jury_breakdown["fact_check"] = {
            "score": fact_checker_result.score,
            "status": fact_checker_result.status.value,
            "hallucinations": len(fact_checker_result.hallucinations)
        }
    if math_validator_result and math_validator_result.applicable:
        jury_breakdown["math"] = {
            "score": math_validator_result.score,
            "status": math_validator_result.status.value,
            "errors": len(math_validator_result.math_errors)
        }
    if logic_auditor_result and logic_auditor_result.applicable:
        jury_breakdown["logic"] = {
            "score": logic_auditor_result.score,
            "status": logic_auditor_result.status.value,
            "flaws": len(logic_auditor_result.logic_flaws)
        }
    
    # Collect all issues
    all_issues = []
    if fact_checker_result:
        all_issues.extend(fact_checker_result.hallucinations)
    if math_validator_result:
        all_issues.extend(math_validator_result.math_errors)
    if logic_auditor_result:
        all_issues.extend(logic_auditor_result.logic_flaws)
    
    # Determine verdict based on scores and issues
    if consensus_score >= 80 and not all_issues:
        verdict = Verdict.PASS
        confidence = min(95, consensus_score + 10)
    elif consensus_score >= 60:
        verdict = Verdict.PARTIAL
        confidence = consensus_score
    else:
        verdict = Verdict.FAIL
        confidence = 100 - consensus_score
    
    # Build summary
    system_prompt = """You are the VERDICT AGENT. Generate a concise summary explaining the verdict."""
    
    user_message = f"""Jury Results:
- Fact Check Score: {fact_check_score}
- Math Score: {math_score}
- Logic Score: {logic_score}
- Consensus: {consensus_score}
- Issues Found: {len(all_issues)}
- Verdict: {verdict.value}

Generate a brief executive summary (2-3 sentences) explaining this verdict."""
    
    try:
        logger.info("Verdict Agent starting")
        
        client = get_async_claude_client()
        summary_text = await asyncio.wait_for(
            client.generate(
                system_prompt=system_prompt,
                user_message=user_message,
                temperature=0.5,
                max_tokens=300
            ),
            timeout=settings.agent_timeout
        )
        
        execution_time = time.time() - start_time
        
        result = VerdictResult(
            agent_name="Verdict Agent",
            status=AgentStatus.COMPLETED,
            applicable=True,
            verdict=verdict,
            confidence=confidence,
            risk_level=RiskLevel(risk_level_str),
            summary=summary_text.strip(),
            key_issues=all_issues[:5],
            jury_breakdown=jury_breakdown,
            reasoning=f"Consensus score: {consensus_score:.1f}. Issues detected: {len(all_issues)}",
            findings=all_issues,
            execution_time=execution_time
        )
        
        logger.info(f"Verdict Agent completed: {verdict.value}")
        return result
        
    except Exception as e:
        logger.error(f"Verdict Agent error: {e}")
        execution_time = time.time() - start_time
        
        return VerdictResult(
            agent_name="Verdict Agent",
            status=AgentStatus.FAILED,
            applicable=True,
            verdict=Verdict.PARTIAL,
            confidence=50,
            risk_level=RiskLevel.MEDIUM,
            summary="Unable to render verdict due to error",
            key_issues=all_issues,
            jury_breakdown=jury_breakdown,
            reasoning=f"Error: {str(e)}",
            findings=all_issues,
            execution_time=execution_time
        )
