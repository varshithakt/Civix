import re
from typing import Dict, Any
from nlp.normalization import (
    normalize_income,
    normalize_state,
    normalize_education,
    normalize_category
)

def extract_user_profile(text: str) -> Dict[str, Any]:
    """
    Extracts structured user profile entity fields from natural language or OCR document text.
    Handles varied inputs, edge cases, and marks missing attributes as 'unknown'.
    """
    if not text:
        return {
            "age": "unknown",
            "annual_income": "unknown",
            "income_type": "unknown",
            "education": "unknown",
            "state": "unknown",
            "district": "unknown",
            "occupation": "unknown",
            "category": "unknown",
            "gender": "unknown",
            "disability_pct": "unknown"
        }

    lowered = text.lower()
    profile: Dict[str, Any] = {}

    # 1. Age Extraction
    age_match = re.search(r'\b(\d{1,2})\s*(?:-| )?(?:year|yrs?|yo|years old)\b', lowered)
    if not age_match:
        age_match = re.search(r'\bage\s*[:\-\=]?\s*(\d{1,2})\b', lowered)
        
    if age_match:
        profile["age"] = int(age_match.group(1))
    else:
        # Check DOB format e.g. 12/05/2004 or 2004
        dob_match = re.search(r'\b(?:dob|date of birth)\s*[:\-\=]?\s*(\d{2}[\/\.-]\d{2}[\/\.-]\d{4}|\d{4})\b', lowered)
        if dob_match:
            year_match = re.search(r'(19\d\d|20\d\d)', dob_match.group(1))
            if year_match:
                birth_year = int(year_match.group(1))
                profile["age"] = max(0, 2026 - birth_year)
            else:
                profile["age"] = "unknown"
        else:
            profile["age"] = "unknown"

    # 2. Income Extraction
    income_val, income_type = normalize_income(text)
    profile["annual_income"] = int(income_val) if income_val is not None else "unknown"
    profile["income_type"] = income_type

    # 3. State & District Extraction
    state_val = normalize_state(text)
    profile["state"] = state_val if state_val else "unknown"

    # Common District Extraction
    district_patterns = ["bengaluru", "bangalore", "mysuru", "mysore", "pune", "mumbai", "chennai", "hyderabad", "delhi"]
    found_district = None
    for d in district_patterns:
        if d in lowered:
            found_district = d.title()
            break
    profile["district"] = found_district if found_district else "unknown"

    # 4. Education Extraction
    edu_val = normalize_education(text)
    profile["education"] = edu_val if edu_val != "unknown" else "unknown"

    # 5. Category / Caste Extraction
    cat_val = normalize_category(text)
    profile["category"] = cat_val

    # 6. Occupation Extraction
    if any(w in lowered for w in ["student", "studying", "college", "undergraduate", "engineering", "school"]):
        profile["occupation"] = "student"
    elif any(w in lowered for w in ["farmer", "agriculture", "farming", "landholding"]):
        profile["occupation"] = "farmer"
    elif any(w in lowered for w in ["business", "shopkeeper", "artisan", "self-employed", "entrepreneur"]):
        profile["occupation"] = "entrepreneur"
    else:
        profile["occupation"] = "unknown"

    # 7. Gender Extraction
    if any(w in lowered for w in ["female", "woman", "girl", "daughter", "mother"]):
        profile["gender"] = "Female"
    elif any(w in lowered for w in ["male", "man", "boy", "son", "father"]):
        profile["gender"] = "Male"
    else:
        profile["gender"] = "unknown"

    # 8. Disability Percentage Extraction
    dis_match = re.search(r'(\d{1,3})\s*%\s*(?:disability|handicap|disabled)', lowered)
    if dis_match:
        profile["disability_pct"] = int(dis_match.group(1))
    else:
        profile["disability_pct"] = "unknown"

    return profile
