from pydantic import BaseModel


class HotelOption(BaseModel):
    name: str

    location: str

    rating: float = 0.0

    price_per_night: float

    currency: str

    total_price: float

    booking_url: str = ""