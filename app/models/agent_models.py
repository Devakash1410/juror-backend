"""
Data models for agent responses and jury verdicts.
"""
from pydantic import BaseModel, Field
from typing import List, Dict, Optional, Any
from enum import Enum
import uuid
from datetime import datetime


class AgentStatus(str, Enum):
    """Status of an agent execution."""
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"
    WARNING = "warning"
    PENDING = "pending"
    ACTIVE = "active"


class RiskLevel(str, Enum):
    """Risk assessment level."""
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"


class Verdict(str, Enum):
    """Final verdict from verdict agent."""
    PASS = "PASS"
    FAIL = "FAIL"
    PARTIAL = "PARTIAL"


class AgentResult(BaseModel):
    """Generic result from any agent."""
    agent_name: str
    status: AgentStatus
    applicable: bool
    score: Optional[float] = None
    confidence: Optional[float] = None
    reasoning: str
    findings: List[str] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)
    execution_time: float = 0.0


class GeneratorResult(AgentResult):
    """Result from Generator Agent."""
    response: str
    confidence: float = Field(ge=0, le=100)


class FactCheckerResult(AgentResult):
    """Result from Fact Checker Agent."""
    factual_claims: List[str] = Field(default_factory=list)
    verified_facts: List[str] = Field(default_factory=list)
    hallucinations: List[str] = Field(default_factory=list)
    sources_checked: List[str] = Field(default_factory=list)
    score: float = Field(ge=0, le=100)


class MathValidatorResult(AgentResult):
    """Result from Math Validator Agent."""
    formulas_detected: List[str] = Field(default_factory=list)
    calculations: List[str] = Field(default_factory=list)
    math_errors: List[str] = Field(default_factory=list)
    correct_formula: Optional[str] = None
    score: float = Field(ge=0, le=100)


class LogicAuditorResult(AgentResult):
    """Result from Logic Auditor Agent."""
    contradictions: List[str] = Field(default_factory=list)
    unsupported_claims: List[str] = Field(default_factory=list)
    logic_flaws: List[str] = Field(default_factory=list)
    score: float = Field(ge=0, le=100)


class CorrectorResult(AgentResult):
    """Result from Corrector Agent."""
    corrected_response: str
    changes_made: List[str] = Field(default_factory=list)
    confidence_after_fix: float = Field(ge=0, le=100)


class VerdictResult(AgentResult):
    """Result from Verdict Agent."""
    verdict: Verdict
    confidence: float = Field(ge=0, le=100)
    risk_level: RiskLevel
    summary: str
    key_issues: List[str] = Field(default_factory=list)
    jury_breakdown: Dict[str, Any] = Field(default_factory=dict)


class JuryEvent(BaseModel):
    """Real-time event streamed to frontend."""
    event_type: str
    agent_name: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    data: Dict[str, Any] = Field(default_factory=dict)


class AnalysisRequest(BaseModel):
    """Request to analyze a query."""
    query: str = Field(..., min_length=1, max_length=5000)
    stream_updates: bool = True


class AnalysisResponse(BaseModel):
    """Complete analysis response for frontend."""
    analysis_id: str
    query: str
    draft_response: str
    verdict: Verdict
    verdict_confidence: float
    risk_level: RiskLevel
    corrected_response: Optional[str] = None
    
    # Agent results
    generator_result: GeneratorResult
    fact_checker_result: Optional[FactCheckerResult] = None
    math_validator_result: Optional[MathValidatorResult] = None
    logic_auditor_result: Optional[LogicAuditorResult] = None
    verdict_result: VerdictResult
    corrector_result: Optional[CorrectorResult] = None
    
    # Metrics
    execution_time: float
    agent_timings: Dict[str, float] = Field(default_factory=dict)
    total_tokens_used: Optional[int] = None
    
    # Jury consensus
    jury_consensus_score: float = Field(ge=0, le=100)
    key_findings: List[str] = Field(default_factory=list)
