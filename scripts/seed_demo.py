"""Наполнение базы демонстрационными данными.

Скрипт создаёт администратора ``demo_admin`` и обычного пользователя
``demo_user``, а также несколько авторов и книг с реальными названиями.

Пароли демо-пользователей берутся ТОЛЬКО из переменных окружения
``DEMO_ADMIN_PASSWORD`` и ``DEMO_USER_PASSWORD`` — в коде они не хранятся.

Скрипт идемпотентен: повторный запуск не создаёт дубликатов. Уже существующие
записи (пользователь по username, автор по имени, книга по названию)
пропускаются.

Запуск из корня проекта::

    python -m scripts.seed_demo
"""

from __future__ import annotations

import os
import sys
from datetime import date
from pathlib import Path

# Делаем пакет app импортируемым при запуске скрипта из корня проекта.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.database import SessionLocal  # noqa: E402
from app.models import Author, Book, User  # noqa: E402
from app.security import hash_password  # noqa: E402

ADMIN_USERNAME = "demo_admin"
USER_USERNAME = "demo_user"

AUTHORS: list[dict] = [
    {
        "name": "Лев Толстой",
        "biography": "Русский писатель, автор романов «Война и мир» и «Анна Каренина».",
        "birth_date": date(1828, 9, 9),
    },
    {
        "name": "Фёдор Достоевский",
        "biography": "Русский писатель и мыслитель, мастер психологического романа.",
        "birth_date": date(1821, 11, 11),
    },
    {
        "name": "Михаил Булгаков",
        "biography": "Русский писатель, автор романа «Мастер и Маргарита».",
        "birth_date": date(1891, 5, 15),
    },
    {
        "name": "Александр Пушкин",
        "biography": "Русский поэт и прозаик, основоположник современного литературного языка.",
        "birth_date": date(1799, 6, 6),
    },
    {
        "name": "Джордж Оруэлл",
        "biography": "Британский писатель и публицист, автор антиутопий «1984» и «Скотный двор».",
        "birth_date": date(1903, 6, 25),
    },
    {
        "name": "Эрих Мария Ремарк",
        "biography": "Немецкий писатель, автор романов о «потерянном поколении».",
        "birth_date": date(1898, 6, 22),
    },
]

BOOKS: list[dict] = [
    {
        "title": "Война и мир",
        "description": "Роман-эпопея о России эпохи войн с Наполеоном.",
        "publication_date": date(1869, 1, 1),
        "genre": "Роман-эпопея",
        "available_copies": 3,
        "authors": ["Лев Толстой"],
    },
    {
        "title": "Анна Каренина",
        "description": "Роман о судьбе Анны Карениной и жизни русского общества.",
        "publication_date": date(1877, 1, 1),
        "genre": "Роман",
        "available_copies": 2,
        "authors": ["Лев Толстой"],
    },
    {
        "title": "Преступление и наказание",
        "description": "История бывшего студента Раскольникова и его внутренней борьбы.",
        "publication_date": date(1866, 1, 1),
        "genre": "Роман",
        "available_copies": 2,
        "authors": ["Фёдор Достоевский"],
    },
    {
        "title": "Идиот",
        "description": "Роман о князе Мышкине и столкновении добра с жестоким миром.",
        "publication_date": date(1869, 1, 1),
        "genre": "Роман",
        "available_copies": 1,
        "authors": ["Фёдор Достоевский"],
    },
    {
        "title": "Мастер и Маргарита",
        "description": "Роман о визите дьявола в Москву 1930-х годов.",
        "publication_date": date(1967, 1, 1),
        "genre": "Роман",
        "available_copies": 2,
        "authors": ["Михаил Булгаков"],
    },
    {
        "title": "Собачье сердце",
        "description": "Повесть о профессоре Преображенском и его эксперименте.",
        "publication_date": date(1925, 1, 1),
        "genre": "Повесть",
        "available_copies": 4,
        "authors": ["Михаил Булгаков"],
    },
    {
        "title": "Евгений Онегин",
        "description": "Роман в стихах о судьбе Евгения Онегина и Татьяны Лариной.",
        "publication_date": date(1833, 1, 1),
        "genre": "Роман в стихах",
        "available_copies": 3,
        "authors": ["Александр Пушкин"],
    },
    {
        "title": "Капитанская дочка",
        "description": "Историческая повесть о восстании Пугачёва.",
        "publication_date": date(1836, 1, 1),
        "genre": "Повесть",
        "available_copies": 2,
        "authors": ["Александр Пушкин"],
    },
    {
        "title": "1984",
        "description": "Антиутопия о тотальном контроле и жизни Уинстона Смита.",
        "publication_date": date(1949, 6, 8),
        "genre": "Антиутопия",
        "available_copies": 2,
        "authors": ["Джордж Оруэлл"],
    },
    {
        "title": "Скотный двор",
        "description": "Сатирическая повесть-притча о восстании животных на ферме.",
        "publication_date": date(1945, 8, 17),
        "genre": "Антиутопия",
        "available_copies": 3,
        "authors": ["Джордж Оруэлл"],
    },
    {
        "title": "Три товарища",
        "description": "Роман о дружбе и любви в Германии после Первой мировой войны.",
        "publication_date": date(1936, 1, 1),
        "genre": "Роман",
        "available_copies": 2,
        "authors": ["Эрих Мария Ремарк"],
    },
    {
        "title": "Триумфальная арка",
        "description": "Роман о хирурге-эмигранте Равике в предвоенном Париже.",
        "publication_date": date(1945, 1, 1),
        "genre": "Роман",
        "available_copies": 1,
        "authors": ["Эрих Мария Ремарк"],
    },
]


def _get_or_create_user(db, username: str, password: str, is_admin: bool) -> tuple[User, bool]:
    """Возвращает пользователя и признак того, что он создан именно сейчас."""
    user = db.query(User).filter(User.username == username).first()
    if user is not None:
        return user, False
    user = User(username=username, hashed_password=hash_password(password), is_admin=is_admin)
    db.add(user)
    return user, True


def apply_demo_data() -> dict[str, int]:
    """Создаёт демо-каталог. Пользователей — только если заданы пароли в окружении.

    Идемпотентно: повторный вызов не плодит дубликаты. Пароли в коде не хранятся,
    поэтому без ``DEMO_ADMIN_PASSWORD`` и ``DEMO_USER_PASSWORD`` появляются
    только авторы и книги.
    """
    admin_password = os.getenv("DEMO_ADMIN_PASSWORD")
    user_password = os.getenv("DEMO_USER_PASSWORD")

    db = SessionLocal()
    try:
        created_users = 0
        if admin_password and user_password:
            for username, password, is_admin in (
                (ADMIN_USERNAME, admin_password, True),
                (USER_USERNAME, user_password, False),
            ):
                _, created = _get_or_create_user(db, username, password, is_admin)
                created_users += int(created)

        authors_by_name: dict[str, Author] = {}
        created_authors = 0
        for data in AUTHORS:
            author = db.query(Author).filter(Author.name == data["name"]).first()
            if author is None:
                author = Author(**data)
                db.add(author)
                db.flush()
                created_authors += 1
            authors_by_name[data["name"]] = author

        created_books = 0
        for data in BOOKS:
            if db.query(Book).filter(Book.title == data["title"]).first() is not None:
                continue
            book = Book(
                title=data["title"],
                description=data["description"],
                publication_date=data["publication_date"],
                genre=data["genre"],
                available_copies=data["available_copies"],
                authors=[authors_by_name[name] for name in data["authors"]],
            )
            db.add(book)
            created_books += 1

        db.commit()
        return {"users": created_users, "authors": created_authors, "books": created_books}
    finally:
        db.close()


def seed() -> None:
    """Создаёт демо-данные из командной строки. Безопасно вызывать повторно."""
    if not os.getenv("DEMO_ADMIN_PASSWORD") or not os.getenv("DEMO_USER_PASSWORD"):
        print(
            "Не заданы переменные окружения DEMO_ADMIN_PASSWORD и/или DEMO_USER_PASSWORD.",
            file=sys.stderr,
        )
        print(
            "Задайте их перед запуском, например: $env:DEMO_ADMIN_PASSWORD = '<пароль>'",
            file=sys.stderr,
        )
        raise SystemExit(1)

    created = apply_demo_data()
    print("Демо-данные готовы.")
    print(f"  пользователи: создано {created['users']} из 2")
    print(f"  авторы:       создано {created['authors']} из {len(AUTHORS)}")
    print(f"  книги:        создано {created['books']} из {len(BOOKS)}")
    print(f"  админ: {ADMIN_USERNAME}, читатель: {USER_USERNAME} (пароли — из переменных окружения)")


if __name__ == "__main__":
    seed()
