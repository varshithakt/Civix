import sys
sys.path.insert(0, '.')
from database.db import db_repo
from nlp.embeddings import embedding_engine
from nlp.intent import intent_classifier
from api.chat import _get_category_from_query, _handle_find_scheme, _handle_get_documents, _handle_explain_eligibility, _handle_scheme_information, _detect_target_scheme

all_schemes = db_repo.get_all()
embedding_engine.index_schemes(all_schemes)

test_queries = [
    ("I am a farmer from Karnataka. What schemes can help?", {"state": "Karnataka"}),
    ("What monthly help is available for women in Karnataka?", {"state": "Karnataka", "gender": "female", "annual_income": 150000}),
    ("I want to start a small shop and need a loan", {}),
    ("What documents do I need for PM Kisan?", {}),
    ("Am I eligible for Karnataka scholarship?", {"age": 20, "state": "Karnataka", "annual_income": 180000, "education": "engineering"}),
    ("What is Gruha Lakshmi scheme?", {}),
    ("Schemes for disabled persons", {}),
    ("I need help for my house construction", {}),
]

for q, prof in test_queries:
    intent_data = intent_classifier.classify(q)
    cat = _get_category_from_query(q)
    intent = intent_data["intent"]
    conf = intent_data["confidence"]
    method = intent_data["method"]
    print(f"Q: {q[:65]}")
    print(f"  Intent: {intent} ({conf:.2f} / {method}), Category: {cat}")

print("\n--- Full response test ---")
q = "What monthly financial help is available for women in Karnataka?"
profile = {"state": "Karnataka", "gender": "female", "annual_income": 150000}
cat = _get_category_from_query(q)
reply = _handle_find_scheme(q, profile, all_schemes, cat)
print(reply[:600])
print("...[truncated]")

print("\n--- Explain eligibility test ---")
q2 = "Am I eligible for Karnataka State Post-Matric Merit Scholarship?"
profile2 = {"age": 20, "state": "Karnataka", "annual_income": 180000, "education": "engineering"}
target2 = _detect_target_scheme(q2, None, all_schemes)
print("Target scheme:", target2["name"] if target2 else "None")
reply2 = _handle_explain_eligibility(q2, profile2, all_schemes, target2)
print(reply2[:600])
