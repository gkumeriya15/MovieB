import pytest

from app.services.moviebox_service import MovieBoxService


@pytest.mark.parametrize(
    "input_value,expected",
    [
        ("3325889774849773352", "/detail/3325889774849773352?id=3325889774849773352"),
        ("/detail/naruto-2D7JgAQBGX3?id=3325889774849773352", "/detail/naruto-2D7JgAQBGX3?id=3325889774849773352"),
        (
            "https://h5.aoneroom.com/detail/naruto-2D7JgAQBGX3?id=3325889774849773352",
            "/detail/naruto-2D7JgAQBGX3?id=3325889774849773352",
        ),
    ],
)

def test_normalize_page_url(input_value, expected):
    service = MovieBoxService()
    result = service._normalize_page_url(input_value)
    assert result == expected
