"""Точка входа на хостинге.

Слушает ``0.0.0.0`` и порт из ``PORT``. Миграции выполняются в lifespan
приложения и не блокируют открытие порта дольше заданного таймаута.
"""

import os

import uvicorn


def _port() -> int:
    raw = os.environ.get("PORT", "").strip()
    if not raw:
        return 8000
    return int(raw)


def main() -> None:
    uvicorn.run("app.main:app", host="0.0.0.0", port=_port(), log_level="info")


if __name__ == "__main__":
    main()
