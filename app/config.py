"""Единая конфигурация приложения.

Все настройки читаются из переменных окружения (файл ``.env`` при локальном
запуске). Секреты в коде не хранятся — см. ``.env.example``.
"""

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # Строка подключения к БД. По умолчанию — локальная SQLite, чтобы проект
    # запускался без внешней инфраструктуры. В продакшене задавайте PostgreSQL
    # через переменную окружения DATABASE_URL.
    database_url: str = "sqlite:///./library.db"

    # ВНИМАНИЕ: значение по умолчанию небезопасно и предназначено только для
    # разработки. В продакшене обязательно переопределите SECRET_KEY.
    secret_key: str = "dev-insecure-secret-key-change-me"

    # Алгоритм подписи JWT.
    algorithm: str = "HS256"

    # Время жизни access-токена в минутах.
    access_token_expire_minutes: int = 30


@lru_cache
def get_settings() -> Settings:
    return Settings()
