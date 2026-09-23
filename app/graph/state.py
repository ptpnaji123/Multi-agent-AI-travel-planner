from typing import TypedDict

from app.models.trip_request import TripRequest
from app.models.destination import DestinationResearch
from app.models.flight import RoundTripFlightOption
from app.models.hotel import HotelOption
from app.models.budget import BudgetReport
from app.models.itinerary import Itinerary


class TravelState(TypedDict, total=False):
    user_request: str

    # Structured user request
    trip_request: TripRequest

    # Destination research
    destination_research: DestinationResearch

    # Available flight options
    flights: list[RoundTripFlightOption]

    # Selected flight used by downstream agents
    selected_flight: RoundTripFlightOption

    # Available hotel options
    hotels: list[HotelOption]

    # Selected hotel used by downstream agents
    selected_hotel: HotelOption

    # Budget
    budget_report: BudgetReport

    # Final itinerary
    itinerary: Itinerary

    # Validation / critique
    critique: dict
    approval: str

    # Errors collected during the workflow
    errors: list[str]