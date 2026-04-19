from datetime import date
from main import is_last_week_of_month


def test_last_day_of_april():
    assert is_last_week_of_month(date(2026, 4, 30)) is True


def test_day_24_of_april_is_in_last_week():
    # April has 30 days. 30 - 24 = 6 < 7.
    assert is_last_week_of_month(date(2026, 4, 24)) is True


def test_day_23_of_april_is_not_in_last_week():
    # 30 - 23 = 7, not < 7.
    assert is_last_week_of_month(date(2026, 4, 23)) is False


def test_first_day_of_month():
    assert is_last_week_of_month(date(2026, 4, 1)) is False


def test_last_day_of_march():
    # March has 31 days.
    assert is_last_week_of_month(date(2026, 3, 31)) is True


def test_day_25_of_march_is_in_last_week():
    # 31 - 25 = 6 < 7.
    assert is_last_week_of_month(date(2026, 3, 25)) is True


def test_day_24_of_march_is_not_in_last_week():
    # 31 - 24 = 7, not < 7.
    assert is_last_week_of_month(date(2026, 3, 24)) is False
