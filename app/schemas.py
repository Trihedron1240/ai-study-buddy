"""Pydantic schema definitions used by the API."""

from pydantic import BaseModel, Field, EmailStr
from typing import Optional, List

class UserCreate(BaseModel):
    email: EmailStr
    password: str

class UserOut(BaseModel):
    id: str
    email: EmailStr
    class Config:
        from_attributes = True

class TokenOut(BaseModel):
    access_token: str
    token_type: str = "bearer"

class DocumentOut(BaseModel):
    id: str
    title: str
    source_type: str
    status: str
    storage_path: Optional[str] = None
    url: Optional[str] = None
    error: Optional[str] = None

    class Config:
        from_attributes = True


class SearchRequest(BaseModel):
    """Request payload for the search endpoint."""

    query: str
    top_k: int = 5


class SearchResult(BaseModel):
    """A ranked chunk returned from a search query."""

    document_id: str
    document_title: str
    content: str
    score: float
