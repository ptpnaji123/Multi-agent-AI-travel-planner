import json
from pathlib import Path


COST_FILE = (
    Path(__file__).resolve().parents[2]
    / "data"
    / "daily_costs.json"
)


def get_daily_costs(
    destination: str,
) -> dict:

    if not COST_FILE.exists():
        raise FileNotFoundError(
            f"Daily cost file not found: "
            f"{COST_FILE}"
        )

    with open(
        COST_FILE,
        "r",
        encoding="utf-8",
    ) as file:

        data = json.load(file)

    # Try exact destination first
    if destination in data:
        return data[destination]

    # Try case-insensitive matching
    destination_lower = destination.lower()

    for city, costs in data.items():

        if city.lower() == destination_lower:
            return costs

    raise ValueError(
        f"No daily cost data found "
        f"for destination: {destination}"
    )