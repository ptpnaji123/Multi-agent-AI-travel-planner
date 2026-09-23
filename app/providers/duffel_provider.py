from datetime import date

import requests

from app.config import DUFFEL_ACCESS_TOKEN
from app.models.flight import (
    FlightSegment,
    RoundTripFlightOption,
)
from app.providers.provider_interface import FlightProvider


class DuffelProvider(FlightProvider):

    BASE_URL = "https://api.duffel.com"

    REQUEST_TIMEOUT = 30

    def __init__(self):

        if not DUFFEL_ACCESS_TOKEN:
            raise ValueError(
                "DUFFEL_ACCESS_TOKEN is not configured."
            )

        self.headers = {
            "Authorization": (
                f"Bearer {DUFFEL_ACCESS_TOKEN}"
            ),
            "Duffel-Version": "v2",
            "Accept": "application/json",
            "Content-Type": "application/json",
        }

    def search_flights(
        self,
        origin: str,
        destination: str,
        departure_date: date,
        return_date: date,
        travelers: int = 1,
    ) -> list[RoundTripFlightOption]:

        print(
            f"Searching flights: "
            f"{origin} -> {destination}"
        )

        print(
            f"Outbound date: "
            f"{departure_date}"
        )

        print(
            f"Return date: "
            f"{return_date}"
        )

        print(
            f"Travelers: "
            f"{travelers}"
        )

        # --------------------------------------------------
        # PASSENGERS
        # --------------------------------------------------

        passengers = [
            {"type": "adult"}
            for _ in range(travelers)
        ]

        # --------------------------------------------------
        # RETURN TRIP
        # --------------------------------------------------

        payload = {
            "data": {
                "slices": [
                    {
                        "origin": origin,
                        "destination": destination,
                        "departure_date": (
                            departure_date.isoformat()
                        ),
                    },
                    {
                        "origin": destination,
                        "destination": origin,
                        "departure_date": (
                            return_date.isoformat()
                        ),
                    },
                ],
                "passengers": passengers,
                "cabin_class": "economy",
            }
        }

        # --------------------------------------------------
        # DUFFEL REQUEST
        # --------------------------------------------------

        print(
            "\nSending request to Duffel..."
        )

        try:

            response = requests.post(
                f"{self.BASE_URL}/air/offer_requests",
                headers=self.headers,
                json=payload,
                timeout=self.REQUEST_TIMEOUT,
            )

        except requests.exceptions.Timeout:

            raise TimeoutError(
                "Duffel flight search timed out "
                f"after {self.REQUEST_TIMEOUT} seconds."
            )

        except requests.exceptions.RequestException as exc:

            raise ConnectionError(
                f"Unable to connect to Duffel: {exc}"
            ) from exc

        print(
            f"Duffel response received. "
            f"HTTP {response.status_code}"
        )

        # --------------------------------------------------
        # ERROR HANDLING
        # --------------------------------------------------

        if not response.ok:

            print(
                "\n--- DUFFEL API ERROR ---"
            )

            print(
                "Status:",
                response.status_code,
            )

            print(
                "Response:",
                response.text,
            )

            response.raise_for_status()

        # --------------------------------------------------
        # RESPONSE
        # --------------------------------------------------

        data = response.json()["data"]

        offers = data.get(
            "offers",
            [],
        )

        print(
            f"Duffel offers received: "
            f"{len(offers)}"
        )

        flights = []

        # --------------------------------------------------
        # PROCESS OFFERS
        # --------------------------------------------------

        for offer in offers:

            slices = offer.get(
                "slices",
                [],
            )

            # A return offer must contain
            # two slices.
            if len(slices) < 2:
                continue

            outbound_slice = slices[0]

            return_slice = slices[1]

            outbound_segments = (
                outbound_slice.get(
                    "segments",
                    [],
                )
            )

            return_segments = (
                return_slice.get(
                    "segments",
                    [],
                )
            )

            if not outbound_segments:
                continue

            if not return_segments:
                continue

            # --------------------------------------------------
            # OUTBOUND
            # --------------------------------------------------

            outbound_first = (
                outbound_segments[0]
            )

            outbound_last = (
                outbound_segments[-1]
            )

            outbound_segment = FlightSegment(

                airline=(
                    outbound_first
                    .get(
                        "operating_carrier",
                        {},
                    )
                    .get(
                        "name",
                        "",
                    )
                ),

                flight_number=(
                    outbound_first
                    .get(
                        "operating_carrier_flight_number",
                        "",
                    )
                ),

                origin=(
                    outbound_first
                    .get(
                        "origin",
                        {},
                    )
                    .get(
                        "iata_code",
                        origin,
                    )
                ),

                destination=(
                    outbound_last
                    .get(
                        "destination",
                        {},
                    )
                    .get(
                        "iata_code",
                        destination,
                    )
                ),

                departure_time=(
                    outbound_first
                    .get(
                        "departing_at",
                        "",
                    )
                ),

                arrival_time=(
                    outbound_last
                    .get(
                        "arriving_at",
                        "",
                    )
                ),

                duration=(
                    outbound_slice.get(
                        "duration",
                        "",
                    )
                ),
            )

            # --------------------------------------------------
            # RETURN
            # --------------------------------------------------

            return_first = (
                return_segments[0]
            )

            return_last = (
                return_segments[-1]
            )

            return_segment = FlightSegment(

                airline=(
                    return_first
                    .get(
                        "operating_carrier",
                        {},
                    )
                    .get(
                        "name",
                        "",
                    )
                ),

                flight_number=(
                    return_first
                    .get(
                        "operating_carrier_flight_number",
                        "",
                    )
                ),

                origin=(
                    return_first
                    .get(
                        "origin",
                        {},
                    )
                    .get(
                        "iata_code",
                        destination,
                    )
                ),

                destination=(
                    return_last
                    .get(
                        "destination",
                        {},
                    )
                    .get(
                        "iata_code",
                        origin,
                    )
                ),

                departure_time=(
                    return_first
                    .get(
                        "departing_at",
                        "",
                    )
                ),

                arrival_time=(
                    return_last
                    .get(
                        "arriving_at",
                        "",
                    )
                ),

                duration=(
                    return_slice.get(
                        "duration",
                        "",
                    )
                ),
            )

            # --------------------------------------------------
            # PRICE
            # --------------------------------------------------

            total_price = float(
                offer.get(
                    "total_amount",
                    0,
                )
            )

            currency = offer.get(
                "total_currency",
                "",
            )

            # --------------------------------------------------
            # CREATE ROUND TRIP
            # --------------------------------------------------

            flights.append(
                RoundTripFlightOption(

                    outbound=outbound_segment,

                    return_flight=return_segment,

                    total_price=total_price,

                    currency=currency,

                    provider="duffel",

                    provider_offer_id=(
                        offer.get(
                            "id",
                            "",
                        )
                    ),
                )
            )

        print(
            f"Parsed {len(flights)} "
            f"valid round-trip flights."
        )

        return flights