from datetime import date

from app.models.trip_request import TripRequest
from app.agents.flight_agent import flight_agent
from app.agents.hotel_agent import hotel_agent


def main():

    trip_request = TripRequest(

        origin="Kochi",

        destination="Dubai",

        start_date=date(
            2026,
            12,
            10,
        ),

        end_date=date(
            2026,
            12,
            15,
        ),

        travelers=1,

        currency="INR",
    )

    # =========================================
    # FLIGHTS
    # =========================================

    print("\n================================")
    print("FLIGHT PRICE NORMALIZATION")
    print("================================")

    flights = flight_agent(
        trip_request
    )

    for index, flight in enumerate(
        flights,
        start=1,
    ):

        print(
            f"\nFlight {index}"
        )

        print(
            f"Original: "
            f"{flight.total_price:.2f} "
            f"{flight.currency}"
        )

        print(
            f"INR: "
            f"₹{flight.total_price_inr:,.2f}"
        )

    # =========================================
    # HOTELS
    # =========================================

    print("\n================================")
    print("HOTEL PRICE NORMALIZATION")
    print("================================")

    hotels = hotel_agent(
        trip_request
    )

    for index, hotel in enumerate(
        hotels,
        start=1,
    ):

        print(
            f"\nHotel {index}"
        )

        print(
            f"Hotel: "
            f"{hotel.name}"
        )

        print(
            f"Original: "
            f"{hotel.total_price:.2f} "
            f"{hotel.currency}"
        )

        print(
            f"INR: "
            f"₹{hotel.total_price_inr:,.2f}"
        )


if __name__ == "__main__":
    main()