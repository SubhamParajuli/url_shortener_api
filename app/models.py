from datetime import datetime

from sqlalchemy import DateTime, String, Text
from sqlalchemy.orm import Mapped,mapped_column
from .database import Base


class URL(Base):
    __tablename__="urls"

    id:Mapped[int]=mapped_column(
        primary_key=True,
        autoincrement=True
    )

    short_code:Mapped[str]=mapped_column(
        String(10),
        unique=True,
        nullable=False,
        index= True
    )

    original_url:Mapped[str]=mapped_column(
        Text,
        nullable=False
    )

    created_at:Mapped[datetime]=mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False
    )