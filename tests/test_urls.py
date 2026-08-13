"""
test file for the url shorten api, cover both unit test (small function)
and integration test (full request through fastapi + real test db).
"""
from fastapi.testclient import TestClient
from tests.conftest import TestingSessionLocal
from app.main import app
from app.services.url_service import generate_short_code


def test_short_code_length():
    """check generated code have correct length as we asked"""
    code = generate_short_code(6)

    assert len(code) == 6

def test_short_code_characters():
    """check generated code only have letters+digit, no weird symbol"""
    code = generate_short_code(6)

    allowed = set(
        "abcdefghijklmnopqrstuvwxyz"
        "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
        "0123456789"
    )

    assert set(code).issubset(allowed)

def test_health(client):
    """simple check that /health endpoint working n give correct response"""
    response= client.get("/health")

    assert response.status_code==200
    assert response.json()=={
        "status":"ok"
    }

def test_shorten_url(client):
    """
    check that posting a url to /shorten give back proper response
    with short_code n short_url field.
    """
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
    """check that giving bad url (no https://) get rejected with 422 validation error"""
    response = client.post(
        "/shorten",
        json={
            "url": "github.com"
        },
    )

    assert response.status_code == 422

def test_redirect(client):
    """
    full flow test: shorten a url then hit that short code and check
    it redirect (302) to correct original url.
    """
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
    """check requesting a short code which not exist give 404"""
    response = client.get(
        "/doesnotexist"
    )

    assert response.status_code == 404

def test_url_persisted(client):
    """
    Integration Test.
    check after calling /shorten api the row actually got saved in db
    (not just returned in response), query db directly to confirm.
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
