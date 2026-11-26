from typing import Dict, Any, Optional
from fastapi import APIRouter
from pydantic import BaseModel
from database.db import db_repo
from nlp.intent import intent_classifier
from nlp.explanation import simplify_scheme_language

router = APIRouter(prefix="/api/chat", tags=["Scheme Chatbot"])

class ChatMessage(BaseModel):
    message: str
    user_profile: Optional[Dict[str, Any]] = None
    selected_scheme_id: Optional[str] = None

@router.post("/ask")
def answer_scheme_question(req: ChatMessage):
    user_msg = req.message.strip()
    profile = req.user_profile or {}
    
    # 1. Intent Detection
    intent_data = intent_classifier.classify(user_msg)
    intent = intent_data["intent"]

    # 2. Scheme context
    all_schemes = db_repo.get_all()
    target_scheme = None
    if req.selected_scheme_id:
        target_scheme = db_repo.get_by_id(req.selected_scheme_id)

    lowered = user_msg.lower()
    
    # Check if a scheme is mentioned by name in message
    if not target_scheme:
        for s in all_schemes:
            if s["name"].lower() in lowered or s["id"].lower() in lowered or s["category"].lower() in lowered:
                target_scheme = s
                break

    # Grounded QA Response synthesis
    if intent == "GET_REQUIRED_DOCUMENTS":
        if target_scheme:
            docs = [d["name"] for d in target_scheme.get("required_documents", [])]
            reply = f"For **{target_scheme['name']}**, you need to provide the following documents:\n\n"
            reply += "\n".join([f"- {d}" for d in docs])
            reply += f"\n\n🔗 Official Source: [{target_scheme['source_url']}]({target_scheme['source_url']})"
        else:
            reply = "Common required documents for most government schemes include:\n- Income Certificate\n- Residence / Domicile Certificate\n- Aadhaar Card / Identity Proof\n- Academic Marks Card or College ID\n\nPlease select a specific scheme for exact requirements!"

    elif intent == "EXPLAIN_ELIGIBILITY":
        if target_scheme:
            simplified = simplify_scheme_language(target_scheme)
            reply = f"Here is the eligibility criteria for **{target_scheme['name']}** in plain language:\n\n{simplified}\n\n"
            if profile.get("annual_income") != "unknown":
                reply += f"Your current income in profile is ₹{profile.get('annual_income'):,}.\n"
            reply += f"🔗 Official Source: [{target_scheme['source_url']}]({target_scheme['source_url']})"
        else:
            reply = "Eligibility is evaluated deterministically against age, family income limit, state domicile, education level, and category. Upload your documents or enter your query to view a criterion-by-criterion breakdown!"

    elif intent == "FIND_AGRICULTURE_SCHEME":
        agri_schemes = [s for s in all_schemes if s["category"] == "Agriculture"]
        if agri_schemes:
            s = agri_schemes[0]
            reply = f"Here is a key agriculture scheme for farmers: **{s['name']}**.\n\n{s['simplified_description']}\n\nBenefits: {s['benefits']}\n🔗 Official Portal: [{s['source_url']}]({s['source_url']})"
        else:
            reply = "We found agricultural support programs including PM Kisan Samman Nidhi Yojana. Check the Scheme Discovery tab for details!"

    elif intent == "SCHEME_INFORMATION":
        if target_scheme:
            reply = f"**{target_scheme['name']}** ({target_scheme['category']})\n\n{target_scheme['description']}\n\n**Benefits**: {target_scheme['benefits']}\n\n🔗 Official Link: [{target_scheme['source_url']}]({target_scheme['source_url']})"
        else:
            reply = "We have indexed schemes across Education, Agriculture, Housing, Disability Support, Skill Development, and Women Welfare. Select a scheme to see details!"

    else:
        # Default FIND_SCHOLARSHIP / general answer
        edu_schemes = [s for s in all_schemes if s["category"] == "Education"]
        s = target_scheme or (edu_schemes[0] if edu_schemes else all_schemes[0])
        reply = f"Based on your query, a top matching scheme is **{s['name']}**.\n\n{s['simplified_description']}\n\n🔗 Official Source: [{s['source_url']}]({s['source_url']})"

    return {
        "user_message": user_msg,
        "intent_detected": intent,
        "grounded_response": reply,
        "source_scheme": target_scheme["name"] if target_scheme else "Knowledge Base"
    }
