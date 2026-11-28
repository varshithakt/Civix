import shutil
import uuid
from pathlib import Path
from typing import List, Dict, Any
from fastapi import APIRouter, UploadFile, File, HTTPException
from config import UPLOADS_DIR, ALLOWED_EXTENSIONS
from ocr.ocr_service import extract_text_from_file
from nlp.classification import classify_document
from nlp.extraction import extract_user_profile
from eligibility.contradiction import detect_profile_contradictions

router = APIRouter(prefix="/api/documents", tags=["Documents"])

# In-memory document session storage (resets on restart)
STORED_DOCUMENTS: List[Dict[str, Any]] = []

@router.post("/upload")
async def upload_document(file: UploadFile = File(...)):
    ext = Path(file.filename).suffix.lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type. Allowed: {', '.join(ALLOWED_EXTENSIONS)}"
        )

    doc_id = str(uuid.uuid4())[:8]
    safe_filename = f"{doc_id}_{Path(file.filename).name}"
    file_path = UPLOADS_DIR / safe_filename

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # 1. OCR Text Extraction
    ocr_result = extract_text_from_file(file_path)
    raw_text = ocr_result.get("extracted_text", "")

    # 2. Document Type Classification
    classification = classify_document(raw_text)

    # 3. NLP Information Extraction from document text
    extracted_profile = extract_user_profile(raw_text)

    doc_record = {
        "id": doc_id,
        "file_name": file.filename,
        "saved_path": str(file_path),
        "document_type": classification["document_type"],
        "confidence": classification["confidence"],
        "matched_keywords": classification.get("matched_keywords", []),
        "secondary_types": classification.get("secondary_types", []),
        "ocr_method": ocr_result.get("ocr_method", "unknown"),
        "ocr_error": ocr_result.get("ocr_error"),
        "raw_text": raw_text,
        "extracted_profile": extracted_profile
    }

    STORED_DOCUMENTS.append(doc_record)

    # 4. Contradiction Detection across all uploaded documents
    contradictions = detect_profile_contradictions(STORED_DOCUMENTS)

    return {
        "message": "Document processed successfully",
        "document": doc_record,
        "total_documents": len(STORED_DOCUMENTS),
        "contradiction_alerts": contradictions
    }


@router.get("/")
def get_uploaded_documents():
    contradictions = detect_profile_contradictions(STORED_DOCUMENTS)
    return {
        "documents": STORED_DOCUMENTS,
        "contradiction_alerts": contradictions
    }


@router.delete("/clear")
def clear_uploaded_documents():
    global STORED_DOCUMENTS
    STORED_DOCUMENTS = []
    return {"message": "All uploaded documents cleared"}
