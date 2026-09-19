from pydantic import BaseModel, Field


class Activity(BaseModel):
    name: str

    start_time: str
    end_time: str

    location: str

    description: str = ""

    estimated_cost: float = 0.0

    currency: str = "USD"


class ItineraryDay(BaseModel):
    day: int

    date: str

    area: str

    activities: list[Activity] = Field(default_factory=list)


class Itinerary(BaseModel):
    destination: str

    days: list[ItineraryDay] = Field(default_factory=list)