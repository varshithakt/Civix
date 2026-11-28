import re
from typing import Dict, Any, List, Tuple

# Weighted keywords per document category: (pattern, weight, is_word_boundary)
DOCUMENT_RULES: Dict[str, List[Tuple[str, int, bool]]] = {
    "Income Certificate": [
        ("income certificate", 4, False),
        ("income and caste", 3, False),
        ("incomeand caste", 3, False),
        ("annual family income", 3, False),
        ("annual income", 3, False),
        ("gross annual", 3, False),
        ("certificate of income", 4, False),
        ("family income", 2, False),
        ("gross income", 2, False),
        ("does not exceed", 2, False),
        ("pay scale", 2, False),
        ("tahsildar", 2, False),
        ("nadakacheri", 2, False),
        ("revenue department", 2, False),
        ("form-e", 2, False),
        ("income", 2, False),
        ("annum", 1, True),
        ("rupees", 1, True),
        ("lakh", 1, False),
    ],
    "Caste Certificate": [
        ("caste certificate", 4, False),
        ("income and caste", 3, False),
        ("incomeand caste", 3, False),
        ("community certificate", 4, False),
        ("scheduled caste", 3, False),
        ("scheduled tribe", 3, False),
        ("backward class", 3, False),
        ("backward", 2, False),
        ("belongs to", 2, False),
        ("sub caste", 2, False),
        ("category", 2, False),
        ("obc", 2, True),
        ("reservation", 2, True),
        ("caste", 2, False),
        ("sc", 1, True),
        ("st", 1, True),
        ("tahsildar", 1, False),
    ],
    "Marks Card": [
        ("statement of marks", 4, False),
        ("marks card", 4, False),
        ("marksheet", 4, False),
        ("marks sheet", 4, False),
        ("grade card", 4, False),
        ("academic transcript", 4, False),
        ("secondary school leaving certificate", 4, False),
        ("board of secondary education", 3, False),
        ("sslc", 3, True),
        ("puc", 3, True),
        ("cbse", 3, True),
        ("icse", 3, True),
        ("kseeb", 3, True),
        ("matriculation", 3, True),
        ("marks obtained", 3, False),
        ("maximum marks", 3, False),
        ("total marks", 3, False),
        ("cgpa", 2, True),
        ("sgpa", 2, True),
        ("percentage", 2, True),
        ("semester", 2, True),
        ("examination", 2, True),
        ("register number", 2, False),
        ("roll no", 2, False),
        ("marks", 1, True),
        ("grade", 1, True),
        ("subject", 1, True),
        ("passed", 1, True),
    ],
    "College ID": [
        ("bonafide certificate", 4, False),
        ("bonafide", 3, True),
        ("study certificate", 4, False),
        ("college id", 4, False),
        ("student identity card", 4, False),
        ("aicte", 3, True),
        ("pragati", 3, True),
        ("saksham", 3, True),
        ("promotion certificate", 3, False),
        ("renewal", 2, True),
        ("institute of technology", 3, False),
        ("engineering college", 3, False),
        ("principal", 2, True),
        ("usn", 2, True),
        ("enrollment", 2, True),
        ("academic year", 2, False),
        ("pursuing", 2, True),
        ("college", 1, True),
        ("university", 1, True),
        ("student", 1, True),
        ("semester", 1, True),
        ("department", 1, True),
        ("branch", 1, True),
        ("engineering", 1, True),
    ],
    "Residence Certificate": [
        ("residence certificate", 4, False),
        ("domicile certificate", 4, False),
        ("nativity certificate", 4, False),
        ("residential certificate", 4, False),
        ("proof of residence", 4, False),
        ("permanent resident", 3, False),
        ("residing at", 2, False),
        ("domicile", 3, True),
        ("nativity", 3, True),
        ("ration card", 2, False),
        ("residence", 2, True),
        ("resident", 1, True),
        ("address", 1, True),
        ("taluk", 1, True),
        ("hobli", 1, True),
    ],
    "Disability Certificate": [
        ("disability certificate", 4, False),
        ("unique disability id", 4, False),
        ("benchmark disability", 3, False),
        ("percentage of disability", 3, False),
        ("udid", 3, True),
        ("medical board", 2, False),
        ("impairment", 2, True),
        ("locomotor", 2, True),
        ("disability", 2, True),
        ("handicap", 2, True),
    ],
    "Identity Document": [
        ("aadhaar", 4, True),
        ("uidai", 4, True),
        ("unique identification", 4, False),
        ("permanent account number", 4, False),
        ("income tax department", 3, False),
        ("election commission", 3, False),
        ("pan card", 3, False),
        ("voter id", 3, False),
        ("government of india", 2, False),
        ("date of birth", 1, False),
        ("dob", 1, True),
        ("identity", 1, True),
    ],
}


def _match_pattern(text: str, pattern: str, word_boundary: bool) -> bool:
    if word_boundary:
        return bool(re.search(rf"\b{re.escape(pattern)}\b", text))
    return pattern in text


def classify_document(text: str) -> Dict[str, Any]:
    """
    Classifies OCR document text into standard document categories.
    Returns detected label, confidence score (0-100%), and matched keywords.
    """
    if not text or len(text.strip()) == 0:
        return {
            "document_type": "Unknown Document",
            "confidence": 0,
            "matched_keywords": []
        }

    lowered = text.lower()
    scores: Dict[str, int] = {}
    matched_words: Dict[str, List[str]] = {}

    for doc_type, rules in DOCUMENT_RULES.items():
        score = 0
        matches = []
        for pattern, weight, use_boundary in rules:
            if _match_pattern(lowered, pattern, use_boundary):
                score += weight
                matches.append(pattern)
        scores[doc_type] = score
        matched_words[doc_type] = matches

    ranked = sorted(scores.items(), key=lambda kv: kv[1], reverse=True)
    best_doc_type, best_score = ranked[0]

    if best_score == 0:
        return {
            "document_type": "General Certificate",
            "confidence": 35,
            "matched_keywords": []
        }

    # Confidence scaled cleanly from weighted score (e.g. score 4 -> ~68%, score 8+ -> ~92-98%)
    confidence = min(98, max(52, int(45 + (best_score / 10.0) * 50)))

    # Include secondary detected types if close (e.g. combined Income & Caste Certificate)
    secondary = [
        doc_type for doc_type, sc in ranked[1:]
        if sc >= 4 and sc >= best_score * 0.6
    ]

    result: Dict[str, Any] = {
        "document_type": best_doc_type,
        "confidence": confidence,
        "matched_keywords": matched_words[best_doc_type],
    }
    if secondary:
        result["secondary_types"] = secondary
    return result
