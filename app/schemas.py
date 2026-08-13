"""
pydantic schema file, this is for request/response body validation.
"""
from pydantic import BaseModel,HttpUrl

class URLCreate(BaseModel):
    """
    schema for incoming request when user want to shorten a url.
    HttpUrl type auto check the string is valid url or not
    (that why invalid url give 422 error).
    """
    url:HttpUrl

class URLResponse(BaseModel):
    """
    schema for what we send back after shorten success.
    short_code is just the code part, short_url is full link with domain.
    """
    short_code:str
    short_url:str
