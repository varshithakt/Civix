from typing import Any, Dict
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from database.db import db_repo
from api.profile import ACTIVE_USER_PROFILE
from api.documents import STORED_DOCUMENTS
from .templates import SCHEME_TEMPLATES, COMMON_FIELDS

router = APIRouter(prefix="/api/autofill", tags=["Form Auto-Fill"])


class PreviewRequest(BaseModel):
    scheme_id: str = Field(..., min_length=1)
    edited_profile: Dict[str, Any] = Field(default_factory=dict)


def is_missing(value: Any) -> bool:
    if value is None:
        return True
    if isinstance(value, str):
        return value.strip().lower() in {"", "unknown", "none", "null", "n/a", "not provided"}
    return False


def build_profile() -> Dict[str, Any]:
    profile = dict(ACTIVE_USER_PROFILE)

    # Document extraction is also consulted as a fallback. Do not overwrite
    # a non-empty value already present in the user's saved profile.
    for document in STORED_DOCUMENTS:
        extracted = document.get("extracted_profile") or {}
        for key, value in extracted.items():
            if key in profile and is_missing(profile.get(key)) and not is_missing(value):
                profile[key] = value

    return profile


@router.get("/health")
def autofill_health():
    return {"status": "ready", "module": "Civix Form Auto-Fill"}


@router.post("/preview")
def create_form_preview(request: PreviewRequest):
    scheme = db_repo.get_by_id(request.scheme_id)
    if not scheme:
        raise HTTPException(status_code=404, detail="Scheme not found")

    profile = build_profile()

    # Only accept known profile attributes from the browser. These are
    # temporary preview edits and do not silently update the saved profile.
    for key, value in request.edited_profile.items():
        if key in profile:
            profile[key] = value

    template = SCHEME_TEMPLATES.get(request.scheme_id, COMMON_FIELDS)
    fields = []

    for definition in template:
        key = definition["profile_key"]
        value = profile.get(key)
        missing = is_missing(value)

        if key == "name" and str(value).strip().lower() == "applicant":
            missing = True
            value = ""

        fields.append({
            "field_id": definition["field_id"],
            "label": definition["label"],
            "profile_key": key,
            "value": "" if missing else str(value),
            "required": definition["required"],
            "status": "missing" if missing else "available",
            "source": "User profile / uploaded document" if not missing else "Not found in profile"
        })

    completed = sum(1 for item in fields if not is_missing(item["value"]))
    required_missing = sum(
        1 for item in fields
        if item["required"] and is_missing(item["value"])
    )

    return {
        "scheme_id": scheme["id"],
        "scheme_name": scheme["name"],
        "category": scheme.get("category", ""),
        "official_url": scheme.get("source_url", ""),
        "fields": fields,
        "total_fields": len(fields),
        "completed_fields": completed,
        "required_missing": required_missing,
        "completion_percentage": round(completed * 100 / len(fields)) if fields else 0,
        "disclaimer": (
            "This is a Civix-generated prefilled information preview, not an official "
            "government application form. Verify all details and complete submission "
            "only through the official government portal."
        )
    }
