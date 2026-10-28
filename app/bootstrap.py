"""Проверка базы до создания движка SQLAlchemy.

Хостинг будит контейнер на первом запросе и ждёт, пока процесс откроет порт.
Если в этот момент ждать недоступный PostgreSQL, порт не открывается, и
посетитель видит бесконечное «запускается» или страницу Not Found.
"""

import logging
import os
import sys
from concurrent.futures import ThreadPoolExecutor

logger = logging.getLogger(__name__)

FALLBACK_DATABASE_URL = "sqlite:///./library.db"


def _can_connect(url: str) -> bool:
    from sqlalchemy import create_engine, text

    engine = create_engine(url, pool_pre_ping=True, connect_args={"connect_timeout": 5})
    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
        return True
    finally:
        engine.dispose()


def _probing_enabled() -> bool:
    """В тестах сеть не трогаем: фикстуры подменяют сессию своей базой в памяти."""
    return "pytest" not in sys.modules


def prepare_database_url() -> None:
    """Оставляет рабочий URL. Если PostgreSQL не отвечает, переключается на SQLite."""
    if not _probing_enabled():
        return

    from .config import get_settings

    url = get_settings().database_url
    if url.startswith("sqlite"):
        return

    pool = ThreadPoolExecutor(max_workers=1, thread_name_prefix="db-probe")
    future = pool.submit(_can_connect, url)
    reachable = False
    error_name = "connection failed"
    try:
        reachable = future.result(timeout=12)
    except Exception as exc:
        error_name = type(exc).__name__
    finally:
        pool.shutdown(wait=False, cancel_futures=True)

    if reachable:
        return

    logger.warning(
        "PostgreSQL is unreachable (%s). The API will use a local SQLite database.",
        error_name,
    )
    os.environ["DATABASE_URL"] = FALLBACK_DATABASE_URL
    get_settings.cache_clear()
