from abc import ABC, abstractmethod
from datetime import date

from app.models.hotel import HotelOption


class HotelProvider(ABC):

    @abstractmethod
    def search_hotels(
        self,
        latitude: float,
        longitude: float,
        check_in_date: date,
        check_out_date: date,
        guests: int = 1,
        rooms: int = 1,
    ) -> list[HotelOption]:
        pass