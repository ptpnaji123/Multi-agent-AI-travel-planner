from app.models.trip_request import TripRequest
from app.models.hotel import HotelOption
from app.providers.hotelbeds_provider import HotelbedsProvider


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

    destination_code = (
        resolve_destination_code(
            trip_request.destination
        )
    )

    provider = HotelbedsProvider(

        certificate_path=(
            CERTIFICATE_PATH
        ),

        private_key_path=(
            PRIVATE_KEY_PATH
        ),
    )

    hotels = provider.search_hotels(

        destination_code=(
            destination_code
        ),

        check_in_date=(
            trip_request.start_date
        ),

        check_out_date=(
            trip_request.end_date
        ),

        adults=(
            trip_request.travelers
        ),

        rooms=1,
    )

    # -------------------------------------------------
    # Keep only BOOKABLE rates
    # -------------------------------------------------

    bookable_hotels = [
        hotel
        for hotel in hotels
        if hotel.rate_type.upper()
        == "BOOKABLE"
    ]

    # -------------------------------------------------
    # Remove duplicate combinations
    # -------------------------------------------------

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

    # -------------------------------------------------
    # Sort by total hotel price
    # -------------------------------------------------

    bookable_hotels = sorted(
        bookable_hotels,
        key=lambda hotel: hotel.total_price,
    )

    # -------------------------------------------------
    # Return top 5
    # -------------------------------------------------

    return bookable_hotels[:5]