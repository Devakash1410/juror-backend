"""
Parsing utilities for extracting structured data from agent responses.
"""
import json
import re
from typing import Any, Dict, Optional
from app.utils.logger import get_logger

logger = get_logger(__name__)


def extract_json_from_text(text: str) -> Optional[Dict[str, Any]]:
    """
    Extract JSON object from text that might contain markdown or other content.
    
    Args:
        text: Text potentially containing JSON
        
    Returns:
        Parsed JSON dict or None
    """
    # Try to find JSON block
    json_pattern = r'\{.*\}'
    match = re.search(json_pattern, text, re.DOTALL)
    
    if match:
        try:
            return json.loads(match.group())
        except json.JSONDecodeError:
            pass
    
    # Try direct parsing
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        return None


def parse_agent_response(raw_response: str) -> Dict[str, Any]:
    """
    Parse agent response and extract structured data.
    
    Args:
        raw_response: Raw text response from Claude
        
    Returns:
        Structured dict with response data
    """
    # Try JSON extraction first
    parsed = extract_json_from_text(raw_response)
    if parsed:
        return parsed
    
    # Fallback: return raw text
    return {
        "response": raw_response,
        "reasoning": "Raw text response",
        "status": "completed"
    }


def extract_factual_claims(text: str) -> list[str]:
    """Extract potential factual claims from text."""
    sentences = text.split('.')
    claims = [s.strip() for s in sentences if s.strip() and len(s.strip()) > 10]
    return claims[:10]  # Limit to 10 claims


def extract_formulas(text: str) -> list[str]:
    """Extract mathematical formulas from text."""
    # Pattern for common math formulas
    formula_pattern = r'(?:^|\s)([a-zA-Z0-9\s+\-*/()\\.^=]+)(?:\s|$)'
    formulas = re.findall(formula_pattern, text)
    return formulas


def extract_urls(text: str) -> list[str]:
    """Extract URLs from text."""
    url_pattern = r'https?://[^\s]+'
    return re.findall(url_pattern, text)
