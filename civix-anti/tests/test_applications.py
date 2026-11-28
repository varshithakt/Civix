import sys
from pathlib import Path
from fastapi.testclient import TestClient

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "backend"))

from app import app
from database.db import db_repo, ApplicationRepository
import api.applications as apps_api

client = TestClient(app)


def test_five_direct_apply_schemes_configured():
    schemes = db_repo.get_all()
    direct_schemes = [s for s in schemes if s.get("direct_apply") is True]
    assert len(direct_schemes) == 5


def test_direct_apply_save_progress_and_delete(tmp_path, monkeypatch):
    temp_repo = ApplicationRepository(tmp_path / "test_apps.db")
    monkeypatch.setattr(apps_api, "app_repo", temp_repo)

    # 1. Reject direct apply for non-direct-apply scheme (SCH004)
    bad_scheme_resp = client.post(
        "/api/applications/apply",
        json={
            "scheme_id": "SCH004",
            "form_fields": [{"field_id": "full_name", "label": "Full Name", "value": "Asha"}],
            "save_as_draft": False,
            "user_confirmed": True,
        },
    )
    assert bad_scheme_resp.status_code == 400

    # 2. Reject direct submission without user_confirmed=True
    unconfirmed_resp = client.post(
        "/api/applications/apply",
        json={
            "scheme_id": "SCH001",
            "form_fields": [{"field_id": "full_name", "label": "Full Name", "value": "Asha"}],
            "save_as_draft": False,
            "user_confirmed": False,
        },
    )
    assert unconfirmed_resp.status_code == 400

    # 3. Save draft -> Step 1, 20%
    draft_resp = client.post(
        "/api/applications/apply",
        json={
            "scheme_id": "SCH001",
            "form_fields": [{"field_id": "full_name", "label": "Full Name", "value": "Asha"}],
            "profile": {"age": 20, "annual_income": 180000, "education": "engineering", "state": "Karnataka"},
            "save_as_draft": True,
            "user_confirmed": False,
        },
    )
    assert draft_resp.status_code == 200
    draft_app = draft_resp.json()["application"]
    assert draft_app["current_step"] == 1
    assert draft_app["progress_pct"] == 20
    assert draft_app["status"] == "Draft Saved"

    # 4. Submit confirmed application updating the draft -> Step >= 2, >= 40%
    submit_resp = client.post(
        "/api/applications/apply",
        json={
            "scheme_id": "SCH001",
            "application_id": draft_app["id"],
            "form_fields": [
                {"field_id": "full_name", "label": "Full Name", "value": "Asha"},
                {"field_id": "institution_name", "label": "College / Institution Name", "value": "RVCE"},
            ],
            "profile": {
                "age": 20,
                "annual_income": 180000,
                "education": "engineering",
                "state": "Karnataka",
                "category": "General",
                "gender": "Female",
            },
            "save_as_draft": False,
            "user_confirmed": True,
        },
    )
    assert submit_resp.status_code == 200
    submitted = submit_resp.json()["application"]
    assert submitted["id"] == draft_app["id"]
    assert submitted["current_step"] >= 2
    assert submitted["progress_pct"] >= 40
    assert submitted["user_confirmed"] is True

    # 5. List persisted applications
    list_resp = client.get("/api/applications/")
    assert list_resp.status_code == 200
    assert list_resp.json()["total"] == 1

    # 6. Advance progress to next stage
    adv_resp = client.post(f"/api/applications/{submitted['id']}/advance")
    assert adv_resp.status_code == 200
    advanced = adv_resp.json()["application"]
    assert advanced["current_step"] == submitted["current_step"] + 1
    assert advanced["progress_pct"] == advanced["current_step"] * 20

    # 7. Delete / withdraw application
    del_resp = client.delete(f"/api/applications/{submitted['id']}")
    assert del_resp.status_code == 200
    assert client.get("/api/applications/").json()["total"] == 0
