def localize(value: dict[str, str] | None, locale: str, default_locale: str) -> str | None:
    if not value:
        return None
    return value.get(locale) or value.get(default_locale) or next(iter(value.values()), None)


def localize_required(value: dict[str, str], locale: str, default_locale: str) -> str:
    text = localize(value, locale, default_locale)
    if text is None:
        raise ValueError("Localized value has no translations")
    return text


def localize_secondary(value: dict[str, str] | None, locale: str | None) -> str | None:
    """Text in the mirror language, for the side-by-side bilingual display.

    Unlike localize(), this never falls back to the project default: a mirror
    with no translation must stay empty rather than repeat the primary text
    back at the reader in the same language. Returns None when no secondary
    locale was requested at all.
    """
    if not value or locale is None:
        return None
    return value.get(locale)
