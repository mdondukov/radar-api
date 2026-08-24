import pytest

from app.services.i18n import localize, localize_required


def test_prefers_the_requested_locale() -> None:
    assert localize({"ru": "Привет", "ky": "Салам"}, "ky", "ru") == "Салам"


def test_falls_back_to_the_project_default_locale() -> None:
    assert localize({"ru": "Привет"}, "ky", "ru") == "Привет"


def test_falls_back_to_any_available_translation() -> None:
    assert localize({"en": "Hello"}, "ky", "ru") == "Hello"


def test_returns_none_for_missing_or_empty_value() -> None:
    assert localize(None, "ru", "ru") is None
    assert localize({}, "ru", "ru") is None


def test_required_variant_raises_when_nothing_is_translated() -> None:
    with pytest.raises(ValueError):
        localize_required({}, "ru", "ru")


def test_required_variant_returns_the_text_when_present() -> None:
    assert localize_required({"ru": "Привет"}, "en", "ru") == "Привет"
