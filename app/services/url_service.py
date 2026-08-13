import string
import secrets

from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from app.redis_client import redis_client
from app.cache_metrics import cache_metrics
from redis.exceptions import RedisError
from app.repositories.url_repository import (
    create_url,
    get_url_by_short_code,
    delete_url
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

def get_original_url(
    db: Session,
    short_code: str,
):
    cache_key=f"url:{short_code}"

    try:
        cached_url=redis_client.get(cache_key)

        if cached_url:
            cache_metrics.hits += 1
            return cached_url
        cache_metrics.misses +=1
    except RedisError:
        pass
    
    url= get_url_by_short_code(
        db=db,
        short_code=short_code,
    )
    if url is None:
        return None
    try:
        redis_client.set(
            cache_key,
            url.original_url,ex=3000
        )
    except RedisError:
        cache_metrics.misses += 1
        
    return url.original_url


def delete_short_url(db:Session,short_code:str)->bool:
    url=get_url_by_short_code(
        db=db,
        short_code=short_code
    )
    if url is None:
        return False 

    delete_url(
        db=db,
        short_code=url
    )
    try:
        redis_client.delete(
            f"url:{short_code}"
        )
    except RedisError:
        pass

    return True