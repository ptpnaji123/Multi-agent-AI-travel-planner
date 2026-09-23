from app.models.trip_request import TripRequest
from app.models.flight import RoundTripFlightOption
from app.providers.duffel_provider import DuffelProvider


# Temporary airport mapping.
# We will replace this later with a proper airport
# lookup service.

AIRPORT_CODES = {
    "kochi": "COK",
    "cochin": "COK",
    "dubai": "DXB",
}


def resolve_airport_code(
    location: str
) -> str:

    location_key = (
        location
        .strip()
        .lower()
    )

    if location_key in AIRPORT_CODES:

        return AIRPORT_CODES[
            location_key
        ]

    # Allow direct IATA codes.
    if len(location_key) == 3:

        return location_key.upper()

    raise ValueError(
        f"Airport code not found "
        f"for location: {location}"
    )


def flight_agent(
    trip_request: TripRequest,
) -> list[RoundTripFlightOption]:

    # --------------------------------------------------
    # RESOLVE AIRPORTS
    # --------------------------------------------------

    origin = resolve_airport_code(
        trip_request.origin
    )

    destination = resolve_airport_code(
        trip_request.destination
    )

    # --------------------------------------------------
    # PROVIDER
    # --------------------------------------------------

    provider = DuffelProvider()

    # --------------------------------------------------
    # SEARCH ROUND TRIP
    # --------------------------------------------------

    flights = provider.search_flights(

        origin=origin,

        destination=destination,

        departure_date=(
            trip_request.start_date
        ),

        return_date=(
            trip_request.end_date
        ),

        travelers=(
            trip_request.travelers
        ),
    )

    # --------------------------------------------------
    # SORT BY TOTAL PRICE
    # --------------------------------------------------

    flights = sorted(
        flights,
        key=lambda flight: flight.total_price
    )

    # --------------------------------------------------
    # TOP 3
    # --------------------------------------------------

    return flights[:3]