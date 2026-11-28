import os
import shutil
import subprocess
import tempfile
from pathlib import Path
from typing import Dict, Any, Optional, Tuple
import numpy as np
from PIL import Image

# Compatibility shim for EasyOCR on NumPy 2.x
if not hasattr(np, "float_"):
    np.float_ = np.float64

try:
    import pdfplumber
except ImportError:
    pdfplumber = None

try:
    import pypdf
except ImportError:
    pypdf = None

try:
    import pypdfium2 as pdfium
except ImportError:
    pdfium = None

try:
    import pytesseract
except ImportError:
    pytesseract = None

try:
    import easyocr
except ImportError:
    easyocr = None


_easyocr_reader = None
MAX_PDF_OCR_PAGES = 5


def _find_tesseract_cmd() -> Optional[str]:
    """Locate tesseract binary if installed on the system."""
    cmd = shutil.which("tesseract")
    if cmd:
        return cmd
    for candidate in (
        r"C:\Program Files\Tesseract-OCR\tesseract.exe",
        r"C:\Program Files (x86)\Tesseract-OCR\tesseract.exe",
    ):
        if os.path.exists(candidate):
            return candidate
    return None


def _get_easyocr_reader():
    """Lazily initialize and cache the EasyOCR English reader."""
    global _easyocr_reader
    if _easyocr_reader is None and easyocr is not None:
        _easyocr_reader = easyocr.Reader(["en"], gpu=False, verbose=False)
    return _easyocr_reader


def _windows_ocr_image(img: Image.Image) -> str:
    """Fallback OCR using built-in Windows.Media.Ocr on Windows 10/11."""
    if os.name != "nt":
        return ""
    ps_file = Path(__file__).resolve().parent / "win_ocr.ps1"
    if not ps_file.exists():
        return ""
    tmp_path = None
    try:
        with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp:
            tmp_path = tmp.name
        img.convert("RGB").save(tmp_path, format="PNG")
        proc = subprocess.run(
            [
                "powershell",
                "-NoProfile",
                "-ExecutionPolicy",
                "Bypass",
                "-File",
                str(ps_file),
                tmp_path,
            ],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="ignore",
            timeout=25,
        )
        if proc.returncode == 0 and proc.stdout:
            return proc.stdout.strip()
    except Exception:
        return ""
    finally:
        if tmp_path and os.path.exists(tmp_path):
            try:
                os.remove(tmp_path)
            except OSError:
                pass
    return ""


def _ocr_pil_image(img: Image.Image) -> Tuple[str, str, Optional[str]]:
    """
    Run OCR on a PIL Image using EasyOCR, pytesseract (if binary installed),
    or Windows built-in OCR fallback.
    Returns (extracted_text, method_used, error_message).
    """
    errors = []
    rgb_img = img.convert("RGB")

    # 1. Try EasyOCR (pure Python + PyTorch, works cleanly for scanned certificates)
    if easyocr is not None:
        try:
            reader = _get_easyocr_reader()
            if reader is not None:
                lines = reader.readtext(np.array(rgb_img), detail=0)
                text = "\n".join(str(line).strip() for line in lines if str(line).strip())
                if text.strip():
                    return text.strip(), "easyocr", None
        except Exception as e:
            errors.append(f"easyocr: {e}")

    # 2. Try pytesseract if Tesseract binary is installed
    tesseract_cmd = _find_tesseract_cmd()
    if pytesseract is not None and tesseract_cmd:
        try:
            pytesseract.pytesseract.tesseract_cmd = tesseract_cmd
            text = pytesseract.image_to_string(rgb_img).strip()
            if text:
                return text, "pytesseract", None
        except Exception as e:
            errors.append(f"pytesseract: {e}")

    # 3. Try Windows built-in OCR fallback
    win_text = _windows_ocr_image(rgb_img)
    if win_text:
        return win_text, "windows_ocr", None

    err_msg = "; ".join(errors) if errors else "No OCR engine could extract text from the image."
    return "", "ocr_failed", err_msg


def extract_text_from_file(file_path: Path) -> Dict[str, Any]:
    """
    OCR & Text Extraction Service.
    Extracts raw text from PDF (text-layer or scanned), Image, or Text files.
    Preserves original file path and extracted text separately.
    """
    ext = file_path.suffix.lower()
    extracted_text = ""
    method_used = "direct_read"
    ocr_error: Optional[str] = None

    if not file_path.exists():
        return {"error": "File not found", "extracted_text": "", "ocr_method": "none"}

    if ext == ".txt":
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            extracted_text = f.read()
        method_used = "text_file_reader"

    elif ext == ".pdf":
        # Step 1: Try embedded text layer via pdfplumber
        if pdfplumber:
            try:
                with pdfplumber.open(file_path) as pdf:
                    pages_text = [page.extract_text() or "" for page in pdf.pages]
                    extracted_text = "\n".join(pages_text).strip()
                if extracted_text:
                    method_used = "pdfplumber"
            except Exception:
                extracted_text = ""

        # Step 2: Fallback to pypdf text layer
        if len(extracted_text) < 20 and pypdf:
            try:
                reader = pypdf.PdfReader(file_path)
                pages_text = [page.extract_text() or "" for page in reader.pages]
                pypdf_text = "\n".join(pages_text).strip()
                if len(pypdf_text) > len(extracted_text):
                    extracted_text = pypdf_text
                    method_used = "pypdf"
            except Exception:
                pass

        # Step 3: Scanned / image-based PDF fallback via pypdfium2 + OCR
        if len(extracted_text) < 20 and pdfium is not None:
            pdf = None
            try:
                pdf = pdfium.PdfDocument(str(file_path))
                page_count = min(len(pdf), MAX_PDF_OCR_PAGES)
                ocr_pages = []
                img_method = "ocr"
                for i in range(page_count):
                    page = pdf[i]
                    bitmap = page.render(scale=250 / 72)
                    pil_img = bitmap.to_pil()
                    page_text, used_method, err = _ocr_pil_image(pil_img)
                    if page_text:
                        ocr_pages.append(page_text)
                        img_method = used_method
                    elif err:
                        ocr_error = err
                if ocr_pages:
                    extracted_text = "\n\n".join(ocr_pages).strip()
                    method_used = f"pypdfium2+{img_method}"
                else:
                    method_used = "pypdfium2+ocr_empty"
            except Exception as e:
                ocr_error = str(e)
            finally:
                if pdf is not None:
                    try:
                        pdf.close()
                    except Exception:
                        pass

    elif ext in [".png", ".jpg", ".jpeg", ".webp", ".bmp", ".tiff"]:
        try:
            with Image.open(file_path) as img:
                extracted_text, method_used, ocr_error = _ocr_pil_image(img)
        except Exception as e:
            extracted_text = ""
            method_used = "image_error"
            ocr_error = str(e)

    result: Dict[str, Any] = {
        "file_name": file_path.name,
        "file_path": str(file_path),
        "file_type": ext,
        "extracted_text": extracted_text.strip(),
        "ocr_method": method_used,
    }
    if ocr_error and not result["extracted_text"]:
        result["ocr_error"] = ocr_error
    return result
