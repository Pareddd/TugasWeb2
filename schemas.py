from pydantic import BaseModel
from typing import Optional

# === ITEM SCHEMAS ===
class ItemBase(BaseModel):
    name: str
    description: Optional[str] = None

class ItemCreate(ItemBase):
    pass

class ItemResponse(ItemBase):
    id: int

    class Config:
        from_attributes = True

# === USER & AUTH SCHEMAS ===
class UserCreate(BaseModel):
    username: str
    password: str
    role: str = "user"  # Bisa diisi "admin" saat registrasi untuk testing

class UserResponse(BaseModel):
    id: int
    username: str
    role: str

    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None