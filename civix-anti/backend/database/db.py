import json
import sqlite3
from pathlib import Path
from typing import List, Dict, Any, Optional
from config import SCHEMES_FILE, SQLITE_DB_PATH


class SchemeRepository:
    def __init__(self, data_path=SCHEMES_FILE):
        self.data_path = data_path
        self._schemes: List[Dict[str, Any]] = []
        self.load_schemes()

    def load_schemes(self):
        if self.data_path.exists():
            with open(self.data_path, "r", encoding="utf-8") as f:
                self._schemes = json.load(f)
        else:
            self._schemes = []

    def get_all(self) -> List[Dict[str, Any]]:
        return self._schemes

    def get_by_id(self, scheme_id: str) -> Optional[Dict[str, Any]]:
        for scheme in self._schemes:
            if scheme.get("id") == scheme_id:
                return scheme
        return None

    def search_by_category(self, category: str) -> List[Dict[str, Any]]:
        return [
            s for s in self._schemes
            if s.get("category", "").lower() == category.lower()
        ]


class ApplicationRepository:
    """SQLite persistence layer for direct scheme applications and their progress."""

    def __init__(self, db_path: Path = SQLITE_DB_PATH):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(str(self.db_path))
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self):
        with self._connect() as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS applications (
                    id TEXT PRIMARY KEY,
                    scheme_id TEXT NOT NULL,
                    scheme_name TEXT NOT NULL,
                    category TEXT NOT NULL,
                    source_url TEXT NOT NULL,
                    applicant_name TEXT NOT NULL,
                    status TEXT NOT NULL,
                    current_step INTEGER NOT NULL,
                    progress_pct INTEGER NOT NULL,
                    eligibility_status TEXT NOT NULL,
                    user_confirmed INTEGER NOT NULL,
                    form_data_json TEXT NOT NULL,
                    documents_json TEXT NOT NULL,
                    timeline_json TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                )
                """
            )
            conn.commit()

    def _row_to_dict(self, row: sqlite3.Row) -> Dict[str, Any]:
        return {
            "id": row["id"],
            "scheme_id": row["scheme_id"],
            "scheme_name": row["scheme_name"],
            "category": row["category"],
            "source_url": row["source_url"],
            "applicant_name": row["applicant_name"],
            "status": row["status"],
            "current_step": row["current_step"],
            "progress_pct": row["progress_pct"],
            "eligibility_status": row["eligibility_status"],
            "user_confirmed": bool(row["user_confirmed"]),
            "form_data": json.loads(row["form_data_json"]),
            "documents": json.loads(row["documents_json"]),
            "timeline": json.loads(row["timeline_json"]),
            "created_at": row["created_at"],
            "updated_at": row["updated_at"],
        }

    def save(self, app_record: Dict[str, Any]) -> Dict[str, Any]:
        with self._connect() as conn:
            conn.execute(
                """
                INSERT OR REPLACE INTO applications (
                    id, scheme_id, scheme_name, category, source_url,
                    applicant_name, status, current_step, progress_pct,
                    eligibility_status, user_confirmed,
                    form_data_json, documents_json, timeline_json,
                    created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    app_record["id"],
                    app_record["scheme_id"],
                    app_record["scheme_name"],
                    app_record["category"],
                    app_record["source_url"],
                    app_record["applicant_name"],
                    app_record["status"],
                    int(app_record["current_step"]),
                    int(app_record["progress_pct"]),
                    app_record["eligibility_status"],
                    1 if app_record["user_confirmed"] else 0,
                    json.dumps(app_record["form_data"]),
                    json.dumps(app_record["documents"]),
                    json.dumps(app_record["timeline"]),
                    app_record["created_at"],
                    app_record["updated_at"],
                ),
            )
            conn.commit()
        return app_record

    def list_all(self) -> List[Dict[str, Any]]:
        with self._connect() as conn:
            rows = conn.execute(
                "SELECT * FROM applications ORDER BY updated_at DESC"
            ).fetchall()
            return [self._row_to_dict(r) for r in rows]

    def get_by_id(self, app_id: str) -> Optional[Dict[str, Any]]:
        with self._connect() as conn:
            row = conn.execute(
                "SELECT * FROM applications WHERE id = ?", (app_id,)
            ).fetchone()
            return self._row_to_dict(row) if row else None

    def delete(self, app_id: str) -> bool:
        with self._connect() as conn:
            cur = conn.execute("DELETE FROM applications WHERE id = ?", (app_id,))
            conn.commit()
            return cur.rowcount > 0


# Global instances
db_repo = SchemeRepository()
app_repo = ApplicationRepository()
