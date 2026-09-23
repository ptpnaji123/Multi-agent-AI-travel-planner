from app.models.trip_request import TripRequest
from app.models.flight import RoundTripFlightOption
from app.models.hotel import HotelOption
from app.models.budget import BudgetReport
from app.services.cost_service import CostService


def budget_agent(
    trip_request: TripRequest,
    flights: list[RoundTripFlightOption],
    hotels: list[HotelOption],
) -> BudgetReport:

    if not flights:
        raise ValueError(
            "Cannot calculate budget without flights."
        )

    if not hotels:
        raise ValueError(
            "Cannot calculate budget without hotels."
        )

    # -----------------------------------------
    # Select cheapest normalized options
    # -----------------------------------------

    cheapest_flight = min(
        flights,
        key=lambda flight: flight.total_price_inr,
    )

    cheapest_hotel = min(
        hotels,
        key=lambda hotel: hotel.total_price_inr,
    )

    # -----------------------------------------
    # Destination cost estimates
    # -----------------------------------------

    cost_service = CostService()

    destination_costs = (
        cost_service.get_destination_costs(
            trip_request.destination
        )
    )

    number_of_days = (
        trip_request.end_date
        - trip_request.start_date
    ).days

    if number_of_days <= 0:
        raise ValueError(
            "Trip duration must be greater than zero."
        )

    # -----------------------------------------
    # Calculate costs
    # -----------------------------------------

    food_cost = (
        destination_costs["food_per_day"]
        * number_of_days
        * trip_request.travelers
    )

    transport_cost = (
        destination_costs["transport_per_day"]
        * number_of_days
    )

    activity_cost = (
        destination_costs["activities_total"]
    )

    flight_cost = (
        cheapest_flight.total_price_inr
    )

    hotel_cost = (
        cheapest_hotel.total_price_inr
    )

    total_cost = (
        flight_cost
        + hotel_cost
        + food_cost
        + transport_cost
        + activity_cost
    )

    notes = (
        f"Budget uses the cheapest available "
        f"flight and bookable hotel from the "
        f"current search results. Food, transport "
        f"and activity costs are planning estimates."
    )

    return BudgetReport(

        currency="INR",

        flight_cost=round(
            flight_cost,
            2,
        ),

        hotel_cost=round(
            hotel_cost,
            2,
        ),

        food_cost=round(
            food_cost,
            2,
        ),

        transport_cost=round(
            transport_cost,
            2,
        ),

        activity_cost=round(
            activity_cost,
            2,
        ),

        total_cost=round(
            total_cost,
            2,
        ),

        notes=notes,
    )