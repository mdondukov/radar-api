def localize(value: dict[str, str] | None, locale: str, default_locale: str) -> str | None:
    if not value:
        return None
    return value.get(locale) or value.get(default_locale) or next(iter(value.values()), None)


def localize_required(value: dict[str, str], locale: str, default_locale: str) -> str:
    text = localize(value, locale, default_locale)
    if text is None:
        raise ValueError("Localized value has no translations")
    return text
