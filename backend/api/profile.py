from typing import Dict, Any, Optional
from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter(prefix="/api/profile", tags=["User Profile"])

# In-memory user active profile state
ACTIVE_USER_PROFILE: Dict[str, Any] = {
    "name": "Applicant",
    "age": "unknown",
    "annual_income": "unknown",
    "income_type": "unknown",
    "education": "unknown",
    "state": "unknown",
    "district": "unknown",
    "occupation": "unknown",
    "category": "unknown",
    "gender": "unknown",
    "disability_pct": "unknown"
}

class ProfileUpdateRequest(BaseModel):
    name: Optional[str] = "Applicant"
    age: Optional[Any] = "unknown"
    annual_income: Optional[Any] = "unknown"
    income_type: Optional[str] = "unknown"
    education: Optional[str] = "unknown"
    state: Optional[str] = "unknown"
    district: Optional[str] = "unknown"
    occupation: Optional[str] = "unknown"
    category: Optional[str] = "unknown"
    gender: Optional[str] = "unknown"
    disability_pct: Optional[Any] = "unknown"

class AutofillRequest(BaseModel):
    scheme_id: str
    profile: Dict[str, Any]

@router.get("/")
def get_current_profile():
    return {"profile": ACTIVE_USER_PROFILE}


@router.post("/update")
def update_profile(req: ProfileUpdateRequest):
    global ACTIVE_USER_PROFILE
    updated = req.dict()
    for key, val in updated.items():
        if val is not None:
            ACTIVE_USER_PROFILE[key] = val
            
    return {
        "message": "User profile updated successfully",
        "profile": ACTIVE_USER_PROFILE
    }


@router.post("/autofill-preview")
def generate_autofill_form(req: AutofillRequest):
    """
    Form Auto-Fill module:
    Maps confirmed user profile into standardized application fields for user review & confirmation.
    IMPORTANT: Never automatically submits applications.
    """
    p = req.profile
    form_fields = [
        {"field_id": "full_name", "label": "Full Name", "value": p.get("name", "Applicant"), "status": "confirmed"},
        {"field_id": "age", "label": "Age", "value": str(p.get("age", "")), "status": "extracted" if p.get("age") != "unknown" else "missing"},
        {"field_id": "annual_income", "label": "Annual Household Income (₹)", "value": f"₹{p.get('annual_income'):,}" if isinstance(p.get("annual_income"), (int, float)) else str(p.get("annual_income")), "status": "extracted" if p.get("annual_income") != "unknown" else "missing"},
        {"field_id": "education_level", "label": "Educational Qualification", "value": str(p.get("education", "")).title(), "status": "extracted" if p.get("education") != "unknown" else "missing"},
        {"field_id": "state_domicile", "label": "State of Residence", "value": str(p.get("state", "")).title(), "status": "extracted" if p.get("state") != "unknown" else "missing"},
        {"field_id": "district", "label": "District", "value": str(p.get("district", "")).title(), "status": "extracted" if p.get("district") != "unknown" else "missing"},
        {"field_id": "caste_category", "label": "Social Category", "value": str(p.get("category", "")), "status": "extracted" if p.get("category") != "unknown" else "missing"},
        {"field_id": "gender", "label": "Gender", "value": str(p.get("gender", "")), "status": "extracted" if p.get("gender") != "unknown" else "missing"}
    ]

    return {
        "scheme_id": req.scheme_id,
        "form_fields": form_fields,
        "disclaimer": "This is a pre-filled preview generated from your confirmed profile. Please verify all details before official submission on the official portal."
    }
