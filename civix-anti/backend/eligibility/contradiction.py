from typing import List, Dict, Any

def detect_profile_contradictions(extracted_documents: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Compares extracted information across multiple uploaded documents.
    Identifies inconsistencies in Income, Age/DOB, State, or Category.
    """
    if len(extracted_documents) < 2:
        return []

    alerts = []
    incomes = []
    ages = []
    states = []

    for doc in extracted_documents:
        doc_name = doc.get("file_name", "Document")
        profile = doc.get("extracted_profile", {})
        
        inc = profile.get("annual_income")
        if inc != "unknown" and inc is not None:
            incomes.append({"doc_name": doc_name, "value": inc})
            
        age = profile.get("age")
        if age != "unknown" and age is not None:
            ages.append({"doc_name": doc_name, "value": age})

        state = profile.get("state")
        if state != "unknown" and state is not None:
            states.append({"doc_name": doc_name, "value": state})

    # 1. Income Contradiction Check
    if len(incomes) > 1:
        first_val = incomes[0]["value"]
        for item in incomes[1:]:
            # If difference is greater than 10%
            if abs(item["value"] - first_val) > (first_val * 0.1):
                alerts.append({
                    "field": "annual_income",
                    "title": "Potential Income Mismatch Detected",
                    "severity": "warning",
                    "description": f"Inconsistency found between documents: '{incomes[0]['doc_name']}' states ₹{incomes[0]['value']:,} while '{item['doc_name']}' states ₹{item['value']:,}.",
                    "conflicting_documents": [incomes[0]['doc_name'], item['doc_name']]
                })
                break

    # 2. Age / DOB Contradiction Check
    if len(ages) > 1:
        first_age = ages[0]["value"]
        for item in ages[1:]:
            if abs(item["value"] - first_age) >= 1:
                alerts.append({
                    "field": "age",
                    "title": "Potential Date-of-Birth / Age Mismatch Detected",
                    "severity": "warning",
                    "description": f"Inconsistency found between documents: '{ages[0]['doc_name']}' indicates age {ages[0]['value']} while '{item['doc_name']}' indicates age {item['value']}.",
                    "conflicting_documents": [ages[0]['doc_name'], item['doc_name']]
                })
                break

    # 3. State Contradiction Check
    if len(states) > 1:
        first_state = states[0]["value"]
        for item in states[1:]:
            if item["value"] != first_state:
                alerts.append({
                    "field": "state",
                    "title": "Potential State / Domicile Mismatch Detected",
                    "severity": "info",
                    "description": f"State mismatch: '{states[0]['doc_name']}' states '{states[0]['value']}' while '{item['doc_name']}' states '{item['value']}'.",
                    "conflicting_documents": [states[0]['doc_name'], item['doc_name']]
                })
                break

    return alerts
