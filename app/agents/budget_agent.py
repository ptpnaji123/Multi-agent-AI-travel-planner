from app.models.trip_request import TripRequest
from app.models.flight import RoundTripFlightOption
from app.models.hotel import HotelOption
from app.models.budget import BudgetReport

from app.services.cost_service import get_daily_costs


def budget_agent(
    trip_request: TripRequest,
    selected_flight: RoundTripFlightOption,
    selected_hotel: HotelOption,
) -> BudgetReport:

    if not selected_flight:
        raise ValueError(
            "No selected flight available for budget calculation."
        )

    if not selected_hotel:
        raise ValueError(
            "No selected hotel available for budget calculation."
        )

    daily_costs = get_daily_costs(
        trip_request.destination
    )

    trip_days = (
        trip_request.end_date
        - trip_request.start_date
    ).days

    if trip_days <= 0:
        raise ValueError(
            "Trip end date must be after start date."
        )

    travelers = trip_request.travelers

    flight_cost = (
        selected_flight.total_price_inr
    )

    hotel_cost = (
        selected_hotel.total_price_inr
    )

    food_cost = (
        daily_costs["food_per_day"]
        * trip_days
        * travelers
    )

    transport_cost = (
        daily_costs["transport_per_day"]
        * trip_days
    )

    activity_cost = (
        daily_costs["activities_total"]
    )

    total_cost = (
        flight_cost
        + hotel_cost
        + food_cost
        + transport_cost
        + activity_cost
    )

    notes = (
        "Flight and hotel costs are based on the "
        "selected live provider options. "
        "Food, transport, and activity costs are "
        "initial planning estimates."
    )

    report = BudgetReport(
        currency="INR",
        flight_cost=flight_cost,
        hotel_cost=hotel_cost,
        food_cost=food_cost,
        transport_cost=transport_cost,
        activity_cost=activity_cost,
        total_cost=total_cost,
        notes=notes,
    )


    print(
        f"Flight Cost: "
        f"₹{flight_cost:,.2f}"
    )

    print(
        f"Hotel Cost: "
        f"₹{hotel_cost:,.2f}"
    )

    print(
        f"Food Cost: "
        f"₹{food_cost:,.2f}"
    )

    print(
        f"Transport Cost: "
        f"₹{transport_cost:,.2f}"
    )

    print(
        f"Activity Cost: "
        f"₹{activity_cost:,.2f}"
    )

    print(
        f"TOTAL ESTIMATED COST: "
        f"₹{total_cost:,.2f}"
    )

    return report