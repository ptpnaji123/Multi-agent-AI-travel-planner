from pydantic import BaseModel, Field


class CancellationPolicy(BaseModel):
    amount: float = 0.0
    from_date: str = ""


class HotelOption(BaseModel):
    hotel_code: str = ""

    name: str = ""

    location: str = ""

    category: str = ""

    rating: float = 0.0

    room_code: str = ""

    room_name: str = ""

    board: str = ""

    price_per_night: float = 0.0

    total_price: float = 0.0

    currency: str = ""

    check_in_date: str = ""

    check_out_date: str = ""

    rate_key: str = ""

    rate_type: str = ""

    rate_class: str = ""

    free_cancellation: bool = False

    cancellation_policies: list[CancellationPolicy] = Field(
        default_factory=list
    )

    provider: str = "hotelbeds"