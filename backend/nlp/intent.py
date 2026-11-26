import re
from typing import Dict, Any
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB

# Training seed data for Intent Classification
TRAINING_DATA = [
    # FIND_SCHOLARSHIP
    ("What government scholarships may be relevant to me?", "FIND_SCHOLARSHIP"),
    ("Which scholarships can an engineering student apply for?", "FIND_SCHOLARSHIP"),
    ("Scholarships for 20 year old student from Karnataka", "FIND_SCHOLARSHIP"),
    ("Financial aid for college education and tuition fees", "FIND_SCHOLARSHIP"),
    ("Show me post matric scholarship schemes", "FIND_SCHOLARSHIP"),
    
    # FIND_AGRICULTURE_SCHEME
    ("I am a farmer from Karnataka. What schemes can help with irrigation?", "FIND_AGRICULTURE_SCHEME"),
    ("Agricultural subsides and landholding financial support for farmers", "FIND_AGRICULTURE_SCHEME"),
    ("PM Kisan scheme details for farmers", "FIND_AGRICULTURE_SCHEME"),
    ("Farming loans and crop support government programs", "FIND_AGRICULTURE_SCHEME"),
    
    # GET_REQUIRED_DOCUMENTS
    ("What documents do I need for this scheme?", "GET_REQUIRED_DOCUMENTS"),
    ("Which certificates should I upload for post-matric scholarship?", "GET_REQUIRED_DOCUMENTS"),
    ("Required documents list for application", "GET_REQUIRED_DOCUMENTS"),
    ("Do I need income certificate and residence certificate?", "GET_REQUIRED_DOCUMENTS"),
    
    # EXPLAIN_ELIGIBILITY
    ("Why did I not match this scheme?", "EXPLAIN_ELIGIBILITY"),
    ("Explain why my application status says ineligible", "EXPLAIN_ELIGIBILITY"),
    ("Why am I disqualified for this scholarship?", "EXPLAIN_ELIGIBILITY"),
    ("Explain my eligibility breakdown", "EXPLAIN_ELIGIBILITY"),
    
    # SCHEME_INFORMATION
    ("What is this scheme about?", "SCHEME_INFORMATION"),
    ("Tell me more about Gruha Lakshmi scheme", "SCHEME_INFORMATION"),
    ("Summarize Mudra loan details and benefits", "SCHEME_INFORMATION"),
    ("What is the objective of DDRS disability scheme?", "SCHEME_INFORMATION")
]

class IntentClassifier:
    def __init__(self):
        self.vectorizer = TfidfVectorizer(ngram_range=(1, 2))
        self.clf = MultinomialNB()
        self._is_trained = False
        self._train()

    def _train(self):
        texts, labels = zip(*TRAINING_DATA)
        X = self.vectorizer.fit_transform(texts)
        self.clf.fit(X, labels)
        self._is_trained = True

    def classify(self, query: str) -> Dict[str, Any]:
        if not query or len(query.strip()) == 0:
            return {"intent": "FIND_SCHOLARSHIP", "confidence": 0.5, "method": "fallback"}
            
        lowered = query.lower()
        
        # Rule-based overrides for clear signals
        if any(w in lowered for w in ["document", "certificate", "proof", "upload", "need for"]):
            return {"intent": "GET_REQUIRED_DOCUMENTS", "confidence": 0.95, "method": "rule"}
        if any(w in lowered for w in ["why did i not match", "why ineligible", "explain my", "why failed"]):
            return {"intent": "EXPLAIN_ELIGIBILITY", "confidence": 0.95, "method": "rule"}
        if any(w in lowered for w in ["farmer", "irrigation", "pm kisan", "crop", "agriculture"]):
            return {"intent": "FIND_AGRICULTURE_SCHEME", "confidence": 0.92, "method": "rule"}

        # ML Model Inference
        X_test = self.vectorizer.transform([query])
        probs = self.clf.predict_proba(X_test)[0]
        max_idx = probs.argmax()
        intent = self.clf.classes_[max_idx]
        confidence = float(probs[max_idx])

        return {
            "intent": intent,
            "confidence": round(confidence, 2),
            "method": "ml_tfidf"
        }

intent_classifier = IntentClassifier()
