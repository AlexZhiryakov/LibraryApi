import logging

from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse, RedirectResponse

from .crud import router

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
logger = logging.getLogger(__name__)

# Таблицы создаются миграциями Alembic (alembic upgrade head), а не create_all.
# Документация размещена под /api: на хостинге (Layero) пути /docs, /redoc и
# /openapi.json перехватывает прослойка платформы, и Swagger был недоступен.
app = FastAPI(
    title="LibraryApi",
    version="1.0.0",
    description="REST API библиотеки: книги, авторы, пользователи и учёт выдачи книг.",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json",
)


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc: RequestValidationError) -> JSONResponse:
    logger.warning("Ошибка валидации: %s", exc.errors())
    return JSONResponse(status_code=422, content={"detail": exc.errors()})


@app.get("/", include_in_schema=False)
def root() -> RedirectResponse:
    """Корень приложения ведёт на интерактивную документацию."""
    return RedirectResponse(url="/api/docs")


@app.get("/health", tags=["service"])
def health() -> dict:
    return {"status": "ok"}


@app.get("/api/health", tags=["service"])
def api_health() -> dict:
    """Дубль /health для хостинга, где корневые пути заняты платформой."""
    return health()


app.include_router(router)

# Запуск: uvicorn app.main:app --reload
# Документация: http://127.0.0.1:8000/api/docs

