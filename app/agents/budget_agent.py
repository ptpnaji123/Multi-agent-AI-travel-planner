from app.models.trip_request import TripRequest
from app.models.flight import RoundTripFlightOption
from app.models.hotel import HotelOption
from app.models.budget import BudgetReport


def budget_agent(
    trip_request: TripRequest,
    selected_flight: RoundTripFlightOption,
    selected_hotel: HotelOption,
) -> BudgetReport:

    print(
        "\n--- BUDGET CALCULATION ---"
    )

    # --------------------------------------------------------
    # Flight cost
    # --------------------------------------------------------

    flight_cost = float(
        selected_flight.total_price_inr
    )

    print(
        f"Flight cost: "
        f"₹{flight_cost:,.2f}"
    )

    # --------------------------------------------------------
    # Hotel cost
    # --------------------------------------------------------

    hotel_cost = float(
        selected_hotel.total_price_inr
    )

    print(
        f"Hotel cost: "
        f"₹{hotel_cost:,.2f}"
    )

    # --------------------------------------------------------
    # Future cost components
    # --------------------------------------------------------
    #
    # Food, transport and activity costs are intentionally
    # disabled for the current version.
    #
    # The previous daily-cost implementation remains in:
    #
    #     app/services/cost_service.py
    #
    # and:
    #
    #     data/daily_costs.json
    #
    # They can be connected again later.
    #
    # --------------------------------------------------------

    food_cost = 0.0
    transport_cost = 0.0
    activity_cost = 0.0

    # --------------------------------------------------------
    # Current total
    # --------------------------------------------------------

    total_cost = (
        flight_cost
        + hotel_cost
    )

    print(
        f"Total trip cost: "
        f"₹{total_cost:,.2f}"
    )

    # --------------------------------------------------------
    # Budget report
    # --------------------------------------------------------

    return BudgetReport(
        currency="INR",

        flight_cost=flight_cost,
        hotel_cost=hotel_cost,

        food_cost=food_cost,
        transport_cost=transport_cost,
        activity_cost=activity_cost,

        total_cost=total_cost,

        notes=(
            "Current estimate includes "
            "flight and hotel costs only. "
            "Food, transport and activity "
            "cost estimation is reserved "
            "for future implementation."
        ),
    )