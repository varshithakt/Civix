"""
Scheme Assistant Chatbot API
-----------------------------
Gives contextually accurate, query-specific answers by combining:
  1. Rule-based intent detection (expanded to 9 intents)
  2. Semantic TF-IDF scheme retrieval (embedding_engine)
  3. Profile-aware eligibility evaluation (evaluate_eligibility)
  4. Exact scheme-name / scheme-ID mention detection
  5. Dynamic response generation per intent + per scheme
"""

from typing import Dict, Any, Optional, List
from fastapi import APIRouter
from pydantic import BaseModel

from database.db import db_repo
from nlp.intent import intent_classifier
from nlp.embeddings import embedding_engine
from nlp.explanation import simplify_scheme_language
from eligibility.rules import evaluate_eligibility

router = APIRouter(prefix="/api/chat", tags=["Scheme Chatbot"])


# ---------------------------------------------------------------------------
# Request model
# ---------------------------------------------------------------------------

class ChatMessage(BaseModel):
    message: str
    user_profile: Optional[Dict[str, Any]] = None
    selected_scheme_id: Optional[str] = None


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

CATEGORY_KEYWORDS: Dict[str, List[str]] = {
    "Education":    ["scholarship", "scholarships", "study", "student", "college",
                     "university", "tuition", "post matric", "nmms", "engineering",
                     "degree", "school", "marks", "merit", "academic"],
    "Agriculture":  ["farmer", "farm", "farming", "crop", "kisan", "land",
                     "irrigation", "agriculture", "agricultural", "landholding"],
    "Housing":      ["house", "home", "housing", "awas", "pucca", "flat",
                     "construction", "shelter", "accommodation"],
    "Disability":   ["disability", "disabled", "handicap", "udid", "ddrs",
                     "specially abled", "rehabilitation", "assistive"],
    "Business":     ["business", "loan", "mudra", "startup", "enterprise",
                     "entrepreneur", "shop", "trade", "micro loan", "self employed",
                     "artisan", "small business"],
    "Women Welfare":["women", "woman", "female", "gruha lakshmi", "mother",
                     "widow", "girl", "gender"],
    "Skill":        ["skill", "training", "vocational", "apprentice", "pmkvy",
                     "trade training", "certificate course"],
}


def _ensure_indexed(all_schemes: List[Dict]) -> None:
    """Index schemes in embedding engine if not already done."""
    if not embedding_engine._is_indexed:
        embedding_engine.index_schemes(all_schemes)


def _detect_target_scheme(
    user_msg: str,
    selected_scheme_id: Optional[str],
    all_schemes: List[Dict]
) -> Optional[Dict]:
    """
    Returns the best single scheme that the user is asking about, in priority order:
      1. Explicit selected_scheme_id from UI
      2. Scheme ID mentioned in message  (e.g. "SCH003")
      3. Scheme name substring in message (case-insensitive, longest match first)
      4. Semantic top-1 scheme (only if similarity >= 0.15 to avoid false matches)
    """
    lowered = user_msg.lower()

    # 1. UI-selected scheme
    if selected_scheme_id:
        s = db_repo.get_by_id(selected_scheme_id)
        if s:
            return s

    # 2. Scheme ID in message
    for s in all_schemes:
        if s["id"].lower() in lowered:
            return s

    # 3. Scheme name substring – longest match first to prefer specific over generic
    matched = [(s, len(s["name"])) for s in all_schemes
               if s["name"].lower() in lowered]
    if matched:
        matched.sort(key=lambda x: x[1], reverse=True)
        return matched[0][0]

    # 4. Semantic top-1 (only for strong signals)
    sim_scores = embedding_engine.calculate_similarity(user_msg)
    if sim_scores:
        best_id = max(sim_scores, key=sim_scores.get)
        if sim_scores[best_id] >= 0.15:
            return db_repo.get_by_id(best_id)

    return None


def _get_category_from_query(user_msg: str) -> Optional[str]:
    """Detect which scheme category the user is asking about from keywords."""
    lowered = user_msg.lower()
    scores: Dict[str, int] = {}
    for cat, kws in CATEGORY_KEYWORDS.items():
        hit = sum(1 for kw in kws if kw in lowered)
        if hit:
            scores[cat] = hit
    if scores:
        return max(scores, key=scores.get)
    return None


def _get_schemes_by_category(category: str, all_schemes: List[Dict]) -> List[Dict]:
    return [s for s in all_schemes if s.get("category") == category]


def _get_ranked_schemes(
    user_msg: str, profile: Dict, all_schemes: List[Dict], top_n: int = 3
) -> List[Dict]:
    """
    Returns top_n schemes ranked by semantic similarity + profile pre-filter.
    If the profile has a state restriction, state-specific schemes are preferred.
    """
    sim_scores = embedding_engine.calculate_similarity(user_msg)
    if not sim_scores:
        return all_schemes[:top_n]

    # Build a preference boost for state-matching schemes
    user_state = str(profile.get("state", "")).lower()

    def rank_key(s: Dict) -> float:
        score = sim_scores.get(s["id"], 0.0)
        states = [st.lower() for st in s.get("eligibility", {}).get("states", [])]
        if user_state and "all" not in states and user_state in states:
            score += 0.08  # small boost for state-specific match
        return score

    ranked = sorted(all_schemes, key=rank_key, reverse=True)
    return ranked[:top_n]


def _eligibility_summary_text(result: Dict) -> str:
    """Convert evaluate_eligibility() result to a readable multi-line string."""
    lines = []
    icons = {"matched": "✅", "unmatched": "❌", "unknown": "❓"}
    for criterion, detail in result.get("breakdown", {}).items():
        icon = icons.get(detail["status"], "•")
        val = detail.get("user_value")
        req = detail.get("requirement", "")
        if val is not None:
            lines.append(f"{icon} **{criterion.capitalize()}**: Your value `{val}` — Requirement: {req}")
        else:
            lines.append(f"{icon} **{criterion.capitalize()}**: Not provided — Requirement: {req}")
    return "\n".join(lines)


def _format_income(val) -> str:
    try:
        v = float(val)
        if v >= 100000:
            return f"₹{v/100000:.1f} lakh (₹{v:,.0f}/yr)"
        return f"₹{v:,.0f}/yr"
    except Exception:
        return str(val)


# ---------------------------------------------------------------------------
# Intent handlers
# ---------------------------------------------------------------------------

def _handle_find_scheme(
    user_msg: str, profile: Dict, all_schemes: List[Dict],
    category: Optional[str]
) -> str:
    """
    For FIND_SCHOLARSHIP, FIND_AGRICULTURE_SCHEME, FIND_HOUSING_SCHEME,
    FIND_DISABILITY_SCHEME, FIND_BUSINESS_SCHEME, FIND_WOMEN_SCHEME, general FIND.
    Returns contextual scheme recommendations.
    """
    # Narrow by detected category
    if category:
        pool = _get_schemes_by_category(category, all_schemes) or all_schemes
    else:
        pool = all_schemes

    # Rank by semantic similarity + profile state
    top_schemes = _get_ranked_schemes(user_msg, profile, pool, top_n=3)
    if not top_schemes:
        return "I couldn't find any schemes matching your query. Try describing your situation (age, state, occupation, income)."

    has_profile = any(profile.get(f) not in (None, "unknown", "")
                      for f in ["age", "annual_income", "state", "education"])

    # Build profile context line
    profile_ctx = ""
    if has_profile:
        parts = []
        if profile.get("age") not in (None, "unknown"):
            parts.append(f"Age {profile['age']}")
        if profile.get("state") not in (None, "unknown"):
            parts.append(f"State: {profile['state']}")
        if profile.get("education") not in (None, "unknown"):
            parts.append(f"Education: {profile['education']}")
        if profile.get("annual_income") not in (None, "unknown"):
            parts.append(f"Income: {_format_income(profile['annual_income'])}")
        profile_ctx = "*(Based on your profile: " + ", ".join(parts) + ")*\n\n"

    lines = [f"Here are the most relevant schemes for your query:\n\n{profile_ctx}"]

    for idx, s in enumerate(top_schemes, 1):
        # Quick eligibility check if profile is available
        eligibility_note = ""
        if has_profile:
            result = evaluate_eligibility(profile, s)
            status = result.get("overall_status", "")
            if status == "potentially_eligible":
                eligibility_note = " — ✅ *Potentially eligible based on your profile*"
            elif status == "ineligible":
                eligibility_note = " — ❌ *May not meet all criteria for your profile*"
            else:
                eligibility_note = " — ❓ *Partial match – some info needed*"

        lines.append(
            f"**{idx}. {s['name']}** ({s['category']}){eligibility_note}\n"
            f"{s.get('simplified_description', s.get('description', ''))}\n"
            f"💰 Benefits: {s.get('benefits', 'See official site')}\n"
            f"🔗 [Official Source]({s['source_url']})\n"
        )

    lines.append("\n> ⚠️ *Eligibility shown here is indicative only. Official eligibility is determined by the government.*")
    return "\n".join(lines)


def _handle_get_documents(
    user_msg: str, profile: Dict, all_schemes: List[Dict],
    target_scheme: Optional[Dict], category: Optional[str]
) -> str:
    if target_scheme:
        docs = target_scheme.get("required_documents", [])
        doc_list = "\n".join([f"- {d['name']}" for d in docs])
        reply = (
            f"For **{target_scheme['name']}**, you will need the following documents:\n\n"
            f"{doc_list}\n\n"
            f"🔗 Official Source: [{target_scheme['source_url']}]({target_scheme['source_url']})"
        )
        return reply

    # Fallback: show docs for best semantically matched scheme(s)
    top_schemes = _get_ranked_schemes(user_msg, profile, all_schemes, top_n=2)
    if top_schemes:
        lines = ["Here are the required documents for the top matching schemes:\n"]
        for s in top_schemes:
            docs = s.get("required_documents", [])
            if docs:
                lines.append(f"**{s['name']}:**")
                lines.extend([f"  - {d['name']}" for d in docs])
                lines.append(f"  🔗 [{s['source_url']}]({s['source_url']})\n")
        return "\n".join(lines)

    return (
        "Common required documents for most government schemes include:\n"
        "- Income Certificate\n"
        "- Residence / Domicile Certificate\n"
        "- Aadhaar Card / Identity Proof\n"
        "- Academic Marks Card or College ID\n\n"
        "Please mention a specific scheme or describe your situation for exact requirements!"
    )


def _handle_explain_eligibility(
    user_msg: str, profile: Dict, all_schemes: List[Dict],
    target_scheme: Optional[Dict]
) -> str:
    has_profile = any(profile.get(f) not in (None, "unknown", "")
                      for f in ["age", "annual_income", "state", "education"])

    if not has_profile:
        return (
            "I need your profile information to explain eligibility.\n\n"
            "Please either:\n"
            "1. Enter a natural-language query like *'I am a 22-year-old student from Karnataka with ₹1.8 lakh income'*, OR\n"
            "2. Upload your documents on the **Document Upload** page so I can extract your profile automatically."
        )

    scheme = target_scheme
    if not scheme:
        # Pick the best semantically matching scheme
        top = _get_ranked_schemes(user_msg, profile, all_schemes, top_n=1)
        scheme = top[0] if top else None

    if not scheme:
        return "Please specify a scheme name or ID so I can explain your eligibility for it."

    result = evaluate_eligibility(profile, scheme)
    summary = _eligibility_summary_text(result)
    overall = result.get("overall_status", "")
    status_line = {
        "potentially_eligible": "✅ **Potentially eligible** based on the information provided.",
        "ineligible":           "❌ **Does not meet** one or more eligibility criteria.",
        "potential_match_with_unknowns": "❓ **Partial match** — some information is missing for a definitive assessment.",
    }.get(overall, "Assessment incomplete.")

    reply = (
        f"**Eligibility breakdown for {scheme['name']}:**\n\n"
        f"{summary}\n\n"
        f"**Overall**: {status_line}\n\n"
        f"> ⚠️ *This is indicative only. Official eligibility is determined by the government.*\n\n"
        f"🔗 Official Source: [{scheme['source_url']}]({scheme['source_url']})"
    )
    return reply


def _handle_scheme_information(
    user_msg: str, all_schemes: List[Dict],
    target_scheme: Optional[Dict]
) -> str:
    if target_scheme:
        s = target_scheme
        simplified = simplify_scheme_language(s)
        return (
            f"**{s['name']}** *(Category: {s['category']})*\n\n"
            f"{s.get('description', '')}\n\n"
            f"**In simple terms:** {simplified}\n\n"
            f"**Benefits:** {s.get('benefits', 'See official site')}\n\n"
            f"🔗 Official Link: [{s['source_url']}]({s['source_url']})"
        )

    # No specific scheme — list categories available
    categories = sorted(set(s["category"] for s in all_schemes))
    cat_list = ", ".join(categories)
    return (
        f"We have indexed schemes across the following categories: **{cat_list}**.\n\n"
        "You can ask things like:\n"
        "- *'Tell me about PM Kisan scheme'*\n"
        "- *'What is Gruha Lakshmi?'*\n"
        "- *'Show me disability support schemes'*\n\n"
        "Or select a scheme from the **Scheme Discovery** tab to see full details!"
    )


# ---------------------------------------------------------------------------
# Main endpoint
# ---------------------------------------------------------------------------

@router.post("/ask")
def answer_scheme_question(req: ChatMessage):
    user_msg = req.message.strip()
    if not user_msg:
        return {
            "user_message": "",
            "intent_detected": "UNKNOWN",
            "grounded_response": "Please type a question about government schemes.",
            "source_scheme": None,
        }

    profile = req.user_profile or {}
    all_schemes = db_repo.get_all()

    # Ensure embedding engine is indexed
    _ensure_indexed(all_schemes)

    # ---- Step 1: Detect intent ----
    intent_data = intent_classifier.classify(user_msg)
    intent = intent_data["intent"]

    # ---- Step 2: Detect category from query ----
    category = _get_category_from_query(user_msg)

    # ---- Step 3: Detect target scheme ----
    target_scheme = _detect_target_scheme(user_msg, req.selected_scheme_id, all_schemes)

    # ---- Step 4: Override intent from category when ML is uncertain ----
    # If ML confidence is low and we have a clear category signal, upgrade intent
    if intent_data.get("confidence", 0) < 0.5 and category:
        cat_to_intent = {
            "Agriculture":   "FIND_AGRICULTURE_SCHEME",
            "Housing":       "FIND_HOUSING_SCHEME",
            "Disability":    "FIND_DISABILITY_SCHEME",
            "Business":      "FIND_BUSINESS_SCHEME",
            "Women Welfare": "FIND_WOMEN_SCHEME",
            "Education":     "FIND_SCHOLARSHIP",
        }
        intent = cat_to_intent.get(category, intent)

    # ---- Step 5: Route to handler ----
    FIND_INTENTS = {
        "FIND_SCHOLARSHIP", "FIND_AGRICULTURE_SCHEME", "FIND_HOUSING_SCHEME",
        "FIND_DISABILITY_SCHEME", "FIND_BUSINESS_SCHEME", "FIND_WOMEN_SCHEME",
        "FIND_SCHEME",
    }

    if intent in FIND_INTENTS:
        reply = _handle_find_scheme(user_msg, profile, all_schemes, category)

    elif intent == "GET_REQUIRED_DOCUMENTS":
        reply = _handle_get_documents(user_msg, profile, all_schemes, target_scheme, category)

    elif intent == "EXPLAIN_ELIGIBILITY":
        reply = _handle_explain_eligibility(user_msg, profile, all_schemes, target_scheme)

    elif intent == "SCHEME_INFORMATION":
        reply = _handle_scheme_information(user_msg, all_schemes, target_scheme)

    else:
        # Catch-all: treat as a general find using semantic retrieval
        # Distinguish by looking at whether user asked about a specific scheme
        if target_scheme:
            reply = _handle_scheme_information(user_msg, all_schemes, target_scheme)
        else:
            reply = _handle_find_scheme(user_msg, profile, all_schemes, category)

    return {
        "user_message": user_msg,
        "intent_detected": intent,
        "grounded_response": reply,
        "source_scheme": target_scheme["name"] if target_scheme else (
            category + " category" if category else "Knowledge Base"
        ),
    }
