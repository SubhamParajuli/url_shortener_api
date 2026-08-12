import os

from fastapi import FastAPI
from app.routers.urls import router as url_router

app=FastAPI(
    title="URL Shortener",
    version="1.0.0",
)

@app.get("/")
def root():
    return {
        "message": "URL Shortener API",
    }

@app.get("/health")
def health():
    return {
        "status": "ok",
    }


app.include_router(url_router)