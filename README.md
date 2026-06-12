Trading Bot (Binance Futures Testnet) - Simplified

Overview

This small Python project demonstrates placing MARKET and LIMIT orders on Binance Futures Testnet (USDT-M). The code is structured with a client layer, order wrapper, validators, and a Typer CLI.

Setup

1. Create a Python 3.9+ virtualenv and activate it.
2. Install dependencies:
   pip install -r requirements.txt

3. Provide API credentials via env vars or CLI options:
   - BINANCE_API_KEY
   - BINANCE_API_SECRET

How to run (examples)

- MARKET order example:
  python -m trading_bot.cli place --symbol BTCUSDT --side BUY --type MARKET --quantity 0.001 --api-key YOUR_KEY --api-secret YOUR_SECRET

- LIMIT order example:
  python -m trading_bot.cli place --symbol BTCUSDT --side SELL --type LIMIT --quantity 0.001 --price 50000 --api-key YOUR_KEY --api-secret YOUR_SECRET

Important links

- Binance Futures Testnet (site): https://testnet.binancefuture.com
- Futures REST API documentation: https://binance-docs.github.io/apidocs/futures/en/
- API Key management (Futures docs): https://binance-docs.github.io/apidocs/futures/en/#api-key-management

Logging

Logs are written to trading_bot.log by default. Sample simulated log files are in sample_logs/ (market_order.log, limit_order.log).

Assumptions

- Uses REST signed endpoints (no websocket)
- Uses testnet base URL: https://testnet.binancefuture.com
- Simulated log files provided; to generate real logs run the CLI with testnet credentials

Deliverables

- Source files under trading_bot/
- README.md
- requirements.txt
- sample_logs/market_order.log
- sample_logs/limit_order.log
