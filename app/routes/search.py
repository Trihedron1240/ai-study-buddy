"""Search endpoint utilising simple vector embeddings."""

from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from auth import get_current_user
from db import get_db
from embeddings import embed_text, cosine_similarity
from models import Document, DocumentChunk, User
from schemas import SearchRequest, SearchResult

router = APIRouter(tags=["search"])


@router.post("/search", response_model=List[SearchResult])
def search_documents(
    payload: SearchRequest,
    current: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Return the top document chunks ranked by similarity to the query."""

    query_emb = embed_text(payload.query)

    rows = (
        db.query(DocumentChunk, Document)
        .join(Document, Document.id == DocumentChunk.document_id)
        .filter(Document.user_id == current.id)
        .all()
    )

    scored: List[SearchResult] = []
    for chunk, doc in rows:
        score = cosine_similarity(query_emb, chunk.embedding)
        scored.append(
            SearchResult(
                document_id=doc.id,
                document_title=doc.title,
                content=chunk.content,
                score=score,
            )
        )

    scored.sort(key=lambda x: x.score, reverse=True)
    return scored[: payload.top_k]
