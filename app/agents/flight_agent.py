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

    print(
        "\nResolving airport codes..."
    )

    origin = resolve_airport_code(
        trip_request.origin
    )

    destination = resolve_airport_code(
        trip_request.destination
    )

    print(
        f"Origin airport: {origin}"
    )

    print(
        f"Destination airport: {destination}"
    )

    # -----------------------------------------
    # Duffel provider
    # -----------------------------------------

    provider = DuffelProvider()

    print(
        "\nSearching Duffel for flights..."
    )

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

    print(
        f"Duffel returned "
        f"{len(flights)} flight options."
    )

    if not flights:
        raise ValueError(
            "Duffel returned no flight options."
        )

    # -----------------------------------------
    # Currency conversion
    # -----------------------------------------

    print(
        "\nConverting flight prices to INR..."
    )

    currency_service = CurrencyService()

    # Get unique currencies first.
    currencies = set(
        flight.currency.upper()
        for flight in flights
        if flight.currency
    )

    exchange_rates = {}

    for currency in currencies:

        if currency == "INR":

            exchange_rates[currency] = 1.0

            continue

        print(
            f"Fetching exchange rate: "
            f"{currency} -> INR"
        )

        rate = currency_service.get_exchange_rate(
            from_currency=currency,
            to_currency="INR",
        )

        exchange_rates[currency] = float(
            rate
        )

        print(
            f"{currency} -> INR = "
            f"{rate}"
        )

    # -----------------------------------------
    # Apply exchange rates
    # -----------------------------------------

    for flight in flights:

        currency = (
            flight.currency.upper()
        )

        if currency not in exchange_rates:
            raise ValueError(
                f"No exchange rate available "
                f"for currency: {currency}"
            )

        flight.total_price_inr = (
            flight.total_price
            * exchange_rates[currency]
        )

    print(
        "Currency conversion completed."
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

    top_flights = flights[:3]

    print(
        f"\nReturning "
        f"{len(top_flights)} flight options."
    )

    return top_flights