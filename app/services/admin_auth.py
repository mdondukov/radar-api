"""Admin sign-in: a Google ID token in, our own session cookie out.

The dashboard gets the ID token from Google Identity Services in the browser;
it is verified here against Google's public keys and the configured client
id, and the email must be verified by Google and be on the allow list. No
Google client secret is involved. The session is a short HS256 JWT in an
HttpOnly cookie; nothing is stored server-side, so removing an email from the
allow list takes effect on the next request.
"""

from datetime import UTC, datetime, timedelta

import anyio
import jwt

from app.core.config import settings

GOOGLE_CERTS_URL = "https://www.googleapis.com/oauth2/v3/certs"
GOOGLE_ISSUERS = ["accounts.google.com", "https://accounts.google.com"]
SESSION_COOKIE = "radar_admin"
SESSION_ALGORITHM = "HS256"

_jwks = jwt.PyJWKClient(GOOGLE_CERTS_URL, cache_keys=True, lifespan=3600)


class AdminAuthError(Exception):
    pass


def enabled() -> bool:
    return bool(settings.google_client_id and settings.admin_session_secret)


def allowed(email: str) -> bool:
    return email.lower() in {e.lower() for e in settings.admin_emails}


def _verify_google_token(credential: str) -> str:
    try:
        key = _jwks.get_signing_key_from_jwt(credential)
        claims = jwt.decode(
            credential,
            key.key,
            algorithms=["RS256"],
            audience=settings.google_client_id,
            issuer=GOOGLE_ISSUERS,
        )
    except jwt.PyJWTError as exc:
        raise AdminAuthError("invalid Google token") from exc
    email = claims.get("email")
    if not isinstance(email, str) or claims.get("email_verified") is not True:
        raise AdminAuthError("no verified email in the token")
    if not allowed(email):
        raise AdminAuthError("email is not on the allow list")
    return email.lower()


async def sign_in(credential: str) -> str:
    """Returns the admin's email; the key fetch is blocking, so off the loop."""
    return await anyio.to_thread.run_sync(_verify_google_token, credential)


def issue_session(email: str) -> str:
    expires = datetime.now(UTC) + timedelta(days=settings.admin_session_days)
    return jwt.encode(
        {"sub": email, "exp": expires}, settings.admin_session_secret, SESSION_ALGORITHM
    )


def read_session(token: str | None) -> str | None:
    if not token or not enabled():
        return None
    try:
        claims = jwt.decode(token, settings.admin_session_secret, algorithms=[SESSION_ALGORITHM])
    except jwt.PyJWTError:
        return None
    email = claims.get("sub")
    if not isinstance(email, str) or not allowed(email):
        return None
    return email
