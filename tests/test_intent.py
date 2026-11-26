import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "backend"))

from nlp.intent import intent_classifier

def test_intent_classification():
    res1 = intent_classifier.classify("What scholarships can I apply for?")
    assert res1["intent"] == "FIND_SCHOLARSHIP"

    res2 = intent_classifier.classify("I am a farmer from Karnataka. What schemes can help with irrigation?")
    assert res2["intent"] == "FIND_AGRICULTURE_SCHEME"

    res3 = intent_classifier.classify("What documents do I need for this scheme?")
    assert res3["intent"] == "GET_REQUIRED_DOCUMENTS"

    res4 = intent_classifier.classify("Why did I not match this scheme?")
    assert res4["intent"] == "EXPLAIN_ELIGIBILITY"
