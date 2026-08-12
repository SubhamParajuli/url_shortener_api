from fastapi import APIRouter,Depends,HTTPException
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session

from app.database import get_db

from app.database import get_db
from app.schema import URLCreate,URLResponse
from app.services.url_service import (get_original_url,shorten_url,delete_short_url)

router=APIRouter()

@router.post(
    "/shorten",
    response_model=URLResponse
)
def create_short_url(request:URLCreate,db:Session=Depends(get_db)):
    url=shorten_url(db=db,original_url=str(request.url))

    return URLResponse(
        short_code=url.short_code,
        short_url=f"http://localhost:8000/{url.short_code}"
    )

@router.get("/{short_code}")
def redirect_to_original(short_code:str,db:Session=Depends(get_db)):
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
    deleted=delete_short_url(db=db,short_code=short_code)
    if not deleted:
        raise HTTPException(
            status_code=404,
            detail="URL not found"
        )
    return{
        "message":"URL deleted"
    }