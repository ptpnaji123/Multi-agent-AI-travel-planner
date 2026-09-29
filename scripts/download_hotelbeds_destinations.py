import json
import sys
from pathlib import Path

import requests


# -----------------------------------------
# Project root
# -----------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parents[1]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


from app.providers.hotelbeds_auth import (
    get_hotelbeds_headers,
)


# -----------------------------------------
# Configuration
# -----------------------------------------

OUTPUT_FILE = (
    PROJECT_ROOT
    / "data"
    / "hotelbeds"
    / "destinations.json"
)

BASE_URL = (
    "https://api.test.hotelbeds.com"
)

DESTINATIONS_URL = (
    BASE_URL
    + "/hotel-content-api/1.0/locations/destinations"
)

PAGE_SIZE = 1000


# -----------------------------------------
# Download destinations
# -----------------------------------------

def fetch_destinations():

    headers = get_hotelbeds_headers()

    # -----------------------------------------
    # First request
    # -----------------------------------------

    print(
        "[HOTELBEDS] Getting destination count..."
    )

    response = requests.get(
        DESTINATIONS_URL,
        headers=headers,
        params={
            "fields": "all",
            "language": "ENG",
            "from": 1,
            "to": PAGE_SIZE,
        },
        timeout=60,
    )

    print(
        "[HOTELBEDS] Status:",
        response.status_code,
    )

    response.raise_for_status()

    data = response.json()

    total = int(
        data.get(
            "total",
            0,
        )
    )

    print(
        f"[HOTELBEDS] Total destinations: {total}"
    )

    all_destinations = []

    # -----------------------------------------
    # Download all pages
    # -----------------------------------------

    current_from = 1

    while current_from <= total:

        current_to = min(
            current_from + PAGE_SIZE - 1,
            total,
        )

        print(
            f"[HOTELBEDS] Downloading "
            f"{current_from} - {current_to}..."
        )

        response = requests.get(
            DESTINATIONS_URL,
            headers=headers,
            params={
                "fields": "all",
                "language": "ENG",
                "from": current_from,
                "to": current_to,
            },
            timeout=60,
        )

        print(
            "[HOTELBEDS] Status:",
            response.status_code,
        )

        response.raise_for_status()

        data = response.json()

        destinations = data.get(
            "destinations",
            [],
        )

        all_destinations.extend(
            destinations
        )

        print(
            f"[HOTELBEDS] Received "
            f"{len(destinations)} destinations."
        )

        current_from = (
            current_to + 1
        )

    # -----------------------------------------
    # Save JSON
    # -----------------------------------------

    OUTPUT_FILE.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    with OUTPUT_FILE.open(
        "w",
        encoding="utf-8",
    ) as file:

        json.dump(
            all_destinations,
            file,
            ensure_ascii=False,
            indent=2,
        )

    print()
    print(
        "[HOTELBEDS] Download completed."
    )

    print(
        f"[HOTELBEDS] Saved "
        f"{len(all_destinations)} destinations."
    )

    print(
        f"[HOTELBEDS] File: "
        f"{OUTPUT_FILE}"
    )


# -----------------------------------------
# Main
# -----------------------------------------

if __name__ == "__main__":
    fetch_destinations()