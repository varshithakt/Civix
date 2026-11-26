import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "backend"))

from eligibility.rules import evaluate_eligibility

def test_eligibility_matching_success():
    profile = {
        "age": 20,
        "annual_income": 180000,
        "education": "engineering",
        "state": "Karnataka",
        "category": "General",
        "gender": "Male"
    }
    scheme = {
        "id": "SCH001",
        "name": "Post-Matric Scholarship",
        "eligibility": {
            "min_age": 16,
            "max_age": 25,
            "income_limit": 250000,
            "education": ["undergraduate", "engineering"],
            "states": ["All"],
            "categories": ["All"]
        }
    }

    res = evaluate_eligibility(profile, scheme)
    assert res["overall_status"] == "potentially_eligible"
    assert res["breakdown"]["age"]["status"] == "matched"
    assert res["breakdown"]["income"]["status"] == "matched"


def test_eligibility_matching_failure():
    profile = {
        "age": 30, # Exceeds max age 25
        "annual_income": 400000, # Exceeds income 2.5L
        "education": "engineering",
        "state": "Karnataka"
    }
    scheme = {
        "id": "SCH001",
        "name": "Post-Matric Scholarship",
        "eligibility": {
            "min_age": 16,
            "max_age": 25,
            "income_limit": 250000,
            "education": ["undergraduate", "engineering"],
            "states": ["All"]
        }
    }

    res = evaluate_eligibility(profile, scheme)
    assert res["overall_status"] == "ineligible"
    assert res["breakdown"]["age"]["status"] == "unmatched"
    assert res["breakdown"]["income"]["status"] == "unmatched"
