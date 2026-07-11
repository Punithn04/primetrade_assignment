"""Order placement logic: ties validation + client together and formats output."""
import logging

from .client import BinanceAPIError, BinanceNetworkError, FuturesTestnetClient
from .validators import validate_order_args

logger = logging.getLogger("trading_bot")


class OrderResult:
    def __init__(self, success: bool, request: dict, response: dict = None, error: str = None):
        self.success = success
        self.request = request
        self.response = response or {}
        self.error = error

    def summary_lines(self) -> list:
        lines = ["Order Request:"]
        for key, value in self.request.items():
            lines.append(f"  {key}: {value}")

        if self.success:
            lines.append("Order Response:")
            lines.append(f"  orderId: {self.response.get('orderId')}")
            lines.append(f"  status: {self.response.get('status')}")
            lines.append(f"  executedQty: {self.response.get('executedQty')}")
            avg_price = self.response.get("avgPrice")
            if avg_price is not None:
                lines.append(f"  avgPrice: {avg_price}")
            lines.append("Result: SUCCESS")
        else:
            lines.append(f"Result: FAILED - {self.error}")

        return lines


def place_order(client: FuturesTestnetClient, symbol: str, side: str, order_type: str,
                 quantity: float, price=None) -> OrderResult:
    symbol, side, order_type, quantity, price = validate_order_args(
        symbol, side, order_type, quantity, price
    )

    request = {
        "symbol": symbol,
        "side": side,
        "type": order_type,
        "quantity": quantity,
    }
    if price is not None:
        request["price"] = price

    try:
        response = client.place_order(symbol, side, order_type, quantity, price)
        logger.info("Order placed successfully: %s", response)
        return OrderResult(success=True, request=request, response=response)
    except BinanceAPIError as exc:
        logger.error("Order failed (API error): %s", exc)
        return OrderResult(success=False, request=request, error=str(exc))
    except BinanceNetworkError as exc:
        logger.error("Order failed (network error): %s", exc)
        return OrderResult(success=False, request=request, error=f"Network error: {exc}")
