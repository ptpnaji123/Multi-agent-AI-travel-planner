from datetime import date

from app.models.flight import FlightOption
from app.providers.provider_interface import FlightProvider


class MockFlightProvider(FlightProvider):

    def search_flights(
        self,
        origin: str,
        destination: str,
        departure_date: date,
        travelers: int = 1,
    ) -> list[FlightOption]:

        return [
            FlightOption(
                airline="Demo Airways",
                flight_number="DA101",
                origin=origin,
                destination=destination,
                departure_time=f"{departure_date} 08:00",
                arrival_time=f"{departure_date} 12:30",
                duration="4h 30m",
                price=18500 * travelers,
                currency="INR",
                booking_url="",
            ),
            FlightOption(
                airline="Demo Airlines",
                flight_number="DA202",
                origin=origin,
                destination=destination,
                departure_time=f"{departure_date} 14:00",
                arrival_time=f"{departure_date} 18:45",
                duration="4h 45m",
                price=19200 * travelers,
                currency="INR",
                booking_url="",
            ),
            FlightOption(
                airline="Demo Express",
                flight_number="DA303",
                origin=origin,
                destination=destination,
                departure_time=f"{departure_date} 20:00",
                arrival_time=f"{departure_date} 00:40",
                duration="4h 40m",
                price=20100 * travelers,
                currency="INR",
                booking_url="",
            ),
        ]
        
        
#TESTING FILE ONLY
