# NLP-Based Government Scheme Eligibility & Application Assistant

An intelligent full-stack NLP web application that helps citizens discover government schemes they may be eligible for, parses natural-language queries and unstructured document certificates, normalizes extracted information into structured user profiles, checks deterministic eligibility rules, detects document contradictions and missing requirements, simplifies policy legalese, and pre-fills scheme applications.

---

## 🏛️ Core NLP Concepts Implemented

This project is built from scratch to visibly demonstrate core Natural Language Processing and Document Intelligence concepts:

1. **Text Preprocessing**: Tokenization, cleaning, lowercasing, and stop-word filtering (`backend/nlp/preprocessing.py`).
2. **Named Entity Recognition (NER) & Information Extraction**: Contextual extraction of Age, Income, Education, State, District, Occupation, Category, Gender, and Disability percentage (`backend/nlp/extraction.py`).
3. **Entity Normalization**: Standardizes financial expressions (e.g., `₹1.8 lakh`, `15000/pm`, `1.8L pa` → `180,000` annual income), distinguishes individual vs family income, and normalizes state/education levels (`backend/nlp/normalization.py`).
4. **Intent Classification**: Machine learning (TF-IDF + Naive Bayes) & rule-based classifier detecting user intent (`FIND_SCHOLARSHIP`, `FIND_AGRICULTURE_SCHEME`, `GET_REQUIRED_DOCUMENTS`, `EXPLAIN_ELIGIBILITY`, `SCHEME_INFORMATION`) (`backend/nlp/intent.py`).
5. **Document Type Classification**: Classifies OCR certificate text into 7 categories (`Income Certificate`, `Residence Certificate`, `College ID`, `Marks Card`, `Caste Certificate`, `Disability Certificate`, `Identity Document`) with confidence score percentages (`backend/nlp/classification.py`).
6. **Text Embeddings & Semantic Similarity**: Vector similarity ranking matching user profile/queries against scheme descriptions (`backend/nlp/embeddings.py`).
7. **Deterministic Rule-Based Eligibility Engine**: Evaluates criteria (`min_age`, `max_age`, `income_limit`, `education`, `state`, `category`, `gender`) and provides criterion-level breakdown (`matched`, `unmatched`, `unknown`) (`backend/eligibility/rules.py`).
8. **Government Language Simplification**: Translates complex policy legalese into plain, accessible language without altering rules (`backend/nlp/explanation.py`).
9. **Missing Document Detection**: Compares scheme document requirements against uploaded certificates (`backend/eligibility/matcher.py`).
10. **Cross-Document Contradiction Analysis**: Scans uploaded files for profile inconsistencies (e.g. Income ₹1.5L vs ₹2.5L, age mismatch) (`backend/eligibility/contradiction.py`).
11. **Grounded Question Answering**: Conversational scheme assistant grounded strictly in stored scheme data without LLM hallucination (`backend/api/chat.py`).
12. **Form Auto-Fill Preview**: Maps confirmed user profile into application fields for mandatory user review prior to official portal submission (`backend/api/profile.py`).

---

## 📁 Project Structure

```
government-scheme-assistant/
│
├── backend/
│   ├── app.py                  # FastAPI entry point & CORS
│   ├── config.py               # Settings, upload paths, security
│   ├── requirements.txt        # Python backend dependencies
│   │
│   ├── api/
│   │   ├── nlp_api.py          # Query parsing & intent endpoint
│   │   ├── documents.py        # File upload, OCR, & contradiction scan
│   │   ├── schemes.py          # Scheme listing, matching, & detail
│   │   ├── profile.py          # Profile management & form autofill
│   │   └── chat.py             # Grounded scheme QA chatbot
│   │
│   ├── nlp/
│   │   ├── preprocessing.py    # Cleaning, tokenization, stop-words
│   │   ├── extraction.py       # NER entity extraction
│   │   ├── normalization.py    # Income, state, & category normalizer
│   │   ├── intent.py           # Intent classifier (TF-IDF + ML)
│   │   ├── classification.py   # Document classification + confidence %
│   │   ├── embeddings.py       # TF-IDF / Transformer similarity engine
│   │   └── explanation.py      # Plain language simplification
│   │
│   ├── ocr/
│   │   └── ocr_service.py      # PDF, Image, & Text OCR extractor
│   │
│   ├── eligibility/
│   │   ├── rules.py            # Deterministic rule evaluator
│   │   ├── matcher.py          # Hybrid retrieval & missing doc check
│   │   └── contradiction.py    # Cross-document inconsistency detector
│   │
│   ├── database/
│   │   └── db.py               # Repository abstraction layer
│   │
│   └── data/
│       └── schemes.json        # Seed scheme dataset with official URLs
│
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── Navbar.jsx
│   │   │   ├── NLPPipelineVisualizer.jsx
│   │   │   └── ContradictionAlerts.jsx
│   │   │
│   │   ├── pages/
│   │   │   ├── Home.jsx
│   │   │   ├── DocumentUpload.jsx
│   │   │   ├── UserProfilePage.jsx
│   │   │   ├── SchemeDiscovery.jsx
│   │   │   ├── SchemeDetailsPage.jsx
│   │   │   ├── FormAutofillPage.jsx
│   │   │   └── SchemeChatbotPage.jsx
│   │   │
│   │   ├── services/
│   │   │   └── api.js          # Axios API service wrapper
│   │   │
│   │   ├── App.jsx             # Main Router & Layout
│   │   ├── index.css           # Custom UI CSS & Badges
│   │   └── main.jsx
│   │
│   ├── package.json
│   └── vite.config.js
│
├── tests/
│   ├── test_extraction.py      # Unit tests for income/NER normalization
│   ├── test_intent.py          # Unit tests for intent classification
│   ├── test_eligibility.py     # Unit tests for rule engine
│   └── test_contradiction.py   # Unit tests for contradiction scan
│
├── .gitignore
└── README.md
```

---

## ⚡ Quick Start Guide

### 1. Prerequisites
- **Python 3.10+** (Python 3.14 compatible)
- **Node.js 18+** & `npm`

---

### 2. Backend Setup & Run

1. Navigate to the `backend` directory:
   ```bash
   cd backend
   ```

2. Create and activate a Python virtual environment:
   ```bash
   python -m venv venv
   # Windows:
   venv\Scripts\activate
   # Linux/macOS:
   source venv/bin/activate
   ```

3. Install requirements:
   ```bash
   pip install -r requirements.txt
   ```

4. Start the FastAPI backend server:
   ```bash
   python app.py
   ```
   *The backend will start at `http://127.0.0.1:8000`.*
   *Interactive API Docs (Swagger) available at `http://127.0.0.1:8000/docs`.*

---

### 3. Frontend Setup & Run

1. Open a new terminal and navigate to the `frontend` directory:
   ```bash
   cd frontend
   ```

2. Install Node dependencies:
   ```bash
   npm install
   ```

3. Start the Vite development server:
   ```bash
   npm run dev
   ```
   *The frontend application will run at `http://localhost:5173`.*

---

## 🧪 Running Unit Tests

Run `pytest` from the root directory to verify extraction rules, income normalization, intent classification, eligibility logic, and contradiction detection:

```bash
pytest tests/
```

---

## ➕ How to Add Real Government Schemes

Edit `backend/data/schemes.json` to add new schemes using the standard flexible schema:

```json
{
  "id": "SCH009",
  "name": "Scheme Name",
  "category": "Education / Agriculture / Women Welfare",
  "description": "Full formal official policy text...",
  "simplified_description": "Simple plain language explanation...",
  "eligibility": {
    "min_age": 18,
    "max_age": 25,
    "income_limit": 250000,
    "education": ["undergraduate", "engineering"],
    "occupation": ["student"],
    "states": ["Karnataka", "All"],
    "categories": ["All"],
    "gender": "All"
  },
  "required_documents": [
    {"name": "Income Certificate", "code": "income_cert"},
    {"name": "Residence Certificate", "code": "residence_cert"}
  ],
  "source_url": "https://official-government-portal.gov.in"
}
```

---

## 🛡️ Disclaimer & Security Notice

- **Potentially Eligible Disclaimer**: The system explicitly states *"Potentially eligible based on the information provided"* or *"Potential match based on available scheme criteria"*. It never guarantees official government approval.
- **Official URL Linkage**: Every scheme renders a direct hyperlink to its official source portal.
- **No Unsolicited Auto-Submission**: The form auto-fill module provides a pre-filled preview for user review. Applications are never automatically submitted.
