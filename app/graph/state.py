from typing import TypedDict

from app.models.trip_request import TripRequest
from app.models.destination import DestinationResearch
from app.models.flight import RoundTripFlightOption
from app.models.hotel import HotelOption
from app.models.budget import BudgetReport
from app.models.itinerary import Itinerary


class TravelState(TypedDict, total=False):

    user_request: str

    trip_request: TripRequest

    destination_research: DestinationResearch

    flights: list[RoundTripFlightOption]

    hotels: list[HotelOption]

    budget_report: BudgetReport

    itinerary: Itinerary

    critique: dict

    approval: str

    errors: list[str]