"""
main entry file, fastapi app start from here.
this file just create the app object and put all route together,
actual short-url logic is living in other files (routers/services).
"""
import os

from fastapi import FastAPI
from app.routers.urls import router as url_router
from app.cache_metrics import cache_metrics

app=FastAPI(
    title="URL Shortener",
    version="1.0.0",
)

@app.get("/")
def root():
    """
    just base route, if hit "/" it give simple msg,
    use for check server is up or not.
    """
    return {
        "message": "URL Shortener API",
    }


@app.get("/health")
def health():
    """
    health check route, docker/k8s use this to know app alive or dead.
    """
    return {
        "status": "ok",
    }

@app.get("/instance")
def get_instance():
    """
    this route tell which instance is running
    (useful when many container running behind lb).
    it read INSTANCE_NAME from env, if not set then show "unknown".
    """
    return{
        "instance":os.getenv("INSTANCE_NAME","unknown")
    }

@app.get("/metrics/cache")
def cache_metrics_endpoint():
    """
    route to see cache hit/miss numbers, pull data from cache_metrics object.
    """
    return {
        "hits":cache_metrics.hits,
        "misses":cache_metrics.misses,
        "hit_rate":cache_metrics.hit_rate
    }

# attaching all the url shorten related routes (defined in routers/urls.py) to main app
app.include_router(url_router)
