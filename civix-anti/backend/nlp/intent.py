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
    ("Education grant for undergraduate students with low income", "FIND_SCHOLARSHIP"),
    ("Merit scholarship for students with family income below 2 lakh", "FIND_SCHOLARSHIP"),
    ("Schemes for school students to continue higher studies", "FIND_SCHOLARSHIP"),

    # FIND_AGRICULTURE_SCHEME
    ("I am a farmer from Karnataka. What schemes can help with irrigation?", "FIND_AGRICULTURE_SCHEME"),
    ("Agricultural subsides and landholding financial support for farmers", "FIND_AGRICULTURE_SCHEME"),
    ("PM Kisan scheme details for farmers", "FIND_AGRICULTURE_SCHEME"),
    ("Farming loans and crop support government programs", "FIND_AGRICULTURE_SCHEME"),
    ("What help can I get for my farmland?", "FIND_AGRICULTURE_SCHEME"),
    ("Agricultural income support for landholding farmers", "FIND_AGRICULTURE_SCHEME"),

    # FIND_HOUSING_SCHEME
    ("What housing schemes are available for low income families?", "FIND_HOUSING_SCHEME"),
    ("I want to build a house. Are there any government schemes?", "FIND_HOUSING_SCHEME"),
    ("PM Awas Yojana eligibility and benefits", "FIND_HOUSING_SCHEME"),
    ("Scheme to get financial help for constructing a home", "FIND_HOUSING_SCHEME"),
    ("Pucca house subsidy for rural families", "FIND_HOUSING_SCHEME"),

    # FIND_DISABILITY_SCHEME
    ("What schemes exist for disabled persons?", "FIND_DISABILITY_SCHEME"),
    ("Disability support and rehabilitation programs", "FIND_DISABILITY_SCHEME"),
    ("I have 50 percent disability what government help can I get", "FIND_DISABILITY_SCHEME"),
    ("DDRS scheme for people with physical handicap", "FIND_DISABILITY_SCHEME"),
    ("Assistive equipment and vocational training for differently abled", "FIND_DISABILITY_SCHEME"),

    # FIND_BUSINESS_SCHEME
    ("I want to start a small business. What loans are available?", "FIND_BUSINESS_SCHEME"),
    ("Mudra loan for entrepreneurs and self employed persons", "FIND_BUSINESS_SCHEME"),
    ("Collateral free micro loan for starting a shop", "FIND_BUSINESS_SCHEME"),
    ("Government schemes for artisans and small business owners", "FIND_BUSINESS_SCHEME"),
    ("Working capital loan for microenterprise", "FIND_BUSINESS_SCHEME"),

    # FIND_WOMEN_SCHEME
    ("What welfare schemes are available for women?", "FIND_WOMEN_SCHEME"),
    ("Gruha Lakshmi scheme for female head of household in Karnataka", "FIND_WOMEN_SCHEME"),
    ("Monthly financial assistance for women in Karnataka", "FIND_WOMEN_SCHEME"),
    ("Government schemes for women empowerment", "FIND_WOMEN_SCHEME"),
    ("Direct benefit transfer scheme for women", "FIND_WOMEN_SCHEME"),

    # GET_REQUIRED_DOCUMENTS
    ("What documents do I need for this scheme?", "GET_REQUIRED_DOCUMENTS"),
    ("Which certificates should I upload for post-matric scholarship?", "GET_REQUIRED_DOCUMENTS"),
    ("Required documents list for application", "GET_REQUIRED_DOCUMENTS"),
    ("Do I need income certificate and residence certificate?", "GET_REQUIRED_DOCUMENTS"),
    ("What proofs are needed to apply for PM Kisan?", "GET_REQUIRED_DOCUMENTS"),
    ("List the certificates required for Mudra loan application", "GET_REQUIRED_DOCUMENTS"),

    # EXPLAIN_ELIGIBILITY
    ("Why did I not match this scheme?", "EXPLAIN_ELIGIBILITY"),
    ("Explain why my application status says ineligible", "EXPLAIN_ELIGIBILITY"),
    ("Why am I disqualified for this scholarship?", "EXPLAIN_ELIGIBILITY"),
    ("Explain my eligibility breakdown", "EXPLAIN_ELIGIBILITY"),
    ("Am I eligible for Gruha Lakshmi scheme?", "EXPLAIN_ELIGIBILITY"),
    ("Check if I qualify for PM Kisan based on my profile", "EXPLAIN_ELIGIBILITY"),
    ("Why is my income not matching the scheme limit?", "EXPLAIN_ELIGIBILITY"),

    # SCHEME_INFORMATION
    ("What is this scheme about?", "SCHEME_INFORMATION"),
    ("Tell me more about Gruha Lakshmi scheme", "SCHEME_INFORMATION"),
    ("Summarize Mudra loan details and benefits", "SCHEME_INFORMATION"),
    ("What is the objective of DDRS disability scheme?", "SCHEME_INFORMATION"),
    ("Give me information about PM Awas Yojana", "SCHEME_INFORMATION"),
    ("What are the benefits of post matric scholarship?", "SCHEME_INFORMATION"),
    ("How does Karnataka merit scholarship work?", "SCHEME_INFORMATION"),
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
        if any(w in lowered for w in ["document", "certificate", "proof", "upload", "need for", "what certificates", "which documents"]):
            return {"intent": "GET_REQUIRED_DOCUMENTS", "confidence": 0.95, "method": "rule"}
        if any(w in lowered for w in ["why did i not match", "why ineligible", "explain my eligibility", "why failed", "why am i not", "am i eligible", "do i qualify", "check if i qualify"]):
            return {"intent": "EXPLAIN_ELIGIBILITY", "confidence": 0.95, "method": "rule"}
        if any(w in lowered for w in ["farmer", "irrigation", "pm kisan", "crop", "agriculture", "farming", "landholding", "kisan"]):
            return {"intent": "FIND_AGRICULTURE_SCHEME", "confidence": 0.92, "method": "rule"}
        if any(w in lowered for w in ["house", "housing", "home", "awas", "pucca", "shelter", "construct a home"]):
            return {"intent": "FIND_HOUSING_SCHEME", "confidence": 0.92, "method": "rule"}
        if any(w in lowered for w in ["disability", "disabled", "handicap", "udid", "specially abled", "differently abled", "rehabilitation"]):
            return {"intent": "FIND_DISABILITY_SCHEME", "confidence": 0.92, "method": "rule"}
        if any(w in lowered for w in ["business", "mudra", "loan", "startup", "enterprise", "entrepreneur", "artisan", "micro loan", "small business", "self employed"]):
            return {"intent": "FIND_BUSINESS_SCHEME", "confidence": 0.92, "method": "rule"}
        if any(w in lowered for w in ["women", "woman", "female", "gruha lakshmi", "widow", "girl child", "women welfare"]):
            return {"intent": "FIND_WOMEN_SCHEME", "confidence": 0.92, "method": "rule"}

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
