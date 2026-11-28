from typing import Dict, Any, List

def simplify_scheme_language(scheme: Dict[str, Any]) -> str:
    """
    NLP text simplification module.
    Translates complex government eligibility criteria into simple, plain language sentences.
    """
    elig = scheme.get("eligibility", {})
    parts = []
    
    # Income
    inc = elig.get("income_limit")
    if inc:
        parts.append(f"Your annual family income must be ₹{inc:,} or less.")
    else:
        parts.append("There is no income restriction for this scheme.")
        
    # Education
    edu = elig.get("education", [])
    if edu and "All" not in edu:
        parts.append(f"You must be enrolled in or pursuing: {', '.join(edu)}.")
        
    # Age
    min_a = elig.get("min_age")
    max_a = elig.get("max_age")
    if min_a and max_a:
        parts.append(f"Your age must be between {min_a} and {max_a} years.")
    elif min_a:
        parts.append(f"You must be at least {min_a} years old.")

    # State
    states = elig.get("states", [])
    if states and "All" not in states:
        parts.append(f"Must be a resident of {', '.join(states)}.")

    # Category
    cats = elig.get("categories", [])
    if cats and "All" not in cats:
        parts.append(f"Open to candidates belonging to: {', '.join(cats)} category.")

    return " ".join(parts)


def generate_natural_explanation(eval_result: Dict[str, Any]) -> str:
    """
    Generates a human-friendly narrative explaining eligibility evaluation results.
    """
    breakdown = eval_result.get("breakdown", {})
    matched_items = []
    unmatched_items = []
    unknown_items = []
    
    for field, info in breakdown.items():
        st = info.get("status")
        if st == "matched":
            matched_items.append(field.capitalize())
        elif st == "unmatched":
            unmatched_items.append(f"{field.capitalize()} ({info.get('user_value')} vs required {info.get('requirement')})")
        elif st == "unknown":
            unknown_items.append(field.capitalize())

    lines = []
    if matched_items:
        lines.append(f"✓ You satisfy the stated {', '.join(matched_items)} requirements.")
        
    if unmatched_items:
        lines.append(f"❌ You do not satisfy the following criteria: {', '.join(unmatched_items)}.")
        
    if unknown_items:
        lines.append(f"❓ The following information could not be verified from your profile/documents: {', '.join(unknown_items)}.")
        
    if eval_result.get("overall_status") == "potentially_eligible":
        lines.append("\nSummary: You are potentially eligible for this scheme based on the available criteria!")
    else:
        lines.append("\nSummary: Please review the missing or unmatched details before applying.")
        
    return "\n".join(lines)
