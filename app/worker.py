"""Background worker functions.

The worker is executed by an RQ worker process and is responsible for turning
uploaded documents into searchable chunks with vector embeddings.  The real
project will eventually contain sophisticated parsing and embedding logic, but
for the purposes of this example we use a very small, self‑contained
implementation.
"""

import os
from typing import List

from sqlalchemy.orm import Session

from app.db import SessionLocal
from app.embeddings import embed_text
from app.models import Document, DocumentChunk


CHUNK_SIZE = 500  # characters per chunk for our toy ingestion


def _chunk_text(text: str) -> List[str]:
    """Split ``text`` into rough equally sized chunks."""

    return [text[i : i + CHUNK_SIZE] for i in range(0, len(text), CHUNK_SIZE)] or [text]


def process_document(doc_id: str) -> None:
    """Process a document and populate ``DocumentChunk`` rows.

    The function performs the following steps:
    * mark the document as processing
    * read the file from disk
    * create chunks and embeddings
    * mark the document as ready (or failed on error)
    """

    db: Session = SessionLocal()
    try:
        doc = db.query(Document).filter(Document.id == doc_id).first()
        if not doc:
            return

        if doc.status not in ("processing", "ready"):
            doc.status = "processing"
            db.add(doc)
            db.commit()

        text = ""
        if doc.storage_path and os.path.exists(doc.storage_path):
            with open(doc.storage_path, "rb") as f:
                text = f.read().decode("utf-8", "ignore")
        elif doc.url:
            # In a full implementation we would fetch the URL.  For now just
            # use the URL itself as content so that search has something.
            text = doc.url

        chunks = _chunk_text(text)
        for chunk_text in chunks:
            emb = embed_text(chunk_text)
            chunk = DocumentChunk(
                user_id=doc.user_id,
                document_id=doc.id,
                content=chunk_text,
                embedding=emb,
            )
            db.add(chunk)

        doc.status = "ready"
        doc.error = None
        db.add(doc)
        db.commit()
    except Exception as e:  # pragma: no cover - defensive; worker environment only
        try:
            doc = db.query(Document).filter(Document.id == doc_id).first()
            if doc:
                doc.status = "failed"
                doc.error = str(e)
                db.add(doc)
                db.commit()
        except Exception:
            pass
    finally:
        db.close()
