# app/db/session.py
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

from app.core.config import settings

SQLALCHEMY_DATABASE_URL = settings.DATABASE_URL

engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# ORM Base for your models
Base = declarative_base()


def init_db() -> None:
    """
    Create DB tables for all models that inherit from Base.
    Import models INSIDE this function so SQLAlchemy knows them
    before metadata.create_all() runs (avoids circular imports).
    """
    # import all model modules that define tables
    from app.models import user  # noqa: F401  (add others as you create them)
    # e.g. from app.models import engine_models  # noqa: F401

    Base.metadata.create_all(bind=engine)