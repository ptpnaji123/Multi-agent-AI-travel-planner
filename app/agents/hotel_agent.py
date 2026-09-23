from decimal import Decimal

from app.models.trip_request import TripRequest
from app.models.hotel import HotelOption
from app.providers.hotelbeds_provider import HotelbedsProvider
from app.services.currency_service import CurrencyService


DESTINATION_CODES = {
    "dubai": "DXB",
}


CERTIFICATE_PATH = (
    "certificates/"
    "certificate-cc0e5bbc8d5f6a35b8e1786368dcdc5b244b8602b88facfc2456a0c626de89a0.pem"
)

PRIVATE_KEY_PATH = (
    "certificates/"
    "hotelbeds-client-unencrypted.key"
)


def resolve_destination_code(
    destination: str,
) -> str:

    destination_key = (
        destination
        .strip()
        .lower()
    )

    if destination_key in DESTINATION_CODES:
        return DESTINATION_CODES[
            destination_key
        ]

    raise ValueError(
        "Hotelbeds destination code "
        f"not found for: {destination}"
    )


def hotel_agent(
    trip_request: TripRequest,
) -> list[HotelOption]:

    print(
        "\n[HOTEL] Resolving destination..."
    )

    destination_code = resolve_destination_code(
        trip_request.destination
    )

    provider = HotelbedsProvider(
        certificate_path=CERTIFICATE_PATH,
        private_key_path=PRIVATE_KEY_PATH,
    )

    print(
        "[HOTEL] Calling Hotelbeds..."
    )

    hotels = provider.search_hotels(
        destination_code=destination_code,
        check_in_date=trip_request.start_date,
        check_out_date=trip_request.end_date,
        adults=trip_request.travelers,
        rooms=1,
    )

    print(
        f"[HOTEL] Hotelbeds returned "
        f"{len(hotels)} rate combinations."
    )

    # -----------------------------------------------------
    # STEP 1: Keep only BOOKABLE rates
    # -----------------------------------------------------

    bookable_hotels = [
        hotel
        for hotel in hotels
        if hotel.rate_type.upper() == "BOOKABLE"
    ]

    print(
        f"[HOTEL] BOOKABLE rates: "
        f"{len(bookable_hotels)}"
    )

    if not bookable_hotels:
        print(
            "[HOTEL] No BOOKABLE hotel rates found."
        )

        return []

    # -----------------------------------------------------
    # STEP 2: Remove duplicates
    # -----------------------------------------------------

    unique_hotels = {}

    for hotel in bookable_hotels:

        key = (
            hotel.hotel_code,
            hotel.room_code,
            hotel.board,
            hotel.total_price,
            hotel.currency,
        )

        if key not in unique_hotels:
            unique_hotels[key] = hotel

    bookable_hotels = list(
        unique_hotels.values()
    )

    print(
        f"[HOTEL] After deduplication: "
        f"{len(bookable_hotels)}"
    )

    # -----------------------------------------------------
    # STEP 3: Get exchange rates ONCE per currency
    # -----------------------------------------------------

    currency_service = CurrencyService()

    currencies = sorted(
        {
            hotel.currency.upper()
            for hotel in bookable_hotels
            if hotel.currency
        }
    )

    print(
        f"[HOTEL] Provider currencies: "
        f"{currencies}"
    )

    exchange_rates = {}

    for currency in currencies:

        if currency == "INR":

            exchange_rates[currency] = Decimal("1")

            continue

        print(
            f"[HOTEL] Fetching "
            f"{currency} -> INR exchange rate..."
        )

        rate = currency_service.get_exchange_rate(
            from_currency=currency,
            to_currency="INR",
        )

        exchange_rates[currency] = rate

        print(
            f"[HOTEL] {currency} -> INR = {rate}"
        )

    # -----------------------------------------------------
    # STEP 4: Convert all prices LOCALLY
    # -----------------------------------------------------

    for hotel in bookable_hotels:

        currency = hotel.currency.upper()

        if currency not in exchange_rates:
            raise ValueError(
                "Missing exchange rate for "
                f"currency: {currency}"
            )

        exchange_rate = exchange_rates[
            currency
        ]

        hotel.total_price_inr = float(
            (
                Decimal(
                    str(hotel.total_price)
                )
                * exchange_rate
            ).quantize(
                Decimal("0.01")
            )
        )

    print(
        "[HOTEL] Currency conversion completed."
    )

    # -----------------------------------------------------
    # STEP 5: Sort by INR price
    # -----------------------------------------------------

    bookable_hotels = sorted(
        bookable_hotels,
        key=lambda hotel: hotel.total_price_inr,
    )

    # -----------------------------------------------------
    # STEP 6: Return top 5
    # -----------------------------------------------------

    top_hotels = bookable_hotels[:5]

    print(
        f"[HOTEL] Returning "
        f"{len(top_hotels)} hotel options."
    )

    for index, hotel in enumerate(
        top_hotels,
        start=1,
    ):

        print(
            f"[HOTEL] {index}. "
            f"{hotel.name} | "
            f"{hotel.currency} "
            f"{hotel.total_price:.2f} | "
            f"₹{hotel.total_price_inr:,.2f}"
        )

    return top_hotels