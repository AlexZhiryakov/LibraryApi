from fastapi import FastAPI
from .crud import router
from .database import Base, engine
import logging
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

# Создаем таблицы
Base.metadata.create_all(bind=engine)

# Инициализация приложения
app = FastAPI()

# Логирование ошибок валидации
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc):
    logging.error(f"Ошибка валидации: {exc}")
    return JSONResponse(
        status_code=422,
        content={"detail": exc.errors(), "body": exc.body.decode("utf-8") if isinstance(exc.body, bytes) else exc.body},
    )

# Подключаем роутер
app.include_router(router)

# Запуск: uvicorn app.main:app --reload
