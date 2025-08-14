"""Routes related to document management."""

import os
import shutil
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, status
from sqlalchemy.orm import Session

from app.auth import get_current_user
from app.db import get_db
from app.jobs import enqueue_ingest
from app.models import Document, User
from app.schemas import DocumentOut

UPLOAD_ROOT = "/data/uploads"

router = APIRouter(prefix="/documents", tags=["documents"])


def ensure_dirs() -> None:
    os.makedirs(UPLOAD_ROOT, exist_ok=True)


@router.post("/", response_model=DocumentOut)
async def create_document(
    current: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    file: Optional[UploadFile] = File(None),
    url: Optional[str] = Form(None),
    title: Optional[str] = Form(None),
):
    """Upload a document or register a URL and enqueue ingestion."""

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
        safe_name = f"{doc.id}_{file.filename}".replace(" ", "_")
        dest_path = os.path.join(UPLOAD_ROOT, safe_name)
        with open(dest_path, "wb") as out:
            shutil.copyfileobj(file.file, out)
        doc.storage_path = dest_path
        db.add(doc)
        db.commit()

    else:
        doc.url = url
        db.add(doc)
        db.commit()

    # Kick off background ingestion job
    enqueue_ingest(doc.id)

    db.refresh(doc)
    return doc


@router.get("/", response_model=List[DocumentOut])
def list_documents(current: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Return all documents for the current user."""

    docs = (
        db.query(Document)
        .filter(Document.user_id == current.id)
        .order_by(Document.created_at.desc())
        .all()
    )
    return docs


@router.get("/{doc_id}", response_model=DocumentOut)
def get_document(doc_id: str, current: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Return a single document."""

    doc = db.query(Document).filter(Document.id == doc_id, Document.user_id == current.id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    return doc


@router.delete("/{doc_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_document(doc_id: str, current: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Delete a document and associated resources."""

    doc = db.query(Document).filter(Document.id == doc_id, Document.user_id == current.id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")

    if doc.storage_path and os.path.exists(doc.storage_path):
        try:
            os.remove(doc.storage_path)
        except OSError:
            pass  # Ignore file removal errors

    db.delete(doc)
    db.commit()
    return None
