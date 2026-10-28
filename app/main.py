import logging

from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from .crud import router

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
logger = logging.getLogger(__name__)

# Таблицы создаются миграциями Alembic (alembic upgrade head), а не create_all.
app = FastAPI(
    title="LibraryApi",
    version="1.0.0",
    description="REST API библиотеки: книги, авторы, пользователи и учёт выдачи книг.",
)


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc: RequestValidationError) -> JSONResponse:
    logger.warning("Ошибка валидации: %s", exc.errors())
    return JSONResponse(status_code=422, content={"detail": exc.errors()})


@app.get("/health", tags=["service"])
def health() -> dict:
    return {"status": "ok"}


app.include_router(router)

# Запуск: uvicorn app.main:app --reload

