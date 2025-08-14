"""Application entry point.

The FastAPI instance defined here wires together database models, routers and
middleware.  Individual route handlers live inside the ``routes`` package to
keep this file small and focused.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.db import Base, engine
from app import models  # ensure models are registered with SQLAlchemy
from app.routes import users, documents, search

# Create tables on startup (for a real app alembic migrations are recommended)
Base.metadata.create_all(bind=engine)

app = FastAPI(title="AI Study Buddy")

# CORS configuration – adjust ``allow_origins`` in production
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routers
app.include_router(users.router)
app.include_router(documents.router)
app.include_router(search.router)


@app.get("/")
def root() -> dict:
    """Simple health check endpoint."""

    return {"message": "AI Study Buddy backend running"}
