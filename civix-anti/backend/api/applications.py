import uuid
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from database.db import db_repo, app_repo
from eligibility.rules import evaluate_eligibility
from eligibility.matcher import detect_missing_documents
from eligibility.contradiction import detect_profile_contradictions
from api.documents import STORED_DOCUMENTS

router = APIRouter(prefix="/api/applications", tags=["Applications"])

PROGRESS_STAGES = [
    ("Draft Saved", "Application form fields saved for review."),
    ("Submitted", "Applicant confirmed extracted details and submitted application."),
    ("Document Verification", "Uploaded certificates checked against scheme requirements."),
    ("Eligibility Review", "Deterministic profile criteria verified against scheme rules."),
    ("Ready / Forwarded", "Application package verified and ready for official portal sync."),
]


def _now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")


def _build_timeline(completed_step: int, existing_timeline: Optional[List[Dict[str, Any]]] = None, notes: Optional[Dict[int, str]] = None) -> List[Dict[str, Any]]:
    notes = notes or {}
    existing_by_step = {item["step"]: item for item in (existing_timeline or [])}
    timeline = []
    now = _now_iso()

    for idx, (label, default_note) in enumerate(PROGRESS_STAGES, start=1):
        prev = existing_by_step.get(idx, {})
        if idx <= completed_step:
            status = "completed"
            timestamp = prev.get("timestamp") or now
        elif idx == completed_step + 1:
            status = "in_progress"
            timestamp = prev.get("timestamp")
        else:
            status = "pending"
            timestamp = None

        timeline.append({
            "step": idx,
            "label": label,
            "status": status,
            "timestamp": timestamp,
            "note": notes.get(idx) or prev.get("note") or default_note,
        })
    return timeline


class ApplyRequest(BaseModel):
    scheme_id: str
    form_fields: List[Dict[str, Any]]
    profile: Optional[Dict[str, Any]] = None
    save_as_draft: bool = False
    user_confirmed: bool = False
    application_id: Optional[str] = None


@router.get("/")
def list_applications():
    apps = app_repo.list_all()
    return {
        "total": len(apps),
        "applications": apps,
    }


@router.get("/{app_id}")
def get_application(app_id: str):
    record = app_repo.get_by_id(app_id)
    if not record:
        raise HTTPException(status_code=404, detail="Application not found")
    return {"application": record}


@router.post("/apply")
def submit_or_save_application(req: ApplyRequest):
    scheme = db_repo.get_by_id(req.scheme_id)
    if not scheme:
        raise HTTPException(status_code=404, detail="Scheme not found")

    if not scheme.get("direct_apply", False):
        raise HTTPException(
            status_code=400,
            detail=f"Direct in-app application is not enabled for {scheme['name']}. Please apply via {scheme['source_url']}."
        )

    if not req.save_as_draft and not req.user_confirmed:
        raise HTTPException(
            status_code=400,
            detail="You must review and confirm your application details before submitting."
        )

    # Extract form values as dict
    form_data = {f["field_id"]: f.get("value", "") for f in req.form_fields}
    applicant_name = str(form_data.get("full_name") or (req.profile or {}).get("name") or "Applicant").strip()

    # Run deterministic eligibility & document checks
    profile = req.profile or {}
    rule_eval = evaluate_eligibility(profile, scheme)
    doc_check = detect_missing_documents(scheme.get("required_documents", []), STORED_DOCUMENTS)
    contradictions = detect_profile_contradictions(STORED_DOCUMENTS)

    if req.save_as_draft:
        current_step = 1
        status_label = "Draft Saved"
        stage_notes = {1: "Draft saved. Confirm details and click Submit when ready."}
    else:
        current_step = 2
        status_label = "Submitted"
        stage_notes = {
            2: "Submitted after applicant review and confirmation.",
            3: (
                "All required documents attached with no contradictions."
                if doc_check["missing_count"] == 0 and len(contradictions) == 0
                else f"Missing {doc_check['missing_count']} document(s) or pending verification."
            ),
        }
        # Auto-advance verification steps when requirements are already satisfied
        if doc_check["missing_count"] == 0 and len(contradictions) == 0:
            current_step = 3
            status_label = "Document Verification"
            if rule_eval["overall_status"] == "potentially_eligible":
                current_step = 4
                status_label = "Eligibility Review"
                stage_notes[4] = "Deterministic rules matched profile criteria."

    progress_pct = current_step * 20
    now = _now_iso()

    existing = app_repo.get_by_id(req.application_id) if req.application_id else None
    app_id = existing["id"] if existing else f"APP-2026-{str(uuid.uuid4())[:6].upper()}"
    created_at = existing["created_at"] if existing else now

    timeline = _build_timeline(current_step, existing.get("timeline") if existing else None, stage_notes)

    record = {
        "id": app_id,
        "scheme_id": scheme["id"],
        "scheme_name": scheme["name"],
        "category": scheme["category"],
        "source_url": scheme["source_url"],
        "applicant_name": applicant_name,
        "status": status_label,
        "current_step": current_step,
        "progress_pct": progress_pct,
        "eligibility_status": rule_eval["overall_status"],
        "user_confirmed": req.user_confirmed,
        "form_data": {
            "fields": req.form_fields,
            "values": form_data,
        },
        "documents": {
            "uploaded": [
                {"file_name": d["file_name"], "document_type": d["document_type"], "confidence": d["confidence"]}
                for d in STORED_DOCUMENTS
            ],
            "matched_count": doc_check["provided_count"],
            "missing_documents": [d["name"] for d in doc_check["missing_documents"]],
            "contradictions_count": len(contradictions),
        },
        "timeline": timeline,
        "created_at": created_at,
        "updated_at": now,
    }

    app_repo.save(record)
    return {
        "message": "Draft saved successfully" if req.save_as_draft else "Application submitted and saved successfully",
        "application": record,
    }


@router.post("/{app_id}/advance")
def advance_application_progress(app_id: str):
    """Advances an application to the next verification/progress stage."""
    record = app_repo.get_by_id(app_id)
    if not record:
        raise HTTPException(status_code=404, detail="Application not found")

    if not record["user_confirmed"] and record["current_step"] == 1:
        raise HTTPException(
            status_code=400,
            detail="Draft applications must be confirmed and submitted from the Application Form before advancing."
        )

    next_step = min(5, record["current_step"] + 1)
    if next_step == record["current_step"]:
        return {"message": "Application has already reached final ready stage.", "application": record}

    status_label = PROGRESS_STAGES[next_step - 1][0]
    record["current_step"] = next_step
    record["progress_pct"] = next_step * 20
    record["status"] = status_label
    record["updated_at"] = _now_iso()
    record["timeline"] = _build_timeline(next_step, record["timeline"])

    app_repo.save(record)
    return {
        "message": f"Application progress updated to: {status_label}",
        "application": record,
    }


@router.delete("/{app_id}")
def delete_application(app_id: str):
    deleted = app_repo.delete(app_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Application not found")
    return {"message": "Application withdrawn and removed", "id": app_id}
