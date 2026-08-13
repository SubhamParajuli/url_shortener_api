from fastapi.testclient import TestClient
from tests.conftest import TestingSessionLocal
from app.main import app
from app.services.url_service import generate_short_code


def test_short_code_length():
    code = generate_short_code(6)

    assert len(code) == 6

def test_short_code_characters():
    code = generate_short_code(6)

    allowed = set(
        "abcdefghijklmnopqrstuvwxyz"
        "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
        "0123456789"
    )

    assert set(code).issubset(allowed)

def test_health(client):
    response= client.get("/health")

    assert response.status_code==200
    assert response.json()=={
        "status":"ok"
    }

def test_shorten_url(client):
    response=client.post(
        "/shorten",
        json={
            "url": "https://github.com"
        },
    )
    assert response.status_code==200

    data=response.json()
    assert "short_code" in data
    assert "short_url" in data

def test_invalid_url(client):
    response = client.post(
        "/shorten",
        json={
            "url": "github.com"
        },
    )

    assert response.status_code == 422

def test_redirect(client):
    create_response = client.post(
        "/shorten",
        json={
            "url": "https://github.com"
        },
    )

    assert create_response.status_code == 200

    data = create_response.json()

    short_code = data["short_code"]

    redirect_response = client.get(
        f"/{short_code}",
        follow_redirects=False,
    )

    assert redirect_response.status_code == 302

    assert redirect_response.headers["location"] == (
        "https://github.com/"
    )

def test_missing_short_code(client):
    response = client.get(
        "/doesnotexist"
    )

    assert response.status_code == 404

def test_url_persisted(client):
    """
    Integration Test
    """
    response = client.post(
        "/shorten",
        json={
            "url": "https://github.com"
        },
    )

    assert response.status_code == 200

    short_code = response.json()["short_code"]

    db = TestingSessionLocal()

    try:
        from app.repositories.url_repository import (
            get_url_by_short_code,
        )

        url = get_url_by_short_code(
            db,
            short_code,
        )

        assert url is not None
        assert url.original_url == "https://github.com/"

    finally:
        db.close()
