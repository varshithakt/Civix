import re
from typing import Dict, Any

DOCUMENT_KEYWORDS = {
    "Income Certificate": [
        "income", "annual income", "tahsildar", "revenue officer", "rs.", "lakh", "family income",
        "salaried", "gross income", "certificate of income", "karnataka revenue"
    ],
    "Residence Certificate": [
        "residence", "domicile", "resident", "habitant", "bengaluru", "karnataka", "address",
        "nativity", "permanent resident", "tahsildar"
    ],
    "College ID": [
        "college", "university", "student", "roll no", "enrollment", "usn", "branch", "engineering",
        "department", "valid until", "academic year", "identity card"
    ],
    "Marks Card": [
        "marks", "grade", "gpa", "cgpa", "percentage", "transcript", "sslc", "puc", "semester",
        "examination", "board of secondary education", "passed", "subject"
    ],
    "Caste Certificate": [
        "caste", "community", "obc", "scheduled caste", "scheduled tribe", "sc", "st", "category",
        "backward class", "reservation", "tahsildar"
    ],
    "Disability Certificate": [
        "disability", "handicap", "udid", "medical board", "impairment", "benchmark disability",
        "locomotor", "visual", "hearing", "percentage of disability"
    ],
    "Identity Document": [
        "aadhaar", "uidai", "government of india", "identity", "dob", "gender", "pan card",
        "voter id", "unique identification"
    ]
}

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
    scores = {}
    matched_words = {}

    for doc_type, keywords in DOCUMENT_KEYWORDS.items():
        score = 0
        matches = []
        for kw in keywords:
            if kw in lowered:
                score += 1
                matches.append(kw)
        
        scores[doc_type] = score
        matched_words[doc_type] = matches

    # Find highest scoring document type
    best_doc_type = max(scores, key=scores.get)
    best_score = scores[best_doc_type]

    if best_score == 0:
        return {
            "document_type": "General Certificate",
            "confidence": 35,
            "matched_keywords": []
        }

    # Calculate realistic confidence percentage based on keyword match density
    confidence = min(98, max(50, int((best_score / max(3, len(DOCUMENT_KEYWORDS[best_doc_type]) * 0.4)) * 100)))

    return {
        "document_type": best_doc_type,
        "confidence": confidence,
        "matched_keywords": matched_words[best_doc_type]
    }
