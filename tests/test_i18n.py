import pytest

from app.services.i18n import localize, localize_required, localize_secondary


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


def test_secondary_returns_the_mirror_translation() -> None:
    assert localize_secondary({"ru": "Привет", "ky": "Салам"}, "ky") == "Салам"


def test_secondary_is_none_when_no_mirror_was_requested() -> None:
    assert localize_secondary({"ru": "Привет", "ky": "Салам"}, None) is None


def test_secondary_does_not_fall_back_to_another_language() -> None:
    """A mirror with no translation stays empty — falling back would print the
    primary text twice in what is supposed to be the other language."""
    assert localize_secondary({"ru": "Привет"}, "ky") is None
    assert localize_secondary(None, "ky") is None
