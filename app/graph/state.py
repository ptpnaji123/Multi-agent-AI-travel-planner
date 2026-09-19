from typing import TypedDict

from app.models.trip_request import TripRequest
from app.models.destination import DestinationResearch
from app.models.flight import FlightOption
from app.models.hotel import HotelOption
from app.models.budget import BudgetReport
from app.models.itinerary import Itinerary


class TravelState(TypedDict, total=False):

    # Original user input
    user_request: str

    # Structured request
    trip_request: TripRequest

    # Research
    destination_research: DestinationResearch

    # Travel options
    flights: list[FlightOption]
    hotels: list[HotelOption]

    # Financial analysis
    budget_report: BudgetReport

    # Final plan
    itinerary: Itinerary

    # Critic
    critique: dict

    # Human approval
    approval: str

    # Errors
    errors: list[str]