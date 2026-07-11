"""CLI entry point for the Binance Futures Testnet trading bot.

Usage:
    python cli.py --symbol BTCUSDT --side BUY --type MARKET --quantity 0.01
    python cli.py --symbol BTCUSDT --side SELL --type LIMIT --quantity 0.01 --price 65000
"""
import argparse
import logging
import os
import sys

from bot.client import FuturesTestnetClient
from bot.logging_config import setup_logging
from bot.orders import place_order

logger = setup_logging()


def parse_args(argv=None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Place MARKET or LIMIT orders on Binance Futures Testnet (USDT-M)."
    )
    parser.add_argument("--symbol", required=True, help="Trading pair, e.g. BTCUSDT")
    parser.add_argument("--side", required=True, choices=["BUY", "SELL", "buy", "sell"])
    parser.add_argument("--type", required=True, dest="order_type",
                         choices=["MARKET", "LIMIT", "market", "limit"])
    parser.add_argument("--quantity", required=True, type=float, help="Order quantity")
    parser.add_argument("--price", type=float, default=None,
                         help="Limit price (required for LIMIT orders)")
    return parser.parse_args(argv)


def build_client() -> FuturesTestnetClient:
    api_key = os.environ.get("BINANCE_TESTNET_API_KEY")
    api_secret = os.environ.get("BINANCE_TESTNET_API_SECRET")
    if not api_key or not api_secret:
        print(
            "ERROR: Set BINANCE_TESTNET_API_KEY and BINANCE_TESTNET_API_SECRET "
            "environment variables before running.",
            file=sys.stderr,
        )
        sys.exit(1)
    return FuturesTestnetClient(api_key, api_secret)


def main(argv=None) -> int:
    try:
        args = parse_args(argv)
    except SystemExit:
        # argparse already printed the usage/error message.
        raise

    client = build_client()

    try:
        result = place_order(
            client,
            symbol=args.symbol,
            side=args.side,
            order_type=args.order_type,
            quantity=args.quantity,
            price=args.price,
        )
    except ValueError as exc:
        # Input validation failure - caught before any API call was made.
        logger.error("Validation error: %s", exc)
        print(f"Invalid input: {exc}")
        return 1

    for line in result.summary_lines():
        print(line)

    return 0 if result.success else 1


if __name__ == "__main__":
    sys.exit(main())
