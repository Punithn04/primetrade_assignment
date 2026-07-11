"""Thin wrapper around the Binance USDT-M Futures Testnet REST API.

Implemented with plain `requests` calls (no python-binance dependency) so
the signing/request logic is fully visible and easy to reason about.
"""
import hashlib
import hmac
import logging
import time
from urllib.parse import urlencode

import requests

logger = logging.getLogger("trading_bot")

BASE_URL = "https://testnet.binancefuture.com"
ORDER_ENDPOINT = "/fapi/v1/order"
ACCOUNT_ENDPOINT = "/fapi/v2/account"
TIMEOUT_SECONDS = 10


class BinanceAPIError(Exception):
    """Raised when Binance returns an error response."""

    def __init__(self, status_code: int, code, message: str):
        self.status_code = status_code
        self.code = code
        self.message = message
        super().__init__(f"Binance API error {code} (HTTP {status_code}): {message}")


class BinanceNetworkError(Exception):
    """Raised when the request itself fails (timeout, DNS, connection reset, etc.)."""


class FuturesTestnetClient:
    def __init__(self, api_key: str, api_secret: str, base_url: str = BASE_URL):
        if not api_key or not api_secret:
            raise ValueError("API key and secret are required.")
        self.api_key = api_key
        self.api_secret = api_secret
        self.base_url = base_url
        self.session = requests.Session()
        self.session.headers.update({"X-MBX-APIKEY": self.api_key})

    def _sign(self, params: dict) -> dict:
        params = dict(params)
        params["timestamp"] = int(time.time() * 1000)
        params["recvWindow"] = 5000
        query = urlencode(params, doseq=True)
        signature = hmac.new(
            self.api_secret.encode("utf-8"), query.encode("utf-8"), hashlib.sha256
        ).hexdigest()
        params["signature"] = signature
        return params

    def _request(self, method: str, path: str, params: dict, signed: bool = True) -> dict:
        url = f"{self.base_url}{path}"
        request_params = self._sign(params) if signed else params

        logger.info("REQUEST %s %s params=%s", method, path, _redact(request_params))

        try:
            response = self.session.request(
                method, url, params=request_params, timeout=TIMEOUT_SECONDS
            )
        except requests.exceptions.RequestException as exc:
            logger.error("NETWORK ERROR %s %s: %s", method, path, exc)
            raise BinanceNetworkError(str(exc)) from exc

        logger.info("RESPONSE %s %s status=%s body=%s", method, path, response.status_code, response.text)

        try:
            body = response.json()
        except ValueError:
            body = {}

        if not response.ok:
            code = body.get("code")
            message = body.get("msg", response.text)
            logger.error("API ERROR %s %s status=%s code=%s msg=%s", method, path, response.status_code, code, message)
            raise BinanceAPIError(response.status_code, code, message)

        return body

    def place_order(self, symbol: str, side: str, order_type: str, quantity: float, price=None) -> dict:
        params = {
            "symbol": symbol,
            "side": side,
            "type": order_type,
            "quantity": quantity,
        }
        if order_type == "LIMIT":
            params["price"] = price
            params["timeInForce"] = "GTC"

        return self._request("POST", ORDER_ENDPOINT, params)

    def get_account(self) -> dict:
        return self._request("GET", ACCOUNT_ENDPOINT, {})


def _redact(params: dict) -> dict:
    """Never write the signature (a secret-derived value) to logs."""
    redacted = dict(params)
    if "signature" in redacted:
        redacted["signature"] = "***"
    return redacted
