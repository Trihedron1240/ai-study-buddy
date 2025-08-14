from pydantic import BaseModel, Field, EmailStr
from typing import Optional

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
