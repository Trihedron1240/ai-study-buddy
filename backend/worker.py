import time
from sqlalchemy.orm import Session
from db import SessionLocal
from models import Document

def process_document(doc_id: str):
    """
    Stub ingestion:
    - mark as processing (if not already)
    - simulate work
    - mark as ready
    Later: extract text, chunk, generate flashcards, attach stats.
    """
    db: Session = SessionLocal()
    try:
        doc = db.query(Document).filter(Document.id == doc_id).first()
        if not doc:
            return
        # ensure processing
        if doc.status not in ("processing", "ready"):
            doc.status = "processing"
            db.add(doc)
            db.commit()

        # Simulate ingestion work
        time.sleep(3)

        # Done
        doc.status = "ready"
        doc.error = None
        db.add(doc)
        db.commit()
    except Exception as e:
        # mark failed on error
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
