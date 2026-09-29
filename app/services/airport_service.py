from pathlib import Path
import re

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[2]
AIRPORTS_FILE = PROJECT_ROOT / "data" / "airports.csv"


class AirportService:
    def __init__(self):
        if not AIRPORTS_FILE.exists():
            raise FileNotFoundError(
                f"Airport database not found: {AIRPORTS_FILE}"
            )

        self.airports = pd.read_csv(
            AIRPORTS_FILE,
            dtype=str,
            keep_default_na=False,
        )

        # Normalize important columns
        for column in [
            "name",
            "municipality",
            "iso_country",
            "iso_region",
            "icao_code",
            "iata_code",
            "gps_code",
            "local_code",
            "type",
        ]:
            if column in self.airports.columns:
                self.airports[column] = (
                    self.airports[column]
                    .fillna("")
                    .astype(str)
                    .str.strip()
                )

    @staticmethod
    def normalize_text(value: str) -> str:
        """
        Normalize user-entered airport/city names.
        """

        value = str(value).strip().lower()

        # Replace punctuation with spaces
        value = re.sub(r"[^a-z0-9\s]", " ", value)

        # Collapse multiple spaces
        value = re.sub(r"\s+", " ", value)

        return value.strip()

    def _normalized_series(self, column: str):
        return self.airports[column].map(
            self.normalize_text
        )

    def find_by_iata(self, code: str):
        """
        Find airport by IATA code.
        """

        code = str(code).strip().upper()

        if not code:
            return None

        matches = self.airports[
            self.airports["iata_code"].str.upper() == code
        ]

        if matches.empty:
            return None

        return matches.iloc[0].to_dict()

    def find_by_icao(self, code: str):
        """
        Find airport by ICAO code.
        """

        code = str(code).strip().upper()

        if not code:
            return None

        matches = self.airports[
            self.airports["icao_code"].str.upper() == code
        ]

        if matches.empty:
            return None

        return matches.iloc[0].to_dict()

    def search(self, location: str, limit: int = 10):
        """
        Search the airport database.

        Search priority:

        1. IATA
        2. ICAO
        3. Exact airport name
        4. Exact municipality
        5. Partial airport name
        6. Partial municipality

        Only records with IATA codes are returned when
        possible because commercial flight providers
        require usable airport codes.
        """

        query = self.normalize_text(location)

        if not query:
            return []

        # --------------------------------------------------
        # 1. IATA code
        # --------------------------------------------------

        iata_match = self.find_by_iata(query)

        if iata_match:
            return [iata_match]

        # --------------------------------------------------
        # 2. ICAO code
        # --------------------------------------------------

        icao_match = self.find_by_icao(query)

        if icao_match:
            return [icao_match]

        # --------------------------------------------------
        # Normalized columns
        # --------------------------------------------------

        name_normalized = self._normalized_series("name")
        municipality_normalized = self._normalized_series(
            "municipality"
        )

        # --------------------------------------------------
        # 3. Exact airport name
        # --------------------------------------------------

        exact_name = self.airports[
            name_normalized == query
        ]

        # Keep only airports with IATA codes
        exact_name = exact_name[
            exact_name["iata_code"].str.strip() != ""
        ]

        if not exact_name.empty:
            return exact_name.head(limit).to_dict(
                "records"
            )

        # --------------------------------------------------
        # 4. Exact municipality
        # --------------------------------------------------

        exact_city = self.airports[
            municipality_normalized == query
        ]

        # IMPORTANT:
        # There may be many heliports/airfields in a city.
        # Keep only records with an IATA code.
        exact_city = exact_city[
            exact_city["iata_code"].str.strip() != ""
        ]

        if not exact_city.empty:

            # Prefer actual airports over other facility types
            if "type" in exact_city.columns:
                airport_rows = exact_city[
                    exact_city["type"].str.lower() == "large_airport"
                ]

                if airport_rows.empty:
                    airport_rows = exact_city[
                        exact_city["type"].str.lower() == "medium_airport"
                    ]

                if not airport_rows.empty:
                    exact_city = airport_rows

            return exact_city.head(limit).to_dict(
                "records"
            )

        # --------------------------------------------------
        # 5. Partial airport name
        # --------------------------------------------------

        name_matches = self.airports[
            name_normalized.str.contains(
                query,
                regex=False,
                na=False,
            )
        ]

        name_matches = name_matches[
            name_matches["iata_code"].str.strip() != ""
        ]

        # --------------------------------------------------
        # 6. Partial municipality
        # --------------------------------------------------

        city_matches = self.airports[
            municipality_normalized.str.contains(
                query,
                regex=False,
                na=False,
            )
        ]

        city_matches = city_matches[
            city_matches["iata_code"].str.strip() != ""
        ]

        # Combine results
        results = pd.concat(
            [
                name_matches,
                city_matches,
            ],
            ignore_index=True,
        )

        # Remove duplicate airport records
        if "ident" in results.columns:
            results = results.drop_duplicates(
                subset=["ident"]
            )

        # Prefer actual airports
        if "type" in results.columns:

            large = results[
                results["type"].str.lower()
                == "large_airport"
            ]

            medium = results[
                results["type"].str.lower()
                == "medium_airport"
            ]

            small = results[
                results["type"].str.lower()
                == "small_airport"
            ]

            ordered = pd.concat(
                [
                    large,
                    medium,
                    small,
                    results,
                ],
                ignore_index=True,
            )

            if "ident" in ordered.columns:
                ordered = ordered.drop_duplicates(
                    subset=["ident"]
                )

            results = ordered

        return results.head(limit).to_dict(
            "records"
        )

    def resolve(self, location: str) -> str:
        """
        Resolve a city/airport name to an IATA code.
        """

        results = self.search(
            location,
            limit=10,
        )

        if not results:
            raise ValueError(
                f"Airport code not found for location: "
                f"{location}"
            )

        # Only consider records with IATA codes
        iata_results = [
            airport
            for airport in results
            if airport.get("iata_code", "").strip()
        ]

        if not iata_results:
            raise ValueError(
                f"No IATA airport code found for location: "
                f"{location}"
            )

        selected = iata_results[0]

        return selected["iata_code"].upper()