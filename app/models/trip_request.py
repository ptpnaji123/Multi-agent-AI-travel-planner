from datetime import date

from pydantic import BaseModel, Field


class TripRequest(BaseModel):
    origin: str
    destination: str

    start_date: date
    end_date: date

    travelers: int = Field(default=1, ge=1)

    currency: str = "INR"

    interests: list[str] = Field(default_factory=list)

    pace: str = "moderate"

    preferred_airports: list[str] = Field(default_factory=list)

    hotel_preferences: list[str] = Field(default_factory=list)