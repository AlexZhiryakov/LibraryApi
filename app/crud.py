"""HTTP-эндпоинты API: книги, авторы, пользователи и учёт выдачи книг."""

import logging
from datetime import date

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, joinedload

from .auth import get_current_admin, get_current_user, get_user_by_username
from .database import get_db
from .models import Author, Book, BorrowRecord, User
from .schemas import (
    AdminCreate,
    AuthorCreate,
    AuthorRead,
    BookCreate,
    BookRead,
    BorrowCreate,
    BorrowRead,
    Message,
    Token,
    UserLogin,
    UserRead,
    UserRegister,
    UserUpdate,
)
from .security import create_access_token, hash_password, verify_password

logger = logging.getLogger(__name__)

router = APIRouter()


def _commit_or_conflict(db: Session, message: str) -> None:
    """Фиксирует транзакцию. При нарушении целостности отдаёт 409 без деталей
    внутренней ошибки (текст БД наружу не уходит)."""
    try:
        db.commit()
    except IntegrityError as err:
        db.rollback()
        logger.warning("Нарушение целостности БД: %s", message)
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=message) from err


# ---------- Регистрация и вход ----------
@router.post("/register", response_model=Token, status_code=status.HTTP_201_CREATED, tags=["auth"])
def register(user: UserRegister, db: Session = Depends(get_db)) -> Token:
    """Регистрирует обычного пользователя.

    Роль не принимается от клиента: админ создаётся только через POST /add_admin.
    """
    if get_user_by_username(db, user.username):
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Пользователь с таким именем уже существует")

    db_user = User(username=user.username, hashed_password=hash_password(user.password), is_admin=False)
    db.add(db_user)
    _commit_or_conflict(db, "Пользователь с таким именем уже существует")
    db.refresh(db_user)

    access_token = create_access_token(data={"sub": db_user.username})
    return Token(access_token=access_token, token_type="bearer")


@router.post("/token", response_model=Token, tags=["auth"])
def login(user: UserLogin, db: Session = Depends(get_db)) -> Token:
    db_user = get_user_by_username(db, user.username)
    if not db_user or not verify_password(user.password, db_user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Неверное имя пользователя или пароль")

    access_token = create_access_token(data={"sub": db_user.username})
    return Token(access_token=access_token, token_type="bearer")


# ---------- Книги ----------
@router.post("/books", response_model=BookRead, status_code=status.HTTP_201_CREATED, tags=["books"])
def create_new_book(
    book: BookCreate,
    db: Session = Depends(get_db),
    _admin: User = Depends(get_current_admin),
) -> Book:
    author_ids = list(dict.fromkeys(book.author_ids))
    authors = db.query(Author).filter(Author.id.in_(author_ids)).all() if author_ids else []
    if len(authors) != len(author_ids):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Один или несколько авторов не найдены")

    db_book = Book(
        title=book.title,
        description=book.description,
        publication_date=book.publication_date or date.today(),
        genre=book.genre,
        available_copies=book.available_copies,
        authors=authors,
    )
    db.add(db_book)
    _commit_or_conflict(db, "Не удалось создать книгу")
    db.refresh(db_book)
    return db_book


@router.get("/books", response_model=list[BookRead], tags=["books"])
def list_books(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)) -> list[Book]:
    return db.query(Book).options(joinedload(Book.authors)).offset(skip).limit(limit).all()


@router.delete("/books/{book_id}", response_model=Message, tags=["books"])
def delete_book(
    book_id: int,
    db: Session = Depends(get_db),
    _admin: User = Depends(get_current_admin),
) -> Message:
    db_book = db.query(Book).filter(Book.id == book_id).first()
    if not db_book:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Книга не найдена")

    active = (
        db.query(BorrowRecord)
        .filter(BorrowRecord.book_id == book_id, BorrowRecord.return_date.is_(None))
        .first()
    )
    if active:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Нельзя удалить книгу с активными выдачами")

    db.delete(db_book)
    _commit_or_conflict(db, "Не удалось удалить книгу")
    return Message(detail="Книга удалена")


# ---------- Авторы ----------
@router.post("/authors", response_model=AuthorRead, status_code=status.HTTP_201_CREATED, tags=["authors"])
def create_author(
    author: AuthorCreate,
    db: Session = Depends(get_db),
    _admin: User = Depends(get_current_admin),
) -> Author:
    db_author = Author(name=author.name, biography=author.biography, birth_date=author.birth_date)
    db.add(db_author)
    _commit_or_conflict(db, "Не удалось создать автора")
    db.refresh(db_author)
    return db_author


@router.get("/authors", response_model=list[AuthorRead], tags=["authors"])
def list_authors(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)) -> list[Author]:
    return db.query(Author).offset(skip).limit(limit).all()


# ---------- Пользователи ----------
@router.get("/users", response_model=list[UserRead], tags=["users"])
def list_readers(db: Session = Depends(get_db), _admin: User = Depends(get_current_admin)) -> list[User]:
    return db.query(User).filter(User.is_admin.is_(False)).all()


@router.put("/users/me", response_model=UserRead, tags=["users"])
def update_my_info(
    user_data: UserUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> User:
    if user_data.username != current_user.username and get_user_by_username(db, user_data.username):
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Имя пользователя уже занято")

    current_user.username = user_data.username
    if user_data.password:
        current_user.hashed_password = hash_password(user_data.password)

    _commit_or_conflict(db, "Имя пользователя уже занято")
    db.refresh(current_user)
    return current_user


@router.post("/add_admin", response_model=Message, tags=["users"])
def add_admin(
    user: AdminCreate,
    db: Session = Depends(get_db),
    _admin: User = Depends(get_current_admin),
) -> Message:
    """Создаёт администратора. Доступно только действующему администратору."""
    if get_user_by_username(db, user.username):
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Пользователь с таким именем уже существует")

    admin_user = User(username=user.username, hashed_password=hash_password(user.password), is_admin=True)
    db.add(admin_user)
    _commit_or_conflict(db, "Пользователь с таким именем уже существует")
    return Message(detail=f"Администратор {admin_user.username} создан")


# ---------- Учёт выдачи книг ----------
@router.post("/borrows", response_model=BorrowRead, status_code=status.HTTP_201_CREATED, tags=["borrows"])
def issue_book(
    payload: BorrowCreate,
    db: Session = Depends(get_db),
    _admin: User = Depends(get_current_admin),
) -> BorrowRecord:
    """Выдаёт книгу читателю. Только администратор."""
    borrower = db.query(User).filter(User.id == payload.user_id).first()
    if not borrower:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Пользователь не найден")

    book = db.query(Book).filter(Book.id == payload.book_id).with_for_update().first()
    if not book:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Книга не найдена")
    if book.available_copies <= 0:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Нет доступных экземпляров для выдачи")

    active = (
        db.query(BorrowRecord)
        .filter(
            BorrowRecord.user_id == payload.user_id,
            BorrowRecord.book_id == payload.book_id,
            BorrowRecord.return_date.is_(None),
        )
        .first()
    )
    if active:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="У пользователя уже есть эта книга на руках")

    book.available_copies -= 1
    record = BorrowRecord(user_id=payload.user_id, book_id=payload.book_id)
    db.add(record)
    _commit_or_conflict(db, "Не удалось оформить выдачу")
    db.refresh(record)
    return record


@router.post("/borrows/{borrow_id}/return", response_model=BorrowRead, tags=["borrows"])
def return_book(
    borrow_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> BorrowRecord:
    """Возвращает книгу. Доступно администратору или владельцу выдачи."""
    record = db.query(BorrowRecord).filter(BorrowRecord.id == borrow_id).with_for_update().first()
    if not record:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Запись о выдаче не найдена")
    if not current_user.is_admin and record.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Можно вернуть только свою книгу")
    if record.return_date is not None:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Книга уже возвращена")

    record.return_date = date.today()
    book = db.query(Book).filter(Book.id == record.book_id).first()
    if book:
        book.available_copies += 1

    _commit_or_conflict(db, "Не удалось оформить возврат")
    db.refresh(record)
    return record


@router.get("/borrows", response_model=list[BorrowRead], tags=["borrows"])
def list_borrows(
    skip: int = 0,
    limit: int = 10,
    db: Session = Depends(get_db),
    _admin: User = Depends(get_current_admin),
) -> list[BorrowRecord]:
    return db.query(BorrowRecord).offset(skip).limit(limit).all()


@router.get("/borrows/me", response_model=list[BorrowRead], tags=["borrows"])
def list_my_borrows(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[BorrowRecord]:
    return db.query(BorrowRecord).filter(BorrowRecord.user_id == current_user.id).all()
