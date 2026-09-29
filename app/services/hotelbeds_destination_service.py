import json
import re
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]

DESTINATIONS_FILE = (
    PROJECT_ROOT
    / "data"
    / "hotelbeds"
    / "destinations.json"
)


class HotelbedsDestinationService:

    def __init__(self):

        if not DESTINATIONS_FILE.exists():
            raise FileNotFoundError(
                "Hotelbeds destination database not found: "
                f"{DESTINATIONS_FILE}"
            )

        with DESTINATIONS_FILE.open(
            "r",
            encoding="utf-8",
        ) as file:

            self.destinations = json.load(file)

        if not isinstance(
            self.destinations,
            list,
        ):
            raise ValueError(
                "Hotelbeds destination database "
                "must contain a list."
            )

    # -----------------------------------------
    # Text normalization
    # -----------------------------------------

    @staticmethod
    def normalize_text(value: str) -> str:

        value = str(value).strip().lower()

        value = re.sub(
            r"[^a-z0-9\s]",
            " ",
            value,
        )

        value = re.sub(
            r"\s+",
            " ",
            value,
        )

        return value.strip()

    # -----------------------------------------
    # Get destination name
    # -----------------------------------------

    @staticmethod
    def get_name(destination: dict) -> str:

        return (
            destination
            .get("name", {})
            .get("content", "")
            .strip()
        )

    # -----------------------------------------
    # Exact search
    # -----------------------------------------

    def find_exact(
        self,
        destination_name: str,
    ):

        query = self.normalize_text(
            destination_name
        )

        if not query:
            return None

        for destination in self.destinations:

            name = self.get_name(
                destination
            )

            if (
                self.normalize_text(name)
                == query
            ):
                return destination

        return None

    # -----------------------------------------
    # Partial search
    # -----------------------------------------

    def search(
        self,
        destination_name: str,
        limit: int = 10,
    ):

        query = self.normalize_text(
            destination_name
        )

        if not query:
            return []

        results = []

        for destination in self.destinations:

            name = self.get_name(
                destination
            )

            normalized_name = (
                self.normalize_text(name)
            )

            if query in normalized_name:

                results.append(
                    destination
                )

                if len(results) >= limit:
                    break

        return results

    # -----------------------------------------
    # Resolve destination code
    # -----------------------------------------

    def resolve(
        self,
        destination_name: str,
    ) -> str:

        exact = self.find_exact(
            destination_name
        )

        if exact:

            code = exact.get(
                "code",
                "",
            ).strip()

            if code:
                return code

        results = self.search(
            destination_name,
            limit=10,
        )

        if not results:

            raise ValueError(
                "Hotelbeds destination code "
                f"not found for: {destination_name}"
            )

        if len(results) == 1:

            code = results[0].get(
                "code",
                "",
            ).strip()

            if code:
                return code

        names = [
            self.get_name(destination)
            for destination in results
        ]

        raise ValueError(
            "Multiple Hotelbeds destinations "
            f"matched '{destination_name}'. "
            f"Matches: {names}"
        )