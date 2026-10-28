# LibraryApi — книги, авторы и выдача

REST API библиотеки на FastAPI: каталог книг и авторов, регистрация читателей и учёт выдачи.

![CI](https://github.com/AlexZhiryakov/LibraryApi/actions/workflows/ci.yml/badge.svg)
![Python](https://img.shields.io/badge/python-3.11-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-0.115-009688)

## 🔗 Живое демо

- Сайт: https://libraryapi-main.layero.app
- Документация: https://libraryapi-main.layero.app/api/docs

## 📖 О проекте

Небольшое демо-приложение: главная страница показывает, сколько книг и авторов в каталоге, а Swagger даёт попробовать запросы прямо в браузере. Книги и авторов можно читать без входа. Создавать записи, выдавать книги и заводить администраторов может только администратор.

Проект показывает REST API с ролями, JWT, связью «книга — авторы» и миграциями базы. Пароли в базе хранятся только как хеши.

## 🛠 Стек технологий

- **Python 3.11** — язык проекта.
- **FastAPI** — веб-фреймворк: маршруты, проверка данных, страница документации.
- **Uvicorn** — ASGI-сервер для запуска приложения.
- **SQLAlchemy 2** — модели и запросы к базе.
- **PostgreSQL** — основная база; **SQLite** — для локального запуска и тестов.
- **Alembic** — миграции схемы базы.
- **Pydantic** — схемы запросов и ответов.
- **JWT (python-jose)** — вход и проверка токена.
- **passlib + bcrypt** — хеширование паролей.
- **pytest + httpx** — тесты API.
- **ruff** — линтер и сортировка импортов.
- **Docker** — запуск вместе с PostgreSQL.
- **GitHub Actions** — линт и тесты на каждый push.

## 🚀 Как пользоваться сайтом

1. Откройте [живое демо](https://libraryapi-main.layero.app).
2. На главной видно размер каталога и ссылки на документацию, список книг и список авторов.
3. Нажмите **Открыть Swagger**, чтобы посмотреть и вызвать запросы. Документация живёт по адресу `/api/docs`.
4. Списки книг и авторов открываются без входа: `/books` и `/authors`.
5. Чтобы отправить запрос от своего имени, зарегистрируйтесь через `POST /register` и в Swagger нажмите **Authorize**.
6. Новые книги, авторы и выдача книг доступны администратору.

## ▶️ Быстрый старт

### Локально

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
alembic upgrade head
uvicorn app.main:app --reload
```

Сайт откроется на http://127.0.0.1:8000, документация — на http://127.0.0.1:8000/api/docs.

Демо-каталог (книги, авторы, `demo_admin` и `demo_user`):

```powershell
$env:DEMO_ADMIN_PASSWORD = "<пароль админа>"
$env:DEMO_USER_PASSWORD = "<пароль читателя>"
python -m scripts.seed_demo
```

### Через Docker

```powershell
docker compose up --build
```

API: http://localhost:8000.

## 🧪 Тесты и качество

```powershell
pip install -r requirements-dev.txt
ruff check .
pytest
```

Тесты ходят в API через SQLite в памяти, отдельная база не нужна. На GitHub при каждом push запускаются линтер и тесты.
