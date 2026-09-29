from pydantic import BaseModel


class BudgetReport(BaseModel):

    currency: str = "INR"

    # Active budget components
    flight_cost: float
    hotel_cost: float

    # Reserved for future cost estimation
    # These remain in the model so the functionality
    # can be re-enabled later without changing the schema.
    food_cost: float = 0.0
    transport_cost: float = 0.0
    activity_cost: float = 0.0

    # Current total = flight + hotel
    total_cost: float

    notes: str = ""