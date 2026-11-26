from typing import List, Dict, Any
from eligibility.rules import evaluate_eligibility
from nlp.embeddings import embedding_engine

def detect_missing_documents(
    scheme_required_docs: List[Dict[str, str]],
    user_uploaded_docs: List[Dict[str, Any]]
) -> Dict[str, Any]:
    """
    Compares scheme required documents against uploaded documents using semantic/alias matching.
    Returns lists of uploaded, matched, and missing documents.
    """
    uploaded_types = [
        str(d.get("document_type", "")).lower() for d in user_uploaded_docs
    ]
    
    # Map common document aliases
    ALIAS_MAP = {
        "income_cert": ["income certificate", "income proof", "salary slip", "tahsildar income cert"],
        "residence_cert": ["residence certificate", "domicile", "proof of residence", "ration card", "address proof"],
        "college_id": ["college id", "student id", "enrollment proof", "college id / enrollment proof"],
        "marks_card": ["marks card", "transcript", "sslc", "puc", "marks card / academic transcript"],
        "caste_cert": ["caste certificate", "community certificate", "caste cert"],
        "disability_cert": ["disability certificate", "udid card", "disability cert"],
        "identity_doc": ["identity document", "aadhaar card", "aadhaar", "pan card", "voter id"]
    }

    matched_docs = []
    missing_docs = []

    for req in scheme_required_docs:
        req_name = req.get("name", "")
        req_code = req.get("code", "")
        aliases = ALIAS_MAP.get(req_code, [req_name.lower()])
        
        # Check if any uploaded document matches
        is_found = False
        for up_type in uploaded_types:
            if any(alias in up_type or up_type in alias for alias in aliases):
                is_found = True
                break
                
        if is_found:
            matched_docs.append(req)
        else:
            missing_docs.append(req)

    return {
        "required_count": len(scheme_required_docs),
        "provided_count": len(matched_docs),
        "missing_count": len(missing_docs),
        "matched_documents": matched_docs,
        "missing_documents": missing_docs
    }


def find_matching_schemes(
    user_profile: Dict[str, Any],
    query_text: str,
    all_schemes: List[Dict[str, Any]],
    user_documents: List[Dict[str, Any]] = None
) -> List[Dict[str, Any]]:
    """
    Hybrid Retrieval Pipeline:
    1. Computes semantic similarity between query/profile and scheme descriptions.
    2. Runs deterministic rule evaluation per scheme.
    3. Runs missing document detection per scheme.
    4. Ranks schemes by overall suitability.
    """
    if user_documents is None:
        user_documents = []

    # Ensure embeddings engine has index
    if not embedding_engine._is_indexed:
        embedding_engine.index_schemes(all_schemes)

    # 1. Semantic Similarity Scores
    search_context = f"{query_text} Education: {user_profile.get('education', '')} State: {user_profile.get('state', '')} Income: {user_profile.get('annual_income', '')}"
    sim_scores = embedding_engine.calculate_similarity(search_context)

    results = []
    for scheme in all_schemes:
        s_id = scheme.get("id")
        rule_result = evaluate_eligibility(user_profile, scheme)
        doc_result = detect_missing_documents(scheme.get("required_documents", []), user_documents)
        
        sim_score = sim_scores.get(s_id, 0.0)
        
        # Combined score for ranking
        status_weight = 1.0 if rule_result["overall_status"] == "potentially_eligible" else 0.4
        rank_score = (sim_score * 0.5) + (status_weight * 0.5)

        results.append({
            "scheme": scheme,
            "rule_evaluation": rule_result,
            "document_check": doc_result,
            "semantic_similarity": sim_score,
            "rank_score": round(rank_score, 3)
        })

    # Sort descending by rank_score
    results.sort(key=lambda x: x["rank_score"], reverse=True)
    return results
