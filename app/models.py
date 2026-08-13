"""
this is db model file, define how "urls" table look like in postgres.
"""
from datetime import datetime

from sqlalchemy import DateTime, String, Text
from sqlalchemy.orm import Mapped,mapped_column
from .database import Base


class URL(Base):
    """
    one row = one shortened url.
    """
    __tablename__="urls"

    id:Mapped[int]=mapped_column(
        primary_key=True,
        autoincrement=True
    )
    """auto increase primary key id"""

    short_code:Mapped[str]=mapped_column(
        String(10),
        unique=True,
        nullable=False,
        index= True
    )
    """the short code part (like "aZ3kD9"), must be unique, index true so lookup is fast"""

    original_url:Mapped[str]=mapped_column(
        Text,
        nullable=False
    )
    """the real long url, using Text type cause url can be very long sometime"""

    created_at:Mapped[datetime]=mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False
    )
    """when this record get created, auto fill with current utc time"""
