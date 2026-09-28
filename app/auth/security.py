import os
from datetime import datetime, timedelta, timezone

import jwt
from dotenv import load_dotenv
from pwdlib import PasswordHash


# ============================================================
# LOAD ENVIRONMENT VARIABLES
# ============================================================

load_dotenv()


# ============================================================
# PASSWORD HASHING
# ============================================================

password_hasher = PasswordHash.recommended()


# ============================================================
# JWT CONFIGURATION
# ============================================================

JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")

JWT_ALGORITHM = "HS256"

JWT_EXPIRATION_MINUTES = 60


if not JWT_SECRET_KEY:
    raise ValueError(
        "JWT_SECRET_KEY is not configured. "
        "Please add it to the .env file."
    )


# ============================================================
# PASSWORD FUNCTIONS
# ============================================================

def hash_password(password: str) -> str:
    """
    Convert a plain-text password into a secure password hash.
    """

    return password_hasher.hash(password)


def verify_password(
    plain_password: str,
    hashed_password: str,
) -> bool:
    """
    Verify a plain-text password against its stored hash.
    """

    return password_hasher.verify(
        plain_password,
        hashed_password,
    )


# ============================================================
# JWT TOKEN CREATION
# ============================================================

def create_access_token(
    user_id: int,
) -> str:
    """
    Create a JWT access token for an authenticated user.
    """

    now = datetime.now(timezone.utc)

    expiration = (
        now
        + timedelta(
            minutes=JWT_EXPIRATION_MINUTES
        )
    )

    payload = {
        "sub": str(user_id),
        "iat": now,
        "exp": expiration,
    }

    token = jwt.encode(
        payload,
        JWT_SECRET_KEY,
        algorithm=JWT_ALGORITHM,
    )

    return token


# ============================================================
# JWT TOKEN VERIFICATION
# ============================================================

def decode_access_token(
    token: str,
) -> dict:
    """
    Decode and validate a JWT access token.

    Raises an exception if the token is invalid
    or expired.
    """

    payload = jwt.decode(
        token,
        JWT_SECRET_KEY,
        algorithms=[JWT_ALGORITHM],
    )

    return payload


# ============================================================
# USER ID EXTRACTION
# ============================================================

def get_user_id_from_token(
    token: str,
) -> int:
    """
    Extract the authenticated user's ID from a JWT.
    """

    payload = decode_access_token(token)

    subject = payload.get("sub")

    if subject is None:
        raise ValueError(
            "Token does not contain a user ID."
        )

    try:
        return int(subject)

    except (TypeError, ValueError) as exc:

        raise ValueError(
            "Invalid user ID in token."
        ) from exc