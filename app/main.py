import logging
import sys
from concurrent.futures import ThreadPoolExecutor
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.exception_handlers import http_exception_handler
from fastapi.exceptions import RequestValidationError
from fastapi.responses import HTMLResponse, JSONResponse
from sqlalchemy.exc import OperationalError
from starlette.exceptions import HTTPException as StarletteHTTPException

from .crud import router
from .pages import render_home, render_not_found

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
logger = logging.getLogger(__name__)

# Таблицы создаются миграциями Alembic (alembic upgrade head), а не create_all.
# Документация размещена под /api: на хостинге (Layero) пути /docs, /redoc и
# /openapi.json перехватывает прослойка платформы, и Swagger был недоступен.


def _run_bounded(step, timeout: float) -> bool:
    """Выполняет шаг старта, но не даёт зависшей базе держать порт закрытым."""
    pool = ThreadPoolExecutor(max_workers=1, thread_name_prefix="startup")
    future = pool.submit(step)
    try:
        future.result(timeout=timeout)
        return True
    except Exception:
        logger.exception("Шаг запуска не завершился за %.0f с", timeout)
        return False
    finally:
        pool.shutdown(wait=False, cancel_futures=True)


def _upgrade_database() -> None:
    from alembic import command
    from alembic.config import Config

    command.upgrade(Config("alembic.ini"), "head")


def _seed_demo() -> None:
    from scripts.seed_demo import apply_demo_data

    created = apply_demo_data()
    logger.info("Демо-каталог: %s", created)


def bring_up_database() -> None:
    if not _run_bounded(_upgrade_database, timeout=25):
        logger.error("Миграции не применились. Сервис поднимется, запросы к базе могут отвечать 503.")
        return
    _run_bounded(_seed_demo, timeout=20)


@asynccontextmanager
async def lifespan(_app: FastAPI):
    if "pytest" not in sys.modules:
        bring_up_database()
    yield


app = FastAPI(
    title="LibraryApi",
    version="1.0.0",
    description="REST API библиотеки: книги, авторы, пользователи и учёт выдачи книг.",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json",
    lifespan=lifespan,
)


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    logger.warning("Ошибка валидации: %s", exc.errors())
    return JSONResponse(status_code=422, content={"detail": exc.errors()})


@app.exception_handler(StarletteHTTPException)
async def not_found_page(request: Request, exc: StarletteHTTPException):
    """Браузеру на неизвестный адрес отдаём страницу, а не голый JSON."""
    accepts_html = "text/html" in request.headers.get("accept", "")
    if exc.status_code == 404 and accepts_html:
        return HTMLResponse(
            render_not_found(request.url.path),
            status_code=404,
            headers={"Cache-Control": "no-store"},
        )
    return await http_exception_handler(request, exc)


@app.exception_handler(OperationalError)
async def database_unavailable(request: Request, exc: OperationalError) -> JSONResponse:
    logger.error("База данных недоступна: %s", type(exc).__name__)
    return JSONResponse(status_code=503, content={"detail": "База данных временно недоступна"})


def _catalog_counts() -> tuple[int | None, int | None, str]:
    from .config import get_settings
    from .database import SessionLocal
    from .models import Author, Book

    database = "SQLite" if get_settings().database_url.startswith("sqlite") else "PostgreSQL"
    session = SessionLocal()
    try:
        return session.query(Book).count(), session.query(Author).count(), database
    except Exception:
        logger.warning("Не удалось прочитать каталог для главной страницы", exc_info=True)
        return None, None, database
    finally:
        session.close()


@app.get("/", include_in_schema=False)
def root() -> HTMLResponse:
    """Главная страница сервиса. Отвечает 200 без обращения к базе в пути ошибки."""
    books, authors, database = _catalog_counts()
    return HTMLResponse(
        render_home(books=books, authors=authors, database=database),
        headers={"Cache-Control": "no-store"},
    )


@app.get("/health", tags=["service"])
def health() -> dict:
    return {"status": "ok"}


@app.get("/api/health", tags=["service"])
def api_health() -> dict:
    """Дубль /health для хостинга, где корневые пути заняты платформой."""
    return health()


app.include_router(router)
