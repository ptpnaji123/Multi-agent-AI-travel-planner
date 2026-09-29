from pathlib import Path

from app.models.trip_request import TripRequest
from app.models.hotel import HotelOption

from app.providers.hotelbeds_provider import (
    HotelbedsProvider,
)

from app.services.currency_service import (
    CurrencyService,
)

from app.services.hotelbeds_destination_service import (
    HotelbedsDestinationService,
)


# ============================================================
# PROJECT PATH
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[2]


CERTIFICATES_DIR = (
    PROJECT_ROOT
    / "certificates"
)


CLIENT_CERTIFICATE = (
    CERTIFICATES_DIR
    / "certificate-cc0e5bbc8d5f6a35b8e1786368dcdc5b244b8602b88facfc2456a0c626de89a0.pem"
)


CLIENT_PRIVATE_KEY = (
    CERTIFICATES_DIR
    / "hotelbeds-client-unencrypted.key"
)


# ============================================================
# SERVICES
# ============================================================

destination_service = (
    HotelbedsDestinationService()
)


# ============================================================
# VALIDATE CERTIFICATES
# ============================================================

def validate_hotelbeds_certificates():

    if not CLIENT_CERTIFICATE.exists():

        raise FileNotFoundError(
            "Hotelbeds client certificate not found: "
            f"{CLIENT_CERTIFICATE}"
        )

    if not CLIENT_PRIVATE_KEY.exists():

        raise FileNotFoundError(
            "Hotelbeds client private key not found: "
            f"{CLIENT_PRIVATE_KEY}"
        )


# ============================================================
# HOTELBEDS DESTINATION RESOLUTION
# ============================================================

def resolve_destination_code(
    destination: str,
) -> str:

    return destination_service.resolve(
        destination
    )


# ============================================================
# HOTEL AGENT
# ============================================================

def hotel_agent(
    trip_request: TripRequest,
) -> list[HotelOption]:

    # --------------------------------------------------------
    # Validate certificates
    # --------------------------------------------------------

    validate_hotelbeds_certificates()

    # --------------------------------------------------------
    # Resolve Hotelbeds destination
    # --------------------------------------------------------

    print(
        "\nResolving Hotelbeds destination..."
    )

    destination_code = (
        resolve_destination_code(
            trip_request.destination
        )
    )

    print(
        f"Hotelbeds destination: "
        f"{destination_code}"
    )

    # --------------------------------------------------------
    # Create Hotelbeds provider
    # --------------------------------------------------------

    provider = HotelbedsProvider(
        certificate_path=str(
            CLIENT_CERTIFICATE
        ),
        private_key_path=str(
            CLIENT_PRIVATE_KEY
        ),
    )

    # --------------------------------------------------------
    # Search hotels
    # --------------------------------------------------------

    print(
        "\nSearching Hotelbeds for hotels..."
    )

    hotels = provider.search_hotels(
        destination_code=destination_code,
        check_in_date=trip_request.start_date,
        check_out_date=trip_request.end_date,
        adults=trip_request.travelers,
        rooms=1,
    )

    print(
        f"Hotelbeds returned "
        f"{len(hotels)} hotel options."
    )

    if not hotels:

        raise ValueError(
            "Hotelbeds returned no hotel options."
        )

    # --------------------------------------------------------
    # Keep only bookable hotels
    # --------------------------------------------------------

    bookable_hotels = [
        hotel
        for hotel in hotels
        if hotel.rate_key
    ]

    print(
        f"Bookable hotels: "
        f"{len(bookable_hotels)}"
    )

    if bookable_hotels:

        hotels = bookable_hotels

    # --------------------------------------------------------
    # Remove duplicate hotel/rate combinations
    # --------------------------------------------------------

    unique_hotels = {}

    for hotel in hotels:

        key = (
            hotel.hotel_code,
            hotel.room_code,
            hotel.board,
            hotel.total_price,
            hotel.currency,
        )

        if key not in unique_hotels:

            unique_hotels[key] = hotel

    hotels = list(
        unique_hotels.values()
    )

    print(
        f"Hotels after deduplication: "
        f"{len(hotels)}"
    )

    if not hotels:

        raise ValueError(
            "No usable hotel options "
            "remained after filtering."
        )

    # --------------------------------------------------------
    # Currency conversion
    # --------------------------------------------------------

    print(
        "\nConverting hotel prices to INR..."
    )

    currency_service = CurrencyService()

    currencies = set(
        hotel.currency.upper()
        for hotel in hotels
        if hotel.currency
    )

    exchange_rates = {}

    for currency in currencies:

        # INR does not need conversion
        if currency == "INR":

            exchange_rates[currency] = 1.0

            continue

        print(
            f"Fetching exchange rate: "
            f"{currency} -> INR"
        )

        rate = (
            currency_service.get_exchange_rate(
                from_currency=currency,
                to_currency="INR",
            )
        )

        exchange_rates[currency] = float(
            rate
        )

        print(
            f"{currency} -> INR = {rate}"
        )

    # --------------------------------------------------------
    # Apply INR conversion
    # --------------------------------------------------------

    for hotel in hotels:

        currency = (
            hotel.currency.upper()
        )

        if currency not in exchange_rates:

            raise ValueError(
                "No exchange rate available "
                f"for currency: {currency}"
            )

        hotel.total_price_inr = (
            hotel.total_price
            * exchange_rates[currency]
        )

    print(
        "Hotel currency conversion completed."
    )

    # --------------------------------------------------------
    # Sort hotels by INR price
    # --------------------------------------------------------

    hotels = sorted(
        hotels,
        key=lambda hotel: (
            hotel.total_price_inr
        ),
    )

    # --------------------------------------------------------
    # Return top 5
    # --------------------------------------------------------

    top_hotels = hotels[:5]

    print(
        f"\nReturning "
        f"{len(top_hotels)} hotel options."
    )

    # --------------------------------------------------------
    # Display selected hotels
    # --------------------------------------------------------

    for index, hotel in enumerate(
        top_hotels,
        start=1,
    ):

        print(
            f"{index}. "
            f"{hotel.name} - "
            f"{hotel.total_price_inr:.2f} INR"
        )

    return top_hotels