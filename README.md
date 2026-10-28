# LibraryApi

REST API библиотеки на FastAPI: книги, авторы, читатели и учёт выдачи книг.

![CI](https://github.com/AlexZhiryakov/LibraryApi/actions/workflows/ci.yml/badge.svg)
![Python](https://img.shields.io/badge/python-3.11-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-0.115-009688)

## 🔗 Живое демо

- API: https://libraryapi-main.layero.app
- Документация (Swagger UI): https://libraryapi-main.layero.app/api/docs

```bash
curl https://libraryapi-main.layero.app/api/health   # {"status":"ok"}
```

## 📖 О проекте

Пет-проект для портфолио: REST API библиотеки на FastAPI, доведённый до
прод-структуры — от миграций и тестов до Docker и CI. Реализованы
JWT-аутентификация с ролевой моделью (читатель и администратор), учёт выдачи и
возврата книг, а также связь «книга ↔ авторы» (many-to-many). Проект показывает,
как собрать небольшое, но аккуратное backend-приложение: конфигурация через
переменные окружения, миграции Alembic, обработка ошибок БД и деплой одной
командой.

## 🛠 Стек технологий

- **Python 3.11** — язык проекта.
- **FastAPI** — веб-фреймворк: маршруты, зависимости, автодокументация.
- **Uvicorn** — ASGI-сервер для запуска приложения.
- **SQLAlchemy 2.0** — ORM: модели и запросы к БД.
- **PostgreSQL** — основная БД; **SQLite** — для локального старта и тестов.
- **Pydantic 2 + pydantic-settings** — валидация схем и конфигурация из окружения.
- **python-jose** — подпись и проверка JWT.
- **passlib + bcrypt** — безопасное хеширование паролей.
- **Alembic** — миграции схемы БД.
- **pytest + httpx** — тесты API через TestClient.
- **ruff** — линтер и сортировка импортов.
- **Docker + docker compose** — упаковка и локальный запуск с PostgreSQL.
- **GitHub Actions** — CI: линт и тесты на каждый push.

## 🚀 Функционал

- Регистрация обычного пользователя и вход по JWT (пароли — bcrypt-хеши).
- Ролевая модель: создание книг, авторов, администраторов и выдача книг доступны
  только администратору.
- Книги: создание, список с пагинацией (`skip`/`limit`), удаление.
- Авторы: создание и список; связь «книга ↔ авторы» (many-to-many).
- Пользователи: изменение своего профиля (`PUT /users/me`), список читателей,
  создание администраторов.
- Учёт выдачи: выдать книгу читателю, вернуть книгу, списки выдач (свои и все).
- Контроль доступности: нельзя выдать книгу без свободных экземпляров и нельзя
  удалить книгу с активными выдачами.
- Миграции Alembic вместо `create_all`; конфликты БД отдаются как `409`.

## 📡 Эндпоинты

| Метод  | Путь                          | Доступ         | Описание                       |
|--------|-------------------------------|----------------|--------------------------------|
| GET    | `/health`                     | публичный      | проверка живости сервиса       |
| GET    | `/api/health`                 | публичный      | то же для хостинга (Layero)    |
| POST   | `/register`                   | публичный      | регистрация читателя           |
| POST   | `/token`                      | публичный      | вход, выдача JWT               |
| GET    | `/books`                      | публичный      | список книг (skip/limit)       |
| POST   | `/books`                      | админ          | создать книгу                  |
| DELETE | `/books/{book_id}`            | админ          | удалить книгу                  |
| GET    | `/authors`                    | публичный      | список авторов                 |
| POST   | `/authors`                    | админ          | создать автора                 |
| GET    | `/users`                      | админ          | список читателей               |
| PUT    | `/users/me`                   | авторизованный | изменить свои данные           |
| POST   | `/add_admin`                  | админ          | создать администратора         |
| POST   | `/borrows`                    | админ          | выдать книгу читателю          |
| POST   | `/borrows/{borrow_id}/return` | авторизованный | вернуть книгу (админ/владелец) |
| GET    | `/borrows`                    | админ          | все выдачи                     |
| GET    | `/borrows/me`                 | авторизованный | свои выдачи                    |

Интерактивная документация: `/api/docs` (Swagger UI) и `/api/redoc`; корень `/`
редиректит на `/api/docs`. Префикс `/api` нужен потому, что пути `/docs`, `/redoc`
и `/health` на хостинге Layero перехватывает прослойка платформы.

## 🔐 Безопасность

- Пароли хранятся только в виде bcrypt-хешей.
- Роль `is_admin` не принимается от клиента при регистрации: администраторы
  создаются лишь действующим админом через `POST /add_admin`.
- Пишущие эндпоинты книг, авторов и выдач защищены правами администратора;
  вернуть книгу может администратор или владелец выдачи.
- Ошибки целостности БД возвращаются как `409` без раскрытия текста исключения.
- Все секреты (`SECRET_KEY`, `DATABASE_URL`) задаются переменными окружения и
  не хранятся в коде.

## 🧪 Тесты и качество

- `pytest` — тесты API на SQLite в памяти (внешняя БД не нужна).
- `ruff check .` — линтер и проверка порядка импортов.
- CI в GitHub Actions: на каждый push и pull request запускаются линт и тесты.

```powershell
pip install -r requirements-dev.txt
ruff check .
pytest
```

## ▶️ Быстрый старт

### Локально

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env      # затем отредактируйте .env
alembic upgrade head             # создать таблицы
uvicorn app.main:app --reload    # http://127.0.0.1:8000/api/docs
```

Демо-данные (админ `demo_admin`, читатель `demo_user`, авторы и книги):

```powershell
$env:DEMO_ADMIN_PASSWORD = "<пароль админа>"
$env:DEMO_USER_PASSWORD = "<пароль читателя>"
python -m scripts.seed_demo      # скрипт идемпотентен
```

### Через Docker Compose

```powershell
docker compose up --build
# API: http://localhost:8000  (миграции применяются при старте контейнера)
```

## ☁️ Деплой на Layero + Neon

1. **База в Neon.** Зарегистрируйтесь на [neon.tech](https://neon.tech), создайте
   проект и скопируйте строку подключения вида
   `postgresql://user:password@host/db?sslmode=require` (Dashboard →
   **Connection string**). Приложение понимает и вариант `postgres://`.
2. **Сервис в Layero.** Создайте сервис из репозитория — конфигурация берётся из
   `layero.json`: установка `pip install -r requirements.txt`, запуск `sh start.sh`.
   Скрипт `start.sh` применяет миграции (`alembic upgrade head`) и поднимает
   uvicorn на порту из переменной `PORT` (по умолчанию `8000`).
3. **Переменные окружения.** Задайте их в панели Layero (секреты храните только в
   хостинге; локальный пример — в `.env.layero`, этот файл не коммитится):

   | Переменная            | Назначение                          |
   |-----------------------|-------------------------------------|
   | `DATABASE_URL`        | строка подключения из Neon          |
   | `SECRET_KEY`          | длинная случайная строка для JWT    |
   | `DEMO_ADMIN_PASSWORD` | пароль `demo_admin` для seed        |
   | `DEMO_USER_PASSWORD`  | пароль `demo_user` для seed         |

4. **Демо-данные.** После первого деплоя наполните базу книгами и авторами —
   команда идемпотентна, повторный запуск не создаёт дубликатов:

   ```powershell
   python -m scripts.seed_demo
   ```

   Логины: администратор `demo_admin`, читатель `demo_user`.

> Демо: https://libraryapi-main.layero.app/api/docs

## ⚙️ Переменные окружения

| Переменная                    | Назначение                          | По умолчанию             |
|-------------------------------|-------------------------------------|--------------------------|
| `DATABASE_URL`                | строка подключения к БД             | `sqlite:///./library.db` |
| `SECRET_KEY`                  | ключ подписи JWT (сменить в проде)  | небезопасный dev-ключ    |
| `ALGORITHM`                   | алгоритм подписи JWT                | `HS256`                  |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | срок жизни access-токена (мин)      | `30`                     |
| `PORT`                        | порт uvicorn внутри контейнера      | `8000`                   |
| `DEMO_ADMIN_PASSWORD`         | пароль `demo_admin` для seed-скрипта | —                       |
| `DEMO_USER_PASSWORD`          | пароль `demo_user` для seed-скрипта  | —                       |

Пустые значения переменных окружения игнорируются — берётся значение по умолчанию.
Это защищает запуск от падений, если переменную в панели хостинга оставили пустой.

## 📁 Структура проекта

```
LibraryApi/
├── app/
│   ├── main.py         # FastAPI, обработчик ошибок, /health
│   ├── config.py       # настройки из окружения (pydantic-settings)
│   ├── database.py     # движок, сессия, get_db
│   ├── models.py       # ORM-модели (Book, Author, User, BorrowRecord)
│   ├── schemas.py      # Pydantic-схемы запросов и ответов
│   ├── security.py     # bcrypt и JWT
│   ├── auth.py         # зависимости get_current_user / get_current_admin
│   └── crud.py         # HTTP-эндпоинты
├── alembic/            # миграции
├── scripts/
│   └── seed_demo.py    # идемпотентное наполнение демо-данными
├── tests/
│   ├── conftest.py     # фикстуры, SQLite в памяти
│   ├── test_api.py     # тесты API
│   └── test_config.py  # тесты настроек (пустые переменные окружения)
├── .github/workflows/ci.yml
├── Dockerfile
├── docker-compose.yml
├── render.yaml         # Blueprint для деплоя на Render
├── layero.json         # конфигурация деплоя на Layero
├── start.sh            # запуск на хостинге: миграции + uvicorn на $PORT
├── pyproject.toml      # настройки ruff и pytest
├── requirements.txt
├── requirements-dev.txt
└── .env.example
```

## 🧭 Что можно улучшить дальше

- Добавить измерение покрытия тестами (`pytest-cov`) и больше негативных сценариев.
- Реализовать refresh-токены и отзыв JWT.
- Добавить поиск и фильтры по книгам, пагинацию для авторов и выдач.
- Проверять миграции в CI (`alembic check`) и деплоить по тегу.
