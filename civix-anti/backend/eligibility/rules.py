from typing import Dict, Any, List

def evaluate_eligibility(profile: Dict[str, Any], scheme: Dict[str, Any]) -> Dict[str, Any]:
    """
    Evaluates a user's structured profile against a scheme's eligibility rules.
    Returns criterion-level status breakdown and an overall decision status.
    Statuses per criterion: 'matched', 'unmatched', 'unknown'.
    """
    eligibility_rules = scheme.get("eligibility", {})
    breakdown = {}
    
    # 1. Age Evaluation
    min_age = eligibility_rules.get("min_age")
    max_age = eligibility_rules.get("max_age")
    user_age = profile.get("age")
    
    if user_age is None or user_age == "unknown":
        breakdown["age"] = {
            "status": "unknown",
            "user_value": None,
            "requirement": f"{min_age}-{max_age}" if min_age and max_age else "Not specified"
        }
    else:
        try:
            u_age = int(user_age)
            satisfied = True
            if min_age is not None and u_age < min_age:
                satisfied = False
            if max_age is not None and u_age > max_age:
                satisfied = False
                
            breakdown["age"] = {
                "status": "matched" if satisfied else "unmatched",
                "user_value": u_age,
                "requirement": f"{min_age} - {max_age} years" if min_age and max_age else f"Min {min_age}"
            }
        except (ValueError, TypeError):
            breakdown["age"] = {
                "status": "unknown",
                "user_value": user_age,
                "requirement": f"{min_age}-{max_age}"
            }

    # 2. Income Evaluation
    income_limit = eligibility_rules.get("income_limit")
    user_income = profile.get("annual_income")
    
    if user_income is None or user_income == "unknown":
        breakdown["income"] = {
            "status": "unknown",
            "user_value": None,
            "requirement": f"<= ₹{income_limit:,}" if income_limit else "No limit"
        }
    else:
        try:
            u_income = float(user_income)
            if income_limit is not None:
                satisfied = u_income <= income_limit
                breakdown["income"] = {
                    "status": "matched" if satisfied else "unmatched",
                    "user_value": u_income,
                    "requirement": f"<= ₹{income_limit:,}"
                }
            else:
                breakdown["income"] = {
                    "status": "matched",
                    "user_value": u_income,
                    "requirement": "No income limit"
                }
        except (ValueError, TypeError):
            breakdown["income"] = {
                "status": "unknown",
                "user_value": user_income,
                "requirement": f"<= ₹{income_limit:,}" if income_limit else "No limit"
            }

    # 3. Education Evaluation
    req_edu = [e.lower() for e in eligibility_rules.get("education", [])]
    user_edu = str(profile.get("education", "")).lower()
    
    if not user_edu or user_edu == "unknown":
        breakdown["education"] = {
            "status": "unknown",
            "user_value": None,
            "requirement": ", ".join(eligibility_rules.get("education", []))
        }
    else:
        if "all" in req_edu:
            satisfied = True
        else:
            # Check semantic match or partial substring match
            satisfied = any(req in user_edu or user_edu in req for req in req_edu)
            
        breakdown["education"] = {
            "status": "matched" if satisfied else "unmatched",
            "user_value": profile.get("education"),
            "requirement": ", ".join(eligibility_rules.get("education", []))
        }

    # 4. State / Location Evaluation
    req_states = [s.lower() for s in eligibility_rules.get("states", [])]
    user_state = str(profile.get("state", "")).lower()
    
    if not user_state or user_state == "unknown":
        breakdown["state"] = {
            "status": "unknown",
            "user_value": None,
            "requirement": ", ".join(eligibility_rules.get("states", []))
        }
    else:
        if "all" in req_states:
            satisfied = True
        else:
            satisfied = any(s == user_state or s in user_state for s in req_states)
            
        breakdown["state"] = {
            "status": "matched" if satisfied else "unmatched",
            "user_value": profile.get("state"),
            "requirement": ", ".join(eligibility_rules.get("states", []))
        }

    # 5. Category Evaluation
    req_cats = [c.lower() for c in eligibility_rules.get("categories", [])]
    user_cat = str(profile.get("category", "")).lower()
    
    if not user_cat or user_cat == "unknown":
        breakdown["category"] = {
            "status": "unknown",
            "user_value": None,
            "requirement": ", ".join(eligibility_rules.get("categories", []))
        }
    else:
        if "all" in req_cats:
            satisfied = True
        else:
            satisfied = any(c == user_cat for c in req_cats)
            
        breakdown["category"] = {
            "status": "matched" if satisfied else "unmatched",
            "user_value": profile.get("category"),
            "requirement": ", ".join(eligibility_rules.get("categories", []))
        }

    # 6. Gender Evaluation
    req_gender = eligibility_rules.get("gender", "All").lower()
    user_gender = str(profile.get("gender", "")).lower()
    
    if not user_gender or user_gender == "unknown":
        breakdown["gender"] = {
            "status": "unknown",
            "user_value": None,
            "requirement": eligibility_rules.get("gender", "All")
        }
    else:
        if req_gender == "all" or user_gender == req_gender:
            satisfied = True
        else:
            satisfied = False
        breakdown["gender"] = {
            "status": "matched" if satisfied else "unmatched",
            "user_value": profile.get("gender"),
            "requirement": eligibility_rules.get("gender", "All")
        }

    # Overall Evaluation Summary
    statuses = [v["status"] for v in breakdown.values()]
    if "unmatched" in statuses:
        overall_status = "ineligible"
        summary_text = "Does not meet one or more mandatory eligibility criteria."
    elif all(s == "matched" for s in statuses):
        overall_status = "potentially_eligible"
        summary_text = "Potentially eligible based on the information provided."
    else:
        overall_status = "potential_match_with_unknowns"
        summary_text = "Potential match based on available scheme criteria. Some details need verification."

    return {
        "scheme_id": scheme.get("id"),
        "scheme_name": scheme.get("name"),
        "overall_status": overall_status,
        "summary_text": summary_text,
        "disclaimer": "Potentially eligible based on the information provided. Official eligibility is subject to government verification.",
        "breakdown": breakdown
    }
