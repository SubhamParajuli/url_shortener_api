"""
repository layer, this is only place where we talk directly with db
(raw db operation). service layer call these function, dont put
business logic here, just db stuff.
"""
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.models import URL

def create_url(db:Session,short_code:str,original_url:str)-> URL:
    """
    insert new url row in db, commit n refresh so we get back
    the id/created_at also.
    """
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
    """
    find one row where short_code match, return None if nothing found.
    """
    statement=select(URL).where(
        URL.short_code==short_code
    )
    return db.scalar(statement)

def delete_url(db:Session,short_code:str)->None:
    """
    delete given row from db. note: param name says short_code but
    actually caller is passing whole URL object here (see
    url_service.py delete_short_url), db.delete() need the model
    instance not the string, so keep that in mind.
    """
    db.delete(short_code)
    db.commit()
