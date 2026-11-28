from typing import List, Dict, Any
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

class SemanticEmbeddingEngine:
    def __init__(self):
        self.vectorizer = TfidfVectorizer(stop_words='english', ngram_range=(1, 2))
        self.scheme_corpus: List[str] = []
        self.scheme_ids: List[str] = []
        self._is_indexed = False

    def index_schemes(self, schemes: List[Dict[str, Any]]):
        """Indexes scheme descriptions and eligibility text for fast semantic retrieval."""
        self.scheme_corpus = []
        self.scheme_ids = []
        
        for s in schemes:
            # Combine name, category, description, simplified description, and eligibility specs
            text = f"{s.get('name', '')} {s.get('category', '')} {s.get('description', '')} {s.get('simplified_description', '')}"
            elig = s.get('eligibility', {})
            text += f" education: {' '.join(elig.get('education', []))}"
            text += f" occupation: {' '.join(elig.get('occupation', []))}"
            text += f" states: {' '.join(elig.get('states', []))}"
            
            self.scheme_corpus.append(text)
            self.scheme_ids.append(s.get('id', ''))
            
        if self.scheme_corpus:
            self.vectorizer.fit(self.scheme_corpus)
            self.scheme_vectors = self.vectorizer.transform(self.scheme_corpus)
            self._is_indexed = True

    def calculate_similarity(self, query: str) -> Dict[str, float]:
        """
        Calculates cosine similarity scores between the query/profile text and indexed schemes.
        Returns a dict mapping scheme_id -> similarity_score (0.0 to 1.0).
        """
        if not self._is_indexed or not query:
            return {}
            
        query_vec = self.vectorizer.transform([query])
        similarities = cosine_similarity(query_vec, self.scheme_vectors)[0]
        
        scores = {}
        for idx, scheme_id in enumerate(self.scheme_ids):
            scores[scheme_id] = round(float(similarities[idx]), 3)
            
        return scores

embedding_engine = SemanticEmbeddingEngine()
