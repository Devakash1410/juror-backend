"""
Scoring and consensus utilities for jury verdict aggregation.
"""
from typing import Dict, List
from app.utils.logger import get_logger

logger = get_logger(__name__)


def calculate_consensus_score(
    fact_check_score: float,
    math_score: float,
    logic_score: float,
    weights: Dict[str, float] = None
) -> float:
    """
    Calculate weighted consensus score from jury agents.
    
    Args:
        fact_check_score: Score from Fact Checker (0-100)
        math_score: Score from Math Validator (0-100)
        logic_score: Score from Logic Auditor (0-100)
        weights: Custom weights for each agent
        
    Returns:
        Weighted consensus score (0-100)
    """
    if weights is None:
        weights = {
            "fact_check": 0.4,
            "math": 0.35,
            "logic": 0.25
        }
    
    scores = [fact_check_score, math_score, logic_score]
    weight_values = [weights["fact_check"], weights["math"], weights["logic"]]
    
    # Filter out None/invalid scores
    valid_pairs = [(s, w) for s, w in zip(scores, weight_values) if s is not None]
    
    if not valid_pairs:
        return 50.0
    
    total_weight = sum(w for _, w in valid_pairs)
    weighted_sum = sum(s * w for s, w in valid_pairs)
    
    return (weighted_sum / total_weight) if total_weight > 0 else 50.0


def determine_risk_level(consensus_score: float) -> str:
    """
    Determine risk level based on consensus score.
    
    Args:
        consensus_score: Score from 0-100
        
    Returns:
        Risk level: "LOW", "MEDIUM", or "HIGH"
    """
    if consensus_score >= 80:
        return "LOW"
    elif consensus_score >= 60:
        return "MEDIUM"
    else:
        return "HIGH"


def aggregate_findings(
    fact_check_findings: List[str],
    math_findings: List[str],
    logic_findings: List[str]
) -> List[str]:
    """Aggregate findings from all jury agents."""
    all_findings = []
    
    if fact_check_findings:
        all_findings.extend([f"[Fact Check] {f}" for f in fact_check_findings])
    if math_findings:
        all_findings.extend([f"[Math] {f}" for f in math_findings])
    if logic_findings:
        all_findings.extend([f"[Logic] {f}" for f in logic_findings])
    
    return all_findings
