import string
import secrets

from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.repositories.url_repo import (
    create_url,
    get_url_by_short_code,
)

def generate_short_code(length: int = 6) -> str:
    characters = string.ascii_letters + string.digits

    return "".join(
        secrets.choice(characters)
        for _ in range(length)
    )


def shorten_url(
    db: Session,
    original_url: str,
    max_retries:int=5,
):
    for _ in range(max_retries):
        short_code = generate_short_code()
        try:
            return create_url(
                db=db,
                short_code=short_code,
                original_url=original_url,
            )
        except IntegrityError:
            db.rollback()
    raise RuntimeError(
        "Unable to generate a unique short code."
    )