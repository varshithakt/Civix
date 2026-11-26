import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "backend"))

from eligibility.contradiction import detect_profile_contradictions

def test_contradiction_detection():
    docs = [
        {
            "file_name": "Income_Cert_1.pdf",
            "extracted_profile": {"annual_income": 150000, "age": 20, "state": "Karnataka"}
        },
        {
            "file_name": "Income_Cert_2.pdf",
            "extracted_profile": {"annual_income": 250000, "age": 20, "state": "Karnataka"}
        }
    ]

    alerts = detect_profile_contradictions(docs)
    assert len(alerts) > 0
    assert alerts[0]["field"] == "annual_income"
    assert "Inconsistency found" in alerts[0]["description"]
