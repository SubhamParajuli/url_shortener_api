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
    pass


def get_db()->Generator[Session,None,None]:
    db=SessionLocal()

    try:
        yield db
    finally:
        db.close()