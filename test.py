from datetime import date

from app.agents.hotel_agent import hotel_agent
from app.models.trip_request import TripRequest


trip_request = TripRequest(
    origin="Kochi",
    destination="Dubai",
    start_date=date(2026, 12, 10),
    end_date=date(2026, 12, 15),
    travelers=1,
    currency="INR",
)


hotels = hotel_agent(
    trip_request
)


print("\n========== RESULTS ==========")

for index, hotel in enumerate(
    hotels,
    start=1,
):

    print(
        f"\n{index}. {hotel.name}"
    )

    print(
        f"   Hotel code: "
        f"{hotel.hotel_code}"
    )

    print(
        f"   Room: "
        f"{hotel.room_name}"
    )

    print(
        f"   Board: "
        f"{hotel.board}"
    )

    print(
        f"   Price: "
        f"{hotel.total_price:.2f} "
        f"{hotel.currency}"
    )

    print(
        f"   INR: "
        f"{hotel.total_price_inr:.2f}"
    )

    print(
        f"   Bookable: "
        f"{bool(hotel.rate_key)}"
    )