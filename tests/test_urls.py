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