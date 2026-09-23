CITY_COORDINATES = {

    "dubai": {
        "latitude": 25.2048,
        "longitude": 55.2708,
    },

    "abu dhabi": {
        "latitude": 24.4539,
        "longitude": 54.3773,
    },

    "kochi": {
        "latitude": 9.9312,
        "longitude": 76.2673,
    },

    "cochin": {
        "latitude": 9.9312,
        "longitude": 76.2673,
    },
}


def get_coordinates(
    location: str,
) -> tuple[float, float]:

    location_key = (
        location
        .strip()
        .lower()
    )

    if location_key not in CITY_COORDINATES:

        raise ValueError(
            f"Coordinates not found for "
            f"location: {location}"
        )

    coordinates = CITY_COORDINATES[
        location_key
    ]

    return (
        coordinates["latitude"],
        coordinates["longitude"],
    )