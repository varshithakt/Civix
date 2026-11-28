from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from config import ALLOWED_ORIGINS
from database.db import db_repo
from nlp.embeddings import embedding_engine

from api.nlp_api import router as nlp_router
from api.documents import router as docs_router
from api.schemes import router as schemes_router
from api.profile import router as profile_router
from api.chat import router as chat_router
from api.applications import router as applications_router

app = FastAPI(
    title="NLP-Based Government Scheme Eligibility & Application Assistant API",
    version="1.0.0",
    description="Backend service providing OCR, NLP entity extraction, semantic retrieval, deterministic eligibility rules, and document contradiction analysis."
)

# CORS Setup
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register Routers
app.include_router(nlp_router)
app.include_router(docs_router)
app.include_router(schemes_router)
app.include_router(profile_router)
app.include_router(chat_router)
app.include_router(applications_router)


@app.on_event("startup")
def startup_event():
    """Index schemes into vector embedding engine upon server start."""
    schemes = db_repo.get_all()
    embedding_engine.index_schemes(schemes)
    print(f"[STARTUP] Initialized Scheme DB with {len(schemes)} schemes and indexed vector embeddings.")


@app.get("/")
def health_check():
    return {
        "status": "online",
        "service": "NLP Government Scheme Assistant API",
        "version": "1.0.0",
        "schemes_indexed": len(db_repo.get_all())
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="127.0.0.1", port=8000, reload=True)
