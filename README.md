# LibraryApi

REST API библиотеки: книги, авторы, читатели и учёт выдачи.

![CI](https://github.com/AlexZhiryakov/LibraryApi/actions/workflows/ci.yml/badge.svg)
![Python](https://img.shields.io/badge/python-3.11-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-0.115-009688)

## Демо

- Сайт: https://libraryapi-main.layero.app
- Документация: https://libraryapi-main.layero.app/api/docs

## Стек

Python 3.11, FastAPI, SQLAlchemy, PostgreSQL, Alembic, Pydantic, JWT, Docker, pytest.

## Возможности

- Регистрация и вход по JWT. Пароли хранятся как bcrypt-хеши.
- Две роли: читатель и администратор.
- Книги и авторы, связь «многие ко многим».
- Выдача и возврат книг, список своих выдач.

Полный список запросов — в Swagger: `/api/docs`.

## Запуск

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
alembic upgrade head
uvicorn app.main:app --reload
```

Откройте http://127.0.0.1:8000/api/docs.

Через Docker: `docker compose up --build`, API на http://localhost:8000.

Демо-книги и пользователей можно добавить так:

```powershell
$env:DEMO_ADMIN_PASSWORD = "<пароль админа>"
$env:DEMO_USER_PASSWORD = "<пароль читателя>"
python -m scripts.seed_demo
```

Логины: `demo_admin` и `demo_user`.
