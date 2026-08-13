"""
this file setup database connection stuff (sqlalchemy engine, session).
"""
import os
from dotenv import load_dotenv
from collections.abc import Generator
from sqlalchemy import create_engine
from sqlalchemy.orm import Session,sessionmaker,DeclarativeBase

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")

engine=create_engine(
    DATABASE_URL,
    pool_pre_ping=True
)

SessionLocal=sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False,
)



class Base(DeclarativeBase):
    """
    base class, all model (like URL model) inherit from this so
    sqlalchemy know about them.
    """
    pass


def get_db()->Generator[Session,None,None]:
    """
    dependency function for fastapi, open db session, give it to
    route, then close it after request done (even if error happen,
    finally block handle that).
    """
    db=SessionLocal()

    try:
        yield db
    finally:
        db.close()
