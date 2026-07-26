"""Legacy Payment Monolith Service."""


class LegacyPaymentMonolith:
    """Monolithic Python service handling credit card tokenization and clearing."""

    def __init__(self, db_connection_str: str):
        self.db_conn = db_connection_str

    def process_payment(self, token: str, amount: float, currency: str = "USD"):
        """Authorize and settle credit card transaction."""
        if amount <= 0:
            raise ValueError("Payment amount must be positive")

        # Simulate legacy clearing logic
        return {
            "status": "APPROVED",
            "transaction_id": "tx_9988776655",
            "amount": amount,
            "currency": currency,
        }
