"""
Main orchestration pipeline for JUROR multi-agent system.
"""
import asyncio
import time
import uuid
from typing import List, Dict, Any, Optional, Callable
from app.models.agent_models import (
    AnalysisResponse, Verdict, RiskLevel, AgentStatus,
    JuryEvent, GeneratorResult, FactCheckerResult,
    MathValidatorResult, LogicAuditorResult, VerdictResult, CorrectorResult
)
from app.agents.generator import run_generator_agent
from app.agents.fact_checker import run_fact_checker_agent
from app.agents.math_validator import run_math_validator_agent
from app.agents.logic_auditor import run_logic_auditor_agent
from app.agents.verdict_agent import run_verdict_agent
from app.agents.corrector import run_corrector_agent
from app.utils.scoring import calculate_consensus_score, determine_risk_level, aggregate_findings
from app.utils.logger import get_logger

logger = get_logger(__name__)


class JurorPipeline:
    """Main pipeline orchestrating all agents."""
    
    def __init__(self, event_callback: Optional[Callable] = None):
        """
        Initialize pipeline.
        
        Args:
            event_callback: Optional callback for real-time events
        """
        self.event_callback = event_callback
        self.analysis_id = str(uuid.uuid4())
    
    async def emit_event(self, event_type: str, data: Dict[str, Any] = None):
        """Emit real-time event to frontend."""
        if self.event_callback:
            event = JuryEvent(
                event_type=event_type,
                data=data or {}
            )
            await self.event_callback(event.model_dump())
    
    async def run(self, query: str) -> AnalysisResponse:
        """
        Run complete analysis pipeline.
        
        Args:
            query: User query to analyze
            
        Returns:
            Complete analysis response
        """
        logger.info(f"JUROR Pipeline starting for query: {query[:100]}")
        
        self.analysis_id = str(uuid.uuid4())
        total_start_time = time.time()
        
        try:
            # 1. Generate initial response
            await self.emit_event("analysis_started", {"analysis_id": self.analysis_id})
            await self.emit_event("agent_started", {"agent": "Generator"})
            
            generator_result = await run_generator_agent(query)
            
            await self.emit_event("agent_completed", {
                "agent": "Generator",
                "score": generator_result.confidence,
                "status": generator_result.status.value
            })
            
            # 2. Run jury agents in parallel
            await self.emit_event("jury_started", {"agents": ["Fact Checker", "Math Validator", "Logic Auditor"]})
            
            # Launch all jury agents concurrently
            jury_tasks = [
                run_fact_checker_agent(generator_result.response, query),
                run_math_validator_agent(generator_result.response),
                run_logic_auditor_agent(generator_result.response),
            ]
            
            jury_results = await asyncio.gather(*jury_tasks, return_exceptions=True)
            
            # Handle exceptions
            fact_checker_result = jury_results[0] if not isinstance(jury_results[0], Exception) else None
            math_validator_result = jury_results[1] if not isinstance(jury_results[1], Exception) else None
            logic_auditor_result = jury_results[2] if not isinstance(jury_results[2], Exception) else None
            
            # Emit jury completion events
            await self.emit_event("agent_completed", {
                "agent": "Fact Checker",
                "score": fact_checker_result.score if fact_checker_result else 0,
                "status": fact_checker_result.status.value if fact_checker_result else "failed"
            })
            await self.emit_event("agent_completed", {
                "agent": "Math Validator",
                "score": math_validator_result.score if math_validator_result else 0,
                "status": math_validator_result.status.value if math_validator_result else "failed"
            })
            await self.emit_event("agent_completed", {
                "agent": "Logic Auditor",
                "score": logic_auditor_result.score if logic_auditor_result else 0,
                "status": logic_auditor_result.status.value if logic_auditor_result else "failed"
            })
            
            # 3. Render verdict
            await self.emit_event("agent_started", {"agent": "Verdict Agent"})
            
            verdict_result = await run_verdict_agent(
                generator_result,
                fact_checker_result,
                math_validator_result,
                logic_auditor_result
            )
            
            await self.emit_event("agent_completed", {
                "agent": "Verdict Agent",
                "verdict": verdict_result.verdict.value,
                "confidence": verdict_result.confidence
            })
            
            # 4. Correct if needed
            corrector_result = None
            if verdict_result.verdict == Verdict.FAIL:
                await self.emit_event("agent_started", {"agent": "Corrector"})
                
                hallucinations = fact_checker_result.hallucinations if fact_checker_result else []
                math_errors = math_validator_result.math_errors if math_validator_result else []
                logic_flaws = logic_auditor_result.logic_flaws if logic_auditor_result else []
                
                corrector_result = await run_corrector_agent(
                    generator_result.response,
                    hallucinations,
                    math_errors,
                    logic_flaws,
                    query
                )
                
                await self.emit_event("agent_completed", {
                    "agent": "Corrector",
                    "status": corrector_result.status.value,
                    "confidence": corrector_result.confidence_after_fix
                })
            
            # 5. Aggregate results
            total_execution_time = time.time() - total_start_time
            
            agent_timings = {
                "Generator": generator_result.execution_time,
                "Fact Checker": fact_checker_result.execution_time if fact_checker_result else 0,
                "Math Validator": math_validator_result.execution_time if math_validator_result else 0,
                "Logic Auditor": logic_auditor_result.execution_time if logic_auditor_result else 0,
                "Verdict Agent": verdict_result.execution_time,
                "Corrector": corrector_result.execution_time if corrector_result else 0,
            }
            
            # Calculate consensus
            fact_check_score = fact_checker_result.score if fact_checker_result and fact_checker_result.applicable else 100
            math_score = math_validator_result.score if math_validator_result and math_validator_result.applicable else 100
            logic_score = logic_auditor_result.score if logic_auditor_result and logic_auditor_result.applicable else 100
            
            consensus_score = calculate_consensus_score(fact_check_score, math_score, logic_score)
            
            # Aggregate findings
            key_findings = aggregate_findings(
                fact_checker_result.hallucinations if fact_checker_result else [],
                math_validator_result.math_errors if math_validator_result else [],
                logic_auditor_result.logic_flaws if logic_auditor_result else []
            )
            
            # Build response
            response = AnalysisResponse(
                analysis_id=self.analysis_id,
                query=query,
                draft_response=generator_result.response,
                verdict=verdict_result.verdict,
                verdict_confidence=verdict_result.confidence,
                risk_level=verdict_result.risk_level,
                corrected_response=corrector_result.corrected_response if corrector_result else None,
                generator_result=generator_result,
                fact_checker_result=fact_checker_result,
                math_validator_result=math_validator_result,
                logic_auditor_result=logic_auditor_result,
                verdict_result=verdict_result,
                corrector_result=corrector_result,
                execution_time=total_execution_time,
                agent_timings=agent_timings,
                jury_consensus_score=consensus_score,
                key_findings=key_findings[:5]
            )
            
            await self.emit_event("analysis_completed", {
                "analysis_id": self.analysis_id,
                "verdict": verdict_result.verdict.value,
                "execution_time": total_execution_time
            })
            
            logger.info(f"JUROR Pipeline completed in {total_execution_time:.2f}s with verdict: {verdict_result.verdict.value}")
            return response
            
        except Exception as e:
            logger.error(f"Pipeline error: {e}", exc_info=True)
            await self.emit_event("analysis_failed", {"error": str(e)})
            raise
