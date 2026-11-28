import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "backend"))

from nlp.normalization import normalize_income, normalize_state, normalize_education
from nlp.extraction import extract_user_profile

def test_income_normalization_lakh():
    val, inc_type = normalize_income("family income is around 1.8 lakh per year")
    assert val == 180000.0
    assert inc_type == "family"

def test_income_normalization_monthly():
    val, inc_type = normalize_income("earns about 15000 per month")
    assert val == 180000.0
    assert inc_type == "individual"

def test_income_normalization_rupees():
    val, inc_type = normalize_income("annual income Rs. 1,50,000")
    assert val == 150000.0

def test_state_normalization():
    assert normalize_state("residing in Bengaluru, Karnataka") == "Karnataka"
    assert normalize_state("living in Mumbai") == "Maharashtra"

def test_education_normalization():
    assert normalize_education("engineering student") == "engineering"
    assert normalize_education("pursuing B.Tech degree") == "engineering"
    assert normalize_education("10th standard school student") == "school"

def test_full_profile_extraction():
    text = "The applicant is a 21-year-old engineering student residing in Bengaluru, Karnataka. The annual family income is Rs. 1.8 lakh."
    prof = extract_user_profile(text)
    assert prof["age"] == 21
    assert prof["annual_income"] == 180000
    assert prof["education"] == "engineering"
    assert prof["state"] == "Karnataka"


def test_no_false_positives_on_marksheet_numbers():
    text = "Board of Secondary Education Marks Card Year 2022 Pin 560001 Student School Result Passed"
    prof = extract_user_profile(text)
    assert prof["annual_income"] == "unknown"
    assert prof["category"] == "unknown"
    assert prof["education"] == "school"
    assert prof["state"] == "unknown"
