"""
this file define all api routes related to url shorten feature.
actual logic is not here, it call service layer function (url_service.py).
"""
from fastapi import APIRouter,Depends,HTTPException
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas import URLCreate,URLResponse
from app.services.url_service import (get_original_url,shorten_url,delete_short_url)
router=APIRouter()

@router.post(
    "/shorten",
    response_model=URLResponse
)
def create_short_url(request:URLCreate,db:Session=Depends(get_db)):
    """
    POST /shorten -> take a long url in body, call service to make short code
    and give back the short_code + full short url to user.
    """
    url=shorten_url(db=db,original_url=str(request.url))

    return URLResponse(
        short_code=url.short_code,
        short_url=f"http://localhost:8000/{url.short_code}"
    )


@router.get("/{short_code}")
def redirect_to_original(short_code:str,db:Session=Depends(get_db)):
    """
    GET /{short_code} -> this is the actual redirect route.
    user hit short link in browser, it find real url and send 302 redirect
    to it. if short_code not found in db/cache then give 404 error.
    """
    original_url=get_original_url(
        db=db,
        short_code=short_code
    )
    if original_url is None:
        raise HTTPException(
            status_code=404,
            detail="URL not found"
        )
    return RedirectResponse(
        url=original_url,
        status_code=302
    )

@router.delete("/{short_code}")
def delete_short_url_endpoint(
    short_code:str,
    db:Session=Depends(get_db)
):
    """
    DELETE /{short_code} -> remove the short url mapping (db + cache both).
    404 if that short code was not there.
    """
    deleted=delete_short_url(db=db,short_code=short_code)
    if not deleted:
        raise HTTPException(
            status_code=404,
            detail="URL not found"
        )
    return{
        "message":"URL deleted"
    }
