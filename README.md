# Trading Bot — Binance Futures Testnet (USDT-M)

A small CLI application for placing MARKET and LIMIT orders on the Binance
USDT-M Futures Testnet, with structured client/order/validation layers,
request/response logging, and CLI input validation.

## Project Structure

```
trading_bot/
  bot/
    __init__.py
    client.py        # signed REST calls to Binance Futures Testnet
    orders.py         # order placement logic + result formatting
    validators.py      # CLI input validation
    logging_config.py  # rotating file + console logging setup
  cli.py               # CLI entry point (argparse)
  logs/
    trading_bot.log     # created at runtime
  requirements.txt
  README.md
```

## Setup

1. **Create a Binance Futures Testnet account** at
   https://testnet.binancefuture.com and generate an API key/secret from
   the testnet dashboard.

2. **Install dependencies** (Python 3.9+):

   ```bash
   python -m venv venv
   source venv/bin/activate        # Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. **Set your API credentials as environment variables** (never hard-code
   them or commit them):

   ```bash
   export BINANCE_TESTNET_API_KEY="your_api_key"
   export BINANCE_TESTNET_API_SECRET="your_api_secret"
   ```

   On Windows PowerShell:

   ```powershell
   $env:BINANCE_TESTNET_API_KEY = "your_api_key"
   $env:BINANCE_TESTNET_API_SECRET = "your_api_secret"
   ```

## Running

**Market order:**

```bash
python cli.py --symbol BTCUSDT --side BUY --type MARKET --quantity 0.01
```

**Limit order:**

```bash
python cli.py --symbol BTCUSDT --side SELL --type LIMIT --quantity 0.01 --price 65000
```

Each run prints:
- the order request summary
- the order response (`orderId`, `status`, `executedQty`, `avgPrice` if present)
- a success/failure message

All requests, responses, and errors are logged to `logs/trading_bot.log`
(rotated at 2 MB, 5 backups kept).

## Input Validation

- `symbol` must look like a USDT-M pair (e.g. `BTCUSDT`)
- `side` must be `BUY` or `SELL`
- `type` must be `MARKET` or `LIMIT`
- `quantity` must be a positive number
- `price` is required and must be positive for `LIMIT` orders; ignored for `MARKET`

Invalid input is rejected before any network call is made.

## Error Handling

- **Validation errors** (bad CLI input): caught in `cli.py`, printed clearly, no API call made.
- **API errors** (e.g. insufficient testnet balance, invalid symbol, bad signature):
  raised as `BinanceAPIError` from `bot/client.py`, logged with the Binance error
  code/message, and reported as a failed order — the process does not crash.
- **Network errors** (timeout, DNS failure, connection reset): raised as
  `BinanceNetworkError`, logged, and reported as a failed order.

## Assumptions

- Only USDT-M Futures (`/fapi/v1/order` on `testnet.binancefuture.com`) is in scope —
  not Coin-M futures or Spot.
- LIMIT orders are placed with `timeInForce=GTC` (good-til-cancelled), since the
  task does not specify a different policy.
- Credentials are supplied via environment variables rather than a config file or
  CLI flags, to avoid ever writing secrets to disk or shell history.
- The API key only needs Futures trading permission enabled on the testnet account.

## Bonus

CLI validates all inputs up front with clear, specific error messages (e.g.
`Invalid symbol 'xyz'. Expected a USDT-M pair like 'BTCUSDT'.`) rather than
surfacing raw exceptions.
