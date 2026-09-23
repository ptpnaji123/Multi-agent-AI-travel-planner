from app.models.trip_request import TripRequest
from app.models.flight import RoundTripFlightOption
from app.providers.duffel_provider import DuffelProvider
from app.services.currency_service import CurrencyService


AIRPORT_CODES = {
    "kochi": "COK",
    "cochin": "COK",
    "dubai": "DXB",
}


def resolve_airport_code(
    location: str,
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

    if len(location_key) == 3:
        return location_key.upper()

    raise ValueError(
        f"Airport code not found for location: "
        f"{location}"
    )


def flight_agent(
    trip_request: TripRequest,
) -> list[RoundTripFlightOption]:

    origin = resolve_airport_code(
        trip_request.origin
    )

    destination = resolve_airport_code(
        trip_request.destination
    )

    provider = DuffelProvider()

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

    # -----------------------------------------
    # Currency conversion
    # -----------------------------------------

    currency_service = CurrencyService()

    for flight in flights:

        flight.total_price_inr = float(
            currency_service.convert_currency(

                amount=flight.total_price,

                from_currency=flight.currency,

                to_currency="INR",
            )
        )

    # -----------------------------------------
    # Sort by INR price
    # -----------------------------------------

    flights = sorted(
        flights,
        key=lambda flight: (
            flight.total_price_inr
        ),
    )

    # -----------------------------------------
    # Return top 3
    # -----------------------------------------

    return flights[:3]