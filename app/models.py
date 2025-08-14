"""Database models for the application.

This module contains SQLAlchemy model definitions.  Only the pieces that are
required for the current backend implementation are included.  The models are
intentionally lightweight – fields that are not yet used by the API are left
out to keep the example concise.
"""

from sqlalchemy import (
    Column,
    String,
    DateTime,
    Text,
    Integer,
    Float,
    ForeignKey,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from db import Base
import uuid

def gen_id() -> str:
    return str(uuid.uuid4())

class User(Base):
    __tablename__ = "users"
    id = Column(String, primary_key=True, default=gen_id)
    email = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    documents = relationship("Document", back_populates="user", cascade="all, delete-orphan")

class Document(Base):
    __tablename__ = "documents"
    id = Column(String, primary_key=True, default=gen_id)
    user_id = Column(String, ForeignKey("users.id"), index=True, nullable=False)
    title = Column(String, nullable=False)
    source_type = Column(String, nullable=False)  # upload | url | raw
    storage_path = Column(Text, nullable=True)    # e.g., /data/uploads/<file>
    url = Column(Text, nullable=True)             # when source_type == url
    status = Column(String, nullable=False, default="pending")  # pending | processing | ready | failed
    error = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    user = relationship("User", back_populates="documents")
    chunks = relationship(
        "DocumentChunk", back_populates="document", cascade="all, delete-orphan"
    )


class DocumentChunk(Base):
    """A small chunk of a document along with its vector embedding."""

    __tablename__ = "document_chunks"

    id = Column(String, primary_key=True, default=gen_id)
    user_id = Column(String, ForeignKey("users.id"), index=True, nullable=False)
    document_id = Column(String, ForeignKey("documents.id"), index=True, nullable=False)
    content = Column(Text, nullable=False)
    embedding = Column(JSONB, nullable=False)

    document = relationship("Document", back_populates="chunks")


# Placeholders (we'll flesh these out in later days)
class Flashcard(Base):
    __tablename__ = "flashcards"
    id = Column(String, primary_key=True, default=gen_id)
    user_id = Column(String, ForeignKey("users.id"), index=True, nullable=False)
    document_id = Column(String, ForeignKey("documents.id"), index=True, nullable=True)
    front = Column(Text, nullable=False)
    back = Column(Text, nullable=False)
    tags = Column(Text, nullable=True)  # simple CSV for now; we'll switch to JSON later
    difficulty = Column(Float, nullable=False, default=0.5)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class Schedule(Base):
    __tablename__ = "schedules"
    id = Column(String, primary_key=True, default=gen_id)
    flashcard_id = Column(String, ForeignKey("flashcards.id"), unique=True, nullable=False)
    ease = Column(Float, nullable=False, default=2.5)
    interval_days = Column(Integer, nullable=False, default=0)
    reps = Column(Integer, nullable=False, default=0)
    due_date = Column(DateTime(timezone=True), nullable=True)

class Review(Base):
    __tablename__ = "reviews"
    id = Column(String, primary_key=True, default=gen_id)
    flashcard_id = Column(String, ForeignKey("flashcards.id"), index=True, nullable=False)
    rating = Column(Integer, nullable=False)  # 0-5
    elapsed_s = Column(Integer, nullable=False, default=0)
    reviewed_at = Column(DateTime(timezone=True), server_default=func.now())
