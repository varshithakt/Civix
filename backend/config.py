import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
UPLOADS_DIR = BASE_DIR / "uploads"
DB_DIR = BASE_DIR / "database"

# Ensure directories exist
DATA_DIR.mkdir(parents=True, exist_ok=True)
UPLOADS_DIR.mkdir(parents=True, exist_ok=True)
DB_DIR.mkdir(parents=True, exist_ok=True)

SCHEMES_FILE = DATA_DIR / "schemes.json"
SQLITE_DB_PATH = DB_DIR / "app.db"

MAX_UPLOAD_SIZE_MB = 10
ALLOWED_EXTENSIONS = {".pdf", ".png", ".jpg", ".jpeg", ".txt"}

# Security & CORS settings
ALLOWED_ORIGINS = ["http://localhost:5173", "http://127.0.0.1:5173", "*"]
