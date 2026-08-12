import os

from fastapi import FastAPI

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