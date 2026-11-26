import re
from typing import Optional, Dict, Any, Tuple

INDIAN_STATES = [
    "Karnataka", "Maharashtra", "Tamil Nadu", "Kerala", "Andhra Pradesh", "Telangana",
    "Delhi", "Uttar Pradesh", "Bihar", "West Bengal", "Gujarat", "Rajasthan",
    "Punjab", "Haryana", "Madhya Pradesh", "Odisha", "Assam"
]

STATE_ALIASES = {
    "ka": "Karnataka",
    "bengaluru": "Karnataka",
    "bangalore": "Karnataka",
    "mysuru": "Karnataka",
    "mh": "Maharashtra",
    "mumbai": "Maharashtra",
    "pune": "Maharashtra",
    "tn": "Tamil Nadu",
    "chennai": "Tamil Nadu",
    "kl": "Kerala",
    "ts": "Telangana",
    "hyderabad": "Telangana",
    "ap": "Andhra Pradesh",
    "dl": "Delhi",
    "up": "Uttar Pradesh"
}

def normalize_income(text: str) -> Tuple[Optional[float], str]:
    """
    Parses natural language income expressions and normalizes to annual income (INR).
    Returns (annual_income_amount, income_type ['family'|'individual'|'unknown']).
    Handles:
      - ₹1.8 lakh / 1.8 lakhs / 1.8L
      - 15000 / month, 15,000 pm, 15k monthly
      - Rs. 1,80,000 per annum
    """
    if not text:
        return None, "unknown"
    
    lowered = text.lower()
    
    # Check income scope
    income_type = "family" if any(w in lowered for w in ["family", "household", "parents", "father", "mother"]) else "individual"
    
    # 1. Check for Lakh pattern e.g., 1.8 lakh, 2.5 lakhs, ₹ 1.5L
    lakh_match = re.search(r'(?:rs\.?|₹|\b)?\s*([\d\.]+)\s*(?:lakhs?|lakh|l)\b', lowered)
    if lakh_match:
        val = float(lakh_match.group(1))
        annual = val * 100000
        # Check if it was per month (rare for lakhs, but check)
        if any(m in lowered for m in ["pm", "per month", "monthly"]):
            annual *= 12
        return annual, income_type

    # 2. Check for Thousand pattern e.g., 15k, 15 thousand
    k_match = re.search(r'(?:rs\.?|₹|\b)?\s*([\d\.]+)\s*(?:k|thousand)\b', lowered)
    if k_match:
        val = float(k_match.group(1)) * 1000
        if any(m in lowered for m in ["pm", "per month", "monthly", "/month", "/pm"]):
            return val * 12, income_type
        return val, income_type

    # 3. Check for Monthly amount e.g., 15,000 per month / 15000 pm / 15000/month
    monthly_match = re.search(r'(?:rs\.?|₹|\b)?\s*([\d,]+)\s*(?:per month|monthly|\/pm|\/month|pm)\b', lowered)
    if monthly_match:
        raw_num = monthly_match.group(1).replace(',', '')
        val = float(raw_num)
        return val * 12, income_type

    # 4. Check for Standard numeric amount with currency indicators or keywords
    num_match = re.search(r'(?:rs\.?|₹|income|earns?|salary)?\s*([\d,]{4,10})\b', lowered)
    if num_match:
        raw_num = num_match.group(1).replace(',', '')
        val = float(raw_num)
        # If income is < 40000, it's likely a monthly figure unless specified per annum
        if val < 40000 and not any(a in lowered for a in ["annual", "annually", "per annum", "pa", "year"]):
            return val * 12, income_type
        return val, income_type

    return None, "unknown"


def normalize_state(text: str) -> Optional[str]:
    """Normalizes state names from raw strings."""
    if not text:
        return None
    lowered = text.lower().strip()
    
    # Check direct aliases
    for alias, std in STATE_ALIASES.items():
        if alias in lowered:
            return std
            
    # Check state list
    for state in INDIAN_STATES:
        if state.lower() in lowered:
            return state
            
    return None


def normalize_education(text: str) -> str:
    """Standardizes educational levels."""
    if not text:
        return "unknown"
    lowered = text.lower()
    
    if any(w in lowered for w in ["engineering", "btech", "b.tech", "b.e", "be student"]):
        return "engineering"
    elif any(w in lowered for w in ["undergraduate", "degree", "bsc", "bcom", "ba", "bba", "college"]):
        return "undergraduate"
    elif any(w in lowered for w in ["postgraduate", "mtech", "msc", "mcom", "ma", "mba", "master"]):
        return "postgraduate"
    elif any(w in lowered for w in ["diploma", "polytechnic"]):
        return "diploma"
    elif any(w in lowered for w in ["school", "10th", "12th", "puc", "pu", "high school", "8th", "9th"]):
        return "school"
    
    return text.strip().title()


def normalize_category(text: str) -> str:
    """Normalizes caste / social category."""
    if not text:
        return "General"
    lowered = text.lower()
    
    if "obc" in lowered or "backward" in lowered or "bc" in lowered:
        return "OBC"
    elif "sc" in lowered or "scheduled caste" in lowered:
        return "SC"
    elif "st" in lowered or "scheduled tribe" in lowered:
        return "ST"
    elif "ews" in lowered or "economically weaker" in lowered:
        return "EWS"
    elif "minority" in lowered or "muslim" in lowered or "christian" in lowered:
        return "Minority"
    
    return "General"
