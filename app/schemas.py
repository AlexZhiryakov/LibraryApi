from datetime import date

from pydantic import BaseModel, ConfigDict, Field


# ---------- Авторы ----------
class AuthorCreate(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    biography: str | None = Field(default=None, max_length=5000)
    birth_date: date | None = None


class AuthorRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    biography: str | None = None
    birth_date: date | None = None


# ---------- Пользователи ----------
class UserRegister(BaseModel):
    """Схема регистрации. Роль не принимается от клиента — всегда обычный
    пользователь. Администраторы создаются только через POST /add_admin."""

    username: str = Field(min_length=3, max_length=50)
    password: str = Field(min_length=8, max_length=128)


class UserLogin(BaseModel):
    username: str = Field(min_length=1, max_length=50)
    password: str = Field(min_length=1, max_length=128)


class UserUpdate(BaseModel):
    username: str = Field(min_length=3, max_length=50)
    password: str | None = Field(default=None, min_length=8, max_length=128)


class UserRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    username: str
    is_admin: bool


class AdminCreate(BaseModel):
    username: str = Field(min_length=3, max_length=50)
    password: str = Field(min_length=8, max_length=128)


# ---------- Токены ----------
class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: str | None = None


# ---------- Книги ----------
class BookCreate(BaseModel):
    title: str = Field(min_length=1, max_length=255)
    description: str | None = Field(default=None, max_length=5000)
    publication_date: date | None = None
    genre: str = Field(min_length=1, max_length=100)
    available_copies: int = Field(default=0, ge=0)
    author_ids: list[int] = Field(default_factory=list)


class AuthorBrief(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str


class BookRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    description: str | None = None
    publication_date: date | None = None
    genre: str
    available_copies: int
    authors: list[AuthorBrief] = Field(default_factory=list)


# ---------- Выдача книг ----------
class BorrowCreate(BaseModel):
    user_id: int = Field(gt=0)
    book_id: int = Field(gt=0)


class BorrowRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    book_id: int
    borrow_date: date
    return_date: date | None = None


class Message(BaseModel):
    detail: str

