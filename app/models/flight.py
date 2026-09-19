from pydantic import BaseModel


class FlightOption(BaseModel):
    airline: str

    flight_number: str = ""

    origin: str
    destination: str

    departure_time: str
    arrival_time: str

    duration: str

    price: float
    currency: str

    booking_url: str = ""