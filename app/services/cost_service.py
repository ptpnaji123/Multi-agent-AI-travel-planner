import json
from pathlib import Path


COST_FILE = (
    Path(__file__).resolve().parents[2]
    / "data"
    / "daily_costs.json"
)


class CostService:

    def __init__(self):

        if not COST_FILE.exists():
            raise FileNotFoundError(
                f"Cost data file not found: {COST_FILE}"
            )

        with open(
            COST_FILE,
            "r",
            encoding="utf-8",
        ) as file:

            self.costs = json.load(file)

    def get_destination_costs(
        self,
        destination: str,
    ) -> dict:

        destination_key = destination.strip()

        if destination_key not in self.costs:

            raise ValueError(
                "No cost data available for "
                f"destination: {destination}"
            )

        return self.costs[destination_key]