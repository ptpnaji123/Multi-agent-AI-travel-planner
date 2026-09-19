from pydantic import BaseModel


class BudgetReport(BaseModel):
    currency: str = "INR"

    flight_cost: float
    hotel_cost: float
    food_cost: float
    transport_cost: float
    activity_cost: float

    total_cost: float

    notes: str = ""