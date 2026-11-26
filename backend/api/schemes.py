from typing import Optional, Dict, Any, List
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from database.db import db_repo
from eligibility.matcher import find_matching_schemes
from nlp.explanation import simplify_scheme_language
from api.documents import STORED_DOCUMENTS

router = APIRouter(prefix="/api/schemes", tags=["Schemes"])

class MatchRequest(BaseModel):
    profile: Dict[str, Any]
    query: Optional[str] = ""

@router.get("/")
def get_all_schemes(category: Optional[str] = None):
    if category:
        return {"schemes": db_repo.search_by_category(category)}
    return {"schemes": db_repo.get_all()}


@router.get("/{scheme_id}")
def get_scheme_detail(scheme_id: str):
    scheme = db_repo.get_by_id(scheme_id)
    if not scheme:
        raise HTTPException(status_code=404, detail="Scheme not found")
        
    simplified = simplify_scheme_language(scheme)
    return {
        "scheme": scheme,
        "simplified_language": simplified
    }


@router.post("/match")
def match_user_schemes(req: MatchRequest):
    all_schemes = db_repo.get_all()
    user_profile = req.profile
    query_text = req.query or ""

    matches = find_matching_schemes(
        user_profile=user_profile,
        query_text=query_text,
        all_schemes=all_schemes,
        user_documents=STORED_DOCUMENTS
    )

    return {
        "query": query_text,
        "profile_used": user_profile,
        "total_schemes_evaluated": len(all_schemes),
        "results": matches
    }
