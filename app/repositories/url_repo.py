from sqlalchemy import select
from sqlalchemy.orm import Session
from app.models import URL


def create_url(db:Session,short_code:str,original_url:str)-> URL:
    url=URL(
        short_code=short_code,
        original_url=original_url
    )
    db.add(url)
    db.commit()
    db.refresh(url)

    return url

def get_url_by_short_code(db:Session,
                          short_code:str)->URL | None:
    statement=select(URL).where(
        URL.short_code==short_code
    )
    return db.scalar(statement)
