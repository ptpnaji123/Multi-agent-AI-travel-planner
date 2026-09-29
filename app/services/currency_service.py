from decimal import Decimal
import requests


class CurrencyService:

    BASE_URL = "https://api.frankfurter.dev/v2"

    # Fallback rates used only when the live exchange-rate API is unavailable.
    # Update these periodically if the live API remains unavailable.
    FALLBACK_RATES = {
        ("USD", "INR"): Decimal("95.66"),
        ("EUR", "INR"): Decimal("109.54"),
        ("GBP", "INR"): Decimal("128.00"),
        ("AED", "INR"): Decimal("26.05"),
    }

    def get_exchange_rate(
        self,
        from_currency: str,
        to_currency: str,
    ) -> Decimal:

        from_currency = from_currency.upper()
        to_currency = to_currency.upper()

        # Same currency: no conversion required.
        if from_currency == to_currency:
            return Decimal("1")

        url = (
            f"{self.BASE_URL}/rate/"
            f"{from_currency}/"
            f"{to_currency}"
        )

        try:
            response = requests.get(
                url,
                timeout=10,
            )

            if response.ok:
                data = response.json()

                rate = Decimal(
                    str(data["rate"])
                )

                print(
                    f"Live exchange rate: "
                    f"1 {from_currency} = {rate} {to_currency}"
                )

                return rate

            print(
                f"Warning: Exchange-rate API returned "
                f"HTTP {response.status_code}."
            )

        except requests.exceptions.Timeout:
            print(
                f"Warning: Exchange-rate API timed out "
                f"for {from_currency} -> {to_currency}."
            )

        except requests.exceptions.RequestException as exc:
            print(
                f"Warning: Exchange-rate API request failed: "
                f"{exc}"
            )

        except (KeyError, ValueError, TypeError) as exc:
            print(
                f"Warning: Invalid exchange-rate API response: "
                f"{exc}"
            )

        # ---------------------------------------------------------
        # FALLBACK
        # ---------------------------------------------------------

        fallback_key = (
            from_currency,
            to_currency,
        )

        if fallback_key in self.FALLBACK_RATES:

            rate = self.FALLBACK_RATES[
                fallback_key
            ]

            print(
                f"Using fallback exchange rate: "
                f"1 {from_currency} = {rate} {to_currency}"
            )

            return rate

        raise ValueError(
            f"Unable to obtain exchange rate "
            f"{from_currency} -> {to_currency}. "
            f"No fallback rate is configured."
        )

    def convert_currency(
        self,
        amount: float | Decimal,
        from_currency: str,
        to_currency: str,
    ) -> Decimal:

        amount = Decimal(
            str(amount)
        )

        rate = self.get_exchange_rate(
            from_currency=from_currency,
            to_currency=to_currency,
        )

        converted_amount = (
            amount * rate
        )

        return converted_amount.quantize(
            Decimal("0.01")
        )


def convert_to_inr(
    amount: float | Decimal,
    currency: str,
) -> Decimal:

    service = CurrencyService()

    return service.convert_currency(
        amount=amount,
        from_currency=currency,
        to_currency="INR",
    )