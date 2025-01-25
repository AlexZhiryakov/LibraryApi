from fastapi import APIRouter, Depends, HTTPException, status, Body
from sqlalchemy.orm import Session, joinedload
from passlib.context import CryptContext
from .models import Book, Author, User
from .schemas import BookCreate, UserCreate, Token, AuthorCreate
from .database import get_db
from .auth import create_access_token, create_user, verify_password, get_user_by_username
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from datetime import datetime
from dotenv import load_dotenv
import os

# Загружаем переменную окружения
load_dotenv()

# Получаем URL базы данных
SECRET_KEY = os.getenv("SECRET_KEY")
if not SECRET_KEY:
    raise ValueError("Переменная окружения SECRET_KEY не установлена.")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Конфигурация для JWT
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

router = APIRouter()


# Команда для запуска приложения: uvicorn app.main:app --reload

# Данные для входа в роль админа:
# {
#     "username": "alexZhiryakov",
#     "password": "password"
# }


def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    try:
        # Расшифровываем токен
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")  # Получаем имя пользователя из токена
        if username is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials",
            )
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
        )

    # Проверяем наличие пользователя в базе данных
    user = db.query(User).filter_by(username=username).first()
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
        )
    return user


def is_admin(
    current_user: User = Depends(get_current_user)
):
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have admin privileges"
        )
    return current_user


# добавить новую книгу
@router.post("/books")
def create_new_book(book: BookCreate, db: Session = Depends(get_db)):
    authors = db.query(Author).filter(Author.id.in_(book.author_ids or [])).all()
    if len(authors) != len(book.author_ids or []):
        raise HTTPException(status_code=400, detail="One or more authors not found")

    # Создание книги
    db_book = Book(
        title=book.title,
        description=book.description,
        publication_date=book.publication_date or datetime.now().date(),  # Текущая дата, если не указана
        genre=book.genre,
        available_copies=book.available_copies,
        authors=authors
    )
    db.add(db_book)
    db.commit()
    db.refresh(db_book)
    return db_book
# Шаблон для добавления новой книги:
# {
#     "title": "Human",
#     "genre": "science",
#     "available_copies": 5,
#     "description": "Anatomy"
# }


# получение всех книг
@router.get("/books")
def list_books(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    books = db.query(Book).options(joinedload(Book.authors)).offset(skip).limit(limit).all()
    return books


# удалить книгу по id
@router.delete("/books/{book_id}")
def delete_book(
    book_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(is_admin)
):
    # Находим книгу по ID
    db_book = db.query(Book).filter(Book.id == book_id).first()
    if not db_book:
        raise HTTPException(status_code=404, detail="Book not found")

    # Удаляем книгу
    db.delete(db_book)
    db.commit()
    return {"detail": "Book deleted"}


# добавить нового автора
@router.post("/authors")
def create_author(author: AuthorCreate, db: Session = Depends(get_db)):
    db_author = Author(
        name=author.name,
        biography=author.biography,
        birth_date=author.birth_date
    )
    db.add(db_author)
    db.commit()
    db.refresh(db_author)
    return db_author
# Шаблон для добавления нового автора:
# {
#     "name": "AlexZhiryakov",
#     "biography": "programmer, from Brn",
#     "birth_date": "2008-12-17"
# }


# просмотр всех авторов
@router.get("/authors")
def list_authors(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    return db.query(Author).offset(skip).limit(limit).all()


# регистрация пользователя
@router.post("/register", response_model=Token)
async def register(user: UserCreate, db: Session = Depends(get_db)):
    try:
        # Проверка на наличие пользователя в бд
        db_user = get_user_by_username(db, user.username)
        if db_user:
            raise HTTPException(status_code=400, detail="Username already registered")

        # Создание пользователя
        db_user = create_user(db, user)
        access_token = create_access_token(data={"sub": db_user.username})
        return {"access_token": access_token, "token_type": "bearer"}

    except Exception as e:
        print(f"Error: {e}")  # Лог ошибки
        raise HTTPException(status_code=500, detail=str(e))
# Шаблон для добавления нового пользователя:
# {
#     "username": "alex",
#     "password": "password"
# }


# получить токен, кинув свои данные, зайти в аккаунт
@router.post("/token", response_model=Token)
def login(user: UserCreate, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.username == user.username).first()
    if not db_user or not verify_password(user.password, db_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
        )
    access_token = create_access_token(data={"sub": db_user.username})
    return {"access_token": access_token, "token_type": "bearer"}
# Шаблон для получения своих данных:
# {
#     "username": "alex",
#     "password": "password"
# }


# просмотр всех пользователей
@router.get("/users")
def list_readers(db: Session = Depends(get_db), current_user: User = Depends(is_admin)):
    return db.query(User).filter(User.is_admin == False).all()


# изменение своих данных
@router.put("/users/me")
def update_my_info(
    user_data: UserCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    current_user.username = user_data.username
    if user_data.password:
        current_user.hashed_password = pwd_context.hash(user_data.password)
    db.commit()
    db.refresh(current_user)
    return current_user


# добавление админа
@router.post("/add_admin")
def add_admin(user: UserCreate = Body(...), db: Session = Depends(get_db), current_user: User = Depends(is_admin)):
    # Проверка на существование пользователя
    db_user = db.query(User).filter(User.username == user.username).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Username already registered")

    # Хеширование пароля
    hashed_password = pwd_context.hash(user.password)

    # Создание нового админа
    admin_user = User(
        username=user.username,
        hashed_password=hashed_password,
        is_admin=True  # Принудительно делаем администратора
    )
    db.add(admin_user)
    db.commit()
    db.refresh(admin_user)
    return {"message": "Admin created successfully", "admin": admin_user.username}
# Шаблон для добавления админа:
# Для начала, нужно ввести в Postman в Headers, в Key: Authorization, в Value: Bearer токен
# {
#     "username": "alex",
#     "password": "password"
# }