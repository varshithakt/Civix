import json
from typing import List, Dict, Any, Optional
from config import SCHEMES_FILE

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

# Global instance
db_repo = SchemeRepository()
