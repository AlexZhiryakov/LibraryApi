"""Тесты конфигурации приложения.

Хостинги (Layero, Render) позволяют задавать переменные окружения пустыми
строками. Благодаря ``env_ignore_empty=True`` такие значения игнорируются:
приложение стартует и берёт значения по умолчанию вместо падения при импорте.

Файл ``.env`` в тестах отключён (``_env_file=None``), чтобы результат не
зависел от локальных настроек разработчика.
"""

import pytest

from app.config import Settings

# Переменные, которые могут быть заданы в окружении разработчика или хостинга.
_ENV_NAMES = (
    "DATABASE_URL",
    "SECRET_KEY",
    "ALGORITHM",
    "ACCESS_TOKEN_EXPIRE_MINUTES",
)


@pytest.fixture(autouse=True)
def _clean_environment(monkeypatch):
    """Убирает переменные окружения приложения, чтобы тесты были изолированы."""
    for name in _ENV_NAMES:
        monkeypatch.delenv(name, raising=False)


def test_settings_work_without_any_env_vars():
    """Приложение стартует без переменных окружения: у всех настроек есть дефолты."""
    settings = Settings(_env_file=None)
    assert settings.database_url
    assert settings.secret_key
    assert settings.algorithm == "HS256"
    assert settings.access_token_expire_minutes == 30


def test_empty_access_token_expire_minutes_uses_default(monkeypatch):
    """Пустое ACCESS_TOKEN_EXPIRE_MINUTES не ломает старт: берётся срок по умолчанию."""
    monkeypatch.setenv("ACCESS_TOKEN_EXPIRE_MINUTES", "")
    settings = Settings(_env_file=None)
    assert settings.access_token_expire_minutes == 30


def test_empty_database_url_and_secret_key_use_defaults(monkeypatch):
    """Пустые DATABASE_URL и SECRET_KEY тоже игнорируются, а не роняют контейнер."""
    monkeypatch.setenv("DATABASE_URL", "")
    monkeypatch.setenv("SECRET_KEY", "")
    settings = Settings(_env_file=None)
    assert settings.database_url.startswith("sqlite")
    assert settings.secret_key


def test_unreachable_postgres_falls_back_to_sqlite(monkeypatch):
    """Мёртвый PostgreSQL не должен оставлять процесс без базы: сайт поднимается на SQLite."""
    from app.bootstrap import prepare_database_url
    from app.config import get_settings

    def _offline(_url: str) -> bool:
        raise TimeoutError("slow")

    monkeypatch.setenv("DATABASE_URL", "postgresql://user:pass@127.0.0.1:1/library")
    monkeypatch.setattr("app.bootstrap._probing_enabled", lambda: True)
    monkeypatch.setattr("app.bootstrap._can_connect", _offline)
    get_settings.cache_clear()
    try:
        prepare_database_url()
        get_settings.cache_clear()
        assert get_settings().database_url.startswith("sqlite")
    finally:
        get_settings.cache_clear()


def test_access_token_expire_minutes_is_read_from_environment(monkeypatch):
    """Непустое значение переменной по-прежнему применяется."""
    monkeypatch.setenv("ACCESS_TOKEN_EXPIRE_MINUTES", "45")
    assert Settings(_env_file=None).access_token_expire_minutes == 45
