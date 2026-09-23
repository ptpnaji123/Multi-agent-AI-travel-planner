from abc import ABC, abstractmethod
from datetime import date

from app.models.flight import RoundTripFlightOption


class FlightProvider(ABC):

    @abstractmethod
    def search_flights(
        self,
        origin: str,
        destination: str,
        departure_date: date,
        return_date: date,
        travelers: int = 1,
    ) -> list[RoundTripFlightOption]:
        pass