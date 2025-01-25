from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List


class AuthorCreate(BaseModel):
    name: str
    biography: str
    birth_date: str


class UserCreate(BaseModel):
    username: str
    password: str
    is_admin: bool = False


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: Optional[str] = None


class BookCreate(BaseModel):
    title: str
    description: Optional[str] = None
    publication_date: Optional[datetime] = None  # Сделать необязательным
    genre: str
    available_copies: int = 0
    author_ids: List[int] = []  # Список ID авторов

