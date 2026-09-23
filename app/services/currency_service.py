from decimal import Decimal
import requests


class CurrencyService:

    BASE_URL = "https://api.frankfurter.dev/v2"

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

        response = requests.get(
            url,
            timeout=15,
        )

        if not response.ok:
            raise ValueError(
                f"Failed to fetch exchange rate "
                f"{from_currency} -> {to_currency}. "
                f"Status: {response.status_code}. "
                f"Response: {response.text}"
            )

        data = response.json()

        return Decimal(
            str(data["rate"])
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