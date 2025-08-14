import os
import shutil
from datetime import datetime
from typing import Optional, List

from fastapi import FastAPI, Depends, HTTPException, status, Form, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from db import Base, engine, get_db
from models import User, Document
from schemas import UserCreate, UserOut, TokenOut, DocumentOut
from auth import hash_password, verify_password, create_access_token, get_current_user
from jobs import enqueue_ingest

# Create tables on startup (simple for now)
Base.metadata.create_all(bind=engine)

app = FastAPI(title="AI Study Buddy")

# CORS (adjust origins later)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], allow_credentials=True,
    allow_methods=["*"], allow_headers=["*"],
)

@app.get("/")
def root():
    return {"message": "AI Study Buddy backend running"}

# -------- Auth --------
@app.post("/auth/register", response_model=UserOut)
def register(payload: UserCreate, db: Session = Depends(get_db)):
    existing = db.query(User).filter(User.email == payload.email.lower()).first()
    if existing:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered")
    user = User(email=payload.email.lower(), password_hash=hash_password(payload.password))
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

@app.post("/auth/login", response_model=TokenOut)
def login(username: str = Form(...), password: str = Form(...), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == username.lower()).first()
    if not user or not verify_password(password, user.password_hash):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Incorrect email or password")
    token = create_access_token(sub=user.id)
    return {"access_token": token, "token_type": "bearer"}

@app.get("/me", response_model=UserOut)
def me(current: User = Depends(get_current_user)):
    return current

# -------- Documents --------
UPLOAD_ROOT = "/data/uploads"

def ensure_dirs():
    os.makedirs(UPLOAD_ROOT, exist_ok=True)

@app.post("/documents", response_model=DocumentOut)
async def create_document(
    current: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    file: Optional[UploadFile] = File(None),
    url: Optional[str] = Form(None),
    title: Optional[str] = Form(None),
):
    """
    Create a document by either uploading a file OR providing a URL.
    - If file is provided: save to /data/uploads and mark status='ready' (ingestion to be added later).
    - If url is provided: store URL and mark status='pending' (we'll process later).
    """
    if not file and not url:
        raise HTTPException(status_code=400, detail="Provide either a file or a url")

    ensure_dirs()

    doc = Document(
        user_id=current.id,
        title=title or (file.filename if file else url),
        source_type="upload" if file else "url",
        status="pending",
    )
    db.add(doc)
    db.commit()
    db.refresh(doc)

    if file:
        # Save the uploaded file
        safe_name = f"{doc.id}_{file.filename}".replace(" ", "_")
        dest_path = os.path.join(UPLOAD_ROOT, safe_name)
        with open(dest_path, "wb") as out:
            shutil.copyfileobj(file.file, out)
        # Mark as ready for now; later we'll enqueue ingestion
        doc.storage_path = dest_path
        doc.status = "ready"
        db.add(doc)
        db.commit()
        db.refresh(doc)
    else:
        # URL case: store and keep pending (we'll fetch/process in a later day)
        doc.url = url
        doc.status = "pending"
        db.add(doc)
        db.commit()
        db.refresh(doc)

    return doc

@app.get("/documents/{doc_id}", response_model=DocumentOut)
def get_document(doc_id: str, current: User = Depends(get_current_user), db: Session = Depends(get_db)):
    doc = db.query(Document).filter(Document.id == doc_id, Document.user_id == current.id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    return doc

@app.get("/documents", response_model=List[DocumentOut])
def list_documents(current: User = Depends(get_current_user), db: Session = Depends(get_db)):
    docs = db.query(Document).filter(Document.user_id == current.id).order_by(Document.created_at.desc()).all()
    return docs


