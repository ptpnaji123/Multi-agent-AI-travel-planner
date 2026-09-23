from pydantic import BaseModel


class FlightSegment(BaseModel):
    airline: str
    flight_number: str = ""

    origin: str
    destination: str

    departure_time: str
    arrival_time: str

    duration: str = ""


class RoundTripFlightOption(BaseModel):
    outbound: FlightSegment
    return_flight: FlightSegment

    total_price: float
    currency: str

    provider: str = ""
    provider_offer_id: str = ""

    booking_url: str = ""