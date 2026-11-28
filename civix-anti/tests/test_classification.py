import sys
from pathlib import Path
from PIL import Image, ImageDraw

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "backend"))

from nlp.classification import classify_document
from ocr.ocr_service import extract_text_from_file


def test_classify_income_and_caste_document():
    text = (
        "Government of Karnataka Revenue Department\n"
        "Income and Caste Certificate\n"
        "Certified that Annual Family Income is Rs. 1,20,000.\n"
        "Belongs to Category 2A OBC. Issued by Tahsildar, Bengaluru."
    )
    res = classify_document(text)
    assert res["document_type"] in ("Income Certificate", "Caste Certificate")
    assert res["confidence"] >= 70


def test_classify_marks_card():
    text = (
        "Karnataka Secondary Education Examination Board\n"
        "SSLC Statement of Marks\n"
        "Register Number: 20220451234\n"
        "Total Marks Obtained: 540 / 625 Percentage: 86.4% Result: PASSED"
    )
    res = classify_document(text)
    assert res["document_type"] == "Marks Card"
    assert res["confidence"] >= 70


def test_classify_bonafide_college_document():
    text = (
        "AICTE Pragati Scholarship Renewal\n"
        "Bonafide Certificate\n"
        "This is to certify that the student is pursuing B.E Engineering in Semester 5."
    )
    res = classify_document(text)
    assert res["document_type"] == "College ID"
    assert res["confidence"] >= 70


def test_ocr_on_generated_image(tmp_path):
    img_path = tmp_path / "sample_income.png"
    img = Image.new("RGB", (900, 300), color="white")
    draw = ImageDraw.Draw(img)
    draw.text((40, 60), "GOVERNMENT OF KARNATAKA", fill="black")
    draw.text((40, 120), "INCOME CERTIFICATE", fill="black")
    draw.text((40, 180), "Annual Family Income Rs 150000", fill="black")
    img.save(img_path)

    res = extract_text_from_file(img_path)
    assert res["ocr_method"] != "pillow_fallback"
    assert "extracted_text" in res
