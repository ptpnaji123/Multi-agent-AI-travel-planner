from app.models.flight import RoundTripFlightOption
from app.models.hotel import HotelOption


def select_flight(
    flights: list[RoundTripFlightOption],
) -> RoundTripFlightOption:

    if not flights:
        raise ValueError("No flight options available for selection.")

    selected = min(
        flights,
        key=lambda flight: flight.total_price_inr,
    )

    print(
        f"Selected flight: "
        f"{selected.outbound.airline} "
        f"{selected.outbound.flight_number}"
    )
    print(
        f"Route: "
        f"{selected.outbound.origin} -> "
        f"{selected.outbound.destination}"
    )
    print(
        f"Flight cost: ₹{selected.total_price_inr:,.2f}"
    )

    return selected


def select_hotel(
    hotels: list[HotelOption],
) -> HotelOption:

    if not hotels:
        raise ValueError("No hotel options available for selection.")

    selected = min(
        hotels,
        key=lambda hotel: hotel.total_price_inr,
    )

    print(f"Selected hotel: {selected.name}")
    print(f"Room: {selected.room_name}")
    print(f"Board: {selected.board}")
    print(
        f"Hotel cost: ₹{selected.total_price_inr:,.2f}"
    )

    return selected