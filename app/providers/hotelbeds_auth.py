import hashlib
import time

from app.config import (
    HOTELBEDS_API_KEY,
    HOTELBEDS_SECRET,
)


def generate_x_signature() -> str:
    """
    Generate Hotelbeds X-Signature.

    Formula:

        SHA256(
            API_KEY
            + SECRET
            + UNIX_TIMESTAMP
        )
    """

    if not HOTELBEDS_API_KEY:
        raise ValueError(
            "HOTELBEDS_API_KEY is not configured."
        )

    if not HOTELBEDS_SECRET:
        raise ValueError(
            "HOTELBEDS_SECRET is not configured."
        )

    timestamp = str(
        int(time.time())
    )

    value = (
        HOTELBEDS_API_KEY
        + HOTELBEDS_SECRET
        + timestamp
    )

    signature = hashlib.sha256(
        value.encode("utf-8")
    ).hexdigest()

    return signature


def get_hotelbeds_headers() -> dict:
    """
    Generate authentication headers.
    """

    return {
        "Api-key": HOTELBEDS_API_KEY,
        "X-Signature": generate_x_signature(),
        "Accept": "application/json",
        "Accept-Encoding": "gzip",
        "Content-Type": "application/json",
    }