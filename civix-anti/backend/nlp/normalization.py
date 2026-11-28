import re
from typing import Optional, Tuple

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
    "mysore": "Karnataka",
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
    lakh_match = re.search(r'(?:rs\.?|₹|\b)\s*([\d\.]+)\s*(?:lakhs?|lakh|l)\b', lowered)
    if lakh_match:
        try:
            val = float(lakh_match.group(1))
            annual = val * 100000
            if any(m in lowered for m in ["pm", "per month", "monthly"]):
                annual *= 12
            return annual, income_type
        except ValueError:
            pass

    # 2. Check for Thousand pattern e.g., 15k, 15 thousand
    k_match = re.search(r'(?:rs\.?|₹|\b)\s*([\d\.]+)\s*(?:k|thousand)\b', lowered)
    if k_match:
        try:
            val = float(k_match.group(1)) * 1000
            if any(m in lowered for m in ["pm", "per month", "monthly", "/month", "/pm"]):
                return val * 12, income_type
            return val, income_type
        except ValueError:
            pass

    # 3. Check for Monthly amount e.g., 15,000 per month / 15000 pm / 15000/month
    monthly_match = re.search(r'(?:rs\.?|₹|\b)\s*([\d,]+)\s*(?:per month|monthly|\/pm|\/month|pm)\b', lowered)
    if monthly_match:
        raw_num = monthly_match.group(1).replace(',', '')
        if raw_num:
            return float(raw_num) * 12, income_type

    # 4. Check for numeric amount paired with explicit currency, income keyword, or annual suffix
    num_match = re.search(
        r'(?:rs\.?|inr|₹|(?:annual|family|household|total)?\s*income(?:\s+(?:is|of|around|about))?|earns?(?:\s+about|\s+around)?|salary(?:\s+is|\s+of)?)\s*[:\-\=]?\s*(?:rs\.?|inr|₹)?\s*([\d,]{4,10})\b',
        lowered
    )
    if not num_match:
        num_match = re.search(
            r'\b([\d,]{4,10})\s*(?:per annum|annum|per year|annually|p\.a\.|\/\-)\b',
            lowered
        )

    if num_match:
        raw_num = num_match.group(1).replace(',', '')
        if raw_num:
            val = float(raw_num)
            if val < 40000 and not any(a in lowered for a in ["annual", "annually", "per annum", "annum", "pa", "year"]):
                return val * 12, income_type
            return val, income_type

    return None, "unknown"


def normalize_state(text: str) -> Optional[str]:
    """Normalizes state names from raw strings using word boundaries."""
    if not text:
        return None
    lowered = text.lower().strip()

    # Check full state names first
    for state in INDIAN_STATES:
        if re.search(rf'\b{re.escape(state.lower())}\b', lowered):
            return state

    # Check city and abbreviation aliases with word boundaries
    for alias, std in STATE_ALIASES.items():
        if re.search(rf'\b{re.escape(alias)}\b', lowered):
            return std

    return None


def normalize_education(text: str) -> str:
    """Standardizes educational levels; returns 'unknown' if none detected."""
    if not text:
        return "unknown"
    lowered = text.lower()

    if any(re.search(rf'\b{p}\b', lowered) for p in ["engineering", "btech", r"b\.tech", r"b\.e", "be student", "aicte"]):
        return "engineering"
    elif any(re.search(rf'\b{p}\b', lowered) for p in ["postgraduate", "mtech", r"m\.tech", "msc", "mcom", "mba", "master"]):
        return "postgraduate"
    elif any(re.search(rf'\b{p}\b', lowered) for p in ["undergraduate", "degree", "bsc", "bcom", "bba", "college"]):
        return "undergraduate"
    elif any(re.search(rf'\b{p}\b', lowered) for p in ["diploma", "polytechnic"]):
        return "diploma"
    elif any(re.search(rf'\b{p}\b', lowered) for p in ["school", "10th", "12th", "sslc", "puc", "matriculation", "high school", "8th", "9th", "secondary"]):
        return "school"

    return "unknown"


def normalize_category(text: str) -> str:
    """Normalizes caste / social category using word boundaries; returns 'unknown' if absent."""
    if not text:
        return "unknown"
    lowered = text.lower()

    if re.search(r'\b(obc|other backward|2a|2b|3a|3b|cat[\-\s]?i+)\b|backward\s*class', lowered):
        return "OBC"
    elif re.search(r'\b(sc|scheduled caste)\b', lowered):
        return "SC"
    elif re.search(r'\b(st|scheduled tribe)\b', lowered):
        return "ST"
    elif re.search(r'\b(ews|economically weaker)\b', lowered):
        return "EWS"
    elif re.search(r'\b(minority|muslim|christian|jain|sikh)\b', lowered):
        return "Minority"
    elif re.search(r'\b(general|unreserved|gm)\b', lowered):
        return "General"

    return "unknown"
