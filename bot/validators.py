"""Input validation for order parameters.

Raises ValueError with a human-readable message on any invalid input so
the CLI layer can catch a single exception type and print a clean error.
"""
import re

VALID_SIDES = {"BUY", "SELL"}
VALID_ORDER_TYPES = {"MARKET", "LIMIT"}
# Binance USDT-M perpetual symbols: uppercase letters/digits ending in USDT.
SYMBOL_RE = re.compile(r"^[A-Z0-9]{3,20}USDT$")


def validate_symbol(symbol: str) -> str:
    symbol = symbol.strip().upper()
    if not SYMBOL_RE.match(symbol):
        raise ValueError(
            f"Invalid symbol '{symbol}'. Expected a USDT-M pair like 'BTCUSDT'."
        )
    return symbol


def validate_side(side: str) -> str:
    side = side.strip().upper()
    if side not in VALID_SIDES:
        raise ValueError(f"Invalid side '{side}'. Must be one of {sorted(VALID_SIDES)}.")
    return side


def validate_order_type(order_type: str) -> str:
    order_type = order_type.strip().upper()
    if order_type not in VALID_ORDER_TYPES:
        raise ValueError(
            f"Invalid order type '{order_type}'. Must be one of {sorted(VALID_ORDER_TYPES)}."
        )
    return order_type


def validate_quantity(quantity: float) -> float:
    if quantity is None:
        raise ValueError("Quantity is required.")
    if quantity <= 0:
        raise ValueError(f"Quantity must be positive, got {quantity}.")
    return quantity


def validate_price(price, order_type: str):
    if order_type == "LIMIT":
        if price is None:
            raise ValueError("Price is required for LIMIT orders.")
        if price <= 0:
            raise ValueError(f"Price must be positive, got {price}.")
        return price
    # MARKET orders ignore price
    return None


def validate_order_args(symbol: str, side: str, order_type: str, quantity: float, price=None):
    """Validate a full set of order arguments and return the normalized values."""
    symbol = validate_symbol(symbol)
    side = validate_side(side)
    order_type = validate_order_type(order_type)
    quantity = validate_quantity(quantity)
    price = validate_price(price, order_type)
    return symbol, side, order_type, quantity, price
