from fastapi import APIRouter
from pydantic import BaseModel
from typing import Dict, Any
from nlp.intent import intent_classifier
from nlp.extraction import extract_user_profile

router = APIRouter(prefix="/api/nlp", tags=["NLP"])

class QueryRequest(BaseModel):
    query: str

@router.post("/process-query")
def process_natural_language_query(req: QueryRequest):
    query_text = req.query.strip()
    
    # 1. Intent Classification
    intent_res = intent_classifier.classify(query_text)
    
    # 2. Entity & User Profile Extraction
    extracted_profile = extract_user_profile(query_text)
    
    return {
        "original_query": query_text,
        "intent": intent_res,
        "extracted_profile": extracted_profile
    }
