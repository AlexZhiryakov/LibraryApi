from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

from .bootstrap import prepare_database_url

# Сначала решаем, к какой базе реально подключаться, и только потом создаём движок.
# create_engine сам соединение не открывает, но URL уже должен быть рабочим.
prepare_database_url()

from .config import get_settings  # noqa: E402

settings = get_settings()

engine_kwargs: dict = {"pool_pre_ping": True}
if settings.database_url.startswith("sqlite"):
    engine_kwargs["connect_args"] = {"check_same_thread": False}
elif settings.database_url.startswith("postgres"):
    engine_kwargs["connect_args"] = {"connect_timeout": 8}

engine = create_engine(settings.database_url, **engine_kwargs)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
