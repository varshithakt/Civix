import re
from typing import List

def clean_text(text: str) -> str:
    """Removes extra whitespaces, normalizes punctuation, converts to clean string."""
    if not text:
        return ""
    text = re.sub(r'\s+', ' ', text)
    return text.strip()

def tokenize(text: str) -> List[str]:
    """Simple whitespace and punctuation tokenization."""
    cleaned = clean_text(text)
    tokens = re.findall(r'\b\w+\b', cleaned.lower())
    return tokens

def remove_stopwords(tokens: List[str]) -> List[str]:
    """Removes basic English stop words."""
    STOP_WORDS = {
        "a", "an", "the", "and", "or", "but", "if", "because", "as", "what", "which",
        "this", "that", "these", "those", "am", "is", "are", "was", "were", "be", "been",
        "being", "have", "has", "had", "do", "does", "did", "to", "from", "in", "out",
        "on", "off", "over", "under", "again", "further", "then", "once", "here", "there",
        "when", "where", "why", "how", "all", "any", "both", "each", "few", "more",
        "most", "other", "some", "such", "no", "nor", "not", "only", "own", "same",
        "so", "than", "too", "very", "s", "t", "can", "will", "just", "don", "should", "now"
    }
    return [t for t in tokens if t not in STOP_WORDS]
