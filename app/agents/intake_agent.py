from app.llm.mistral import llm
from app.models.trip_request import TripRequest


def intake_agent(user_request: str) -> TripRequest:
    """
    Convert a natural-language travel request
    into a structured TripRequest using Mistral.
    """

    structured_llm = llm.with_structured_output(TripRequest)

    prompt = f"""
You are a travel planning intake agent.

Convert the user's travel request into a structured TripRequest.

Important rules:
- Do not invent missing information.
- If travelers are not mentioned, use 1.
- Currency must be INR.
- Extract the origin and destination.
- Extract start and end dates.
- Extract interests if mentioned.
- Extract travel pace if mentioned.
- Extract hotel preferences if mentioned.
- preferred_airports can remain empty if not mentioned.
- There is NO user-provided budget. Never create one.

User request:
{user_request}
"""

    result = structured_llm.invoke(prompt)

    return result