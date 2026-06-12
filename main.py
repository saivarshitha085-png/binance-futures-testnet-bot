import logging
import os
import sys
from decimal import Decimal
from typing import Optional

import typer

from binance_client import BinanceFuturesClient, BinanceAPIError

app = typer.Typer()
LOG_FILE = 'trading_bot.log'


def setup_logging():
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)
    fmt = logging.Formatter('%(asctime)s %(levelname)s %(name)s: %(message)s')

    fh = logging.FileHandler(LOG_FILE)
    fh.setLevel(logging.DEBUG)
    fh.setFormatter(fmt)
    logger.addHandler(fh)

    ch = logging.StreamHandler(sys.stdout)
    ch.setLevel(logging.INFO)
    ch.setFormatter(logging.Formatter('%(levelname)s: %(message)s'))
    logger.addHandler(ch)


def validate_inputs(symbol: str, side: str, order_type: str, quantity: str, price: Optional[str]):
    side = side.upper()
    if side not in ('BUY', 'SELL'):
        raise typer.BadParameter('side must be BUY or SELL')

    order_type = order_type.upper()
    if order_type not in ('MARKET', 'LIMIT'):
        raise typer.BadParameter('type must be MARKET or LIMIT')

    try:
        qty = Decimal(quantity)
        if qty <= 0:
            raise typer.BadParameter('quantity must be > 0')
    except Exception as e:
        raise typer.BadParameter(f'Invalid quantity: {e}')

    if order_type == 'LIMIT':
        if price is None:
            raise typer.BadParameter('price is required for LIMIT orders')
        try:
            pr = Decimal(price)
            if pr <= 0:
                raise typer.BadParameter('price must be > 0')
        except Exception as e:
            raise typer.BadParameter(f'Invalid price: {e}')

    return side, order_type


@app.command()
def place(
    symbol: str = typer.Option(..., help='Symbol, e.g. BTCUSDT'),
    side: str = typer.Option(..., help='BUY or SELL'),
    order_type: str = typer.Option(..., '--type', '-t', help='MARKET or LIMIT'),
    quantity: str = typer.Option(..., help='Quantity (numeric)'),
    price: Optional[str] = typer.Option(None, help='Price (required for LIMIT)'),
    api_key: Optional[str] = typer.Option(None, help='API key or set BINANCE_API_KEY'),
    api_secret: Optional[str] = typer.Option(None, help='API secret or set BINANCE_API_SECRET'),
    base_url: str = typer.Option('https://testnet.binancefuture.com', help='Base URL for testnet'),
):
    """Place an order on Binance Futures Testnet (USDT-M)."""
    setup_logging()
    logger = logging.getLogger('main')

    try:
        side, order_type = validate_inputs(symbol, side, order_type, quantity, price)
    except typer.BadParameter as e:
        logger.error('Validation error: %s', e)
        typer.echo(f'Validation error: {e}')
        raise typer.Exit(code=1)

    api_key = api_key or os.getenv('BINANCE_API_KEY')
    api_secret = api_secret or os.getenv('BINANCE_API_SECRET')
    if not api_key or not api_secret:
        logger.error('API credentials missing')
        typer.echo('API credentials missing. Provide --api-key/--api-secret or set BINANCE_API_KEY/BINANCE_API_SECRET')
        raise typer.Exit(code=1)

    client = BinanceFuturesClient(api_key=api_key, api_secret=api_secret, base_url=base_url)

    typer.echo('Order request summary:')
    typer.echo(f"  symbol={symbol} side={side} type={order_type} quantity={quantity} price={price}")

    try:
        resp = client.place_order(symbol=symbol, side=side, order_type=order_type, quantity=quantity, price=price)
    except BinanceAPIError as e:
        logger.error('Order failed: %s', e)
        typer.echo(f'Order failed: {e}')
        raise typer.Exit(code=1)
    except Exception as e:
        logger.exception('Unexpected error')
        typer.echo(f'Unexpected error: {e}')
        raise typer.Exit(code=1)

    order_id = resp.get('orderId')
    status = resp.get('status')
    executed_qty = resp.get('executedQty')
    avg_price = resp.get('avgPrice') or resp.get('avgPrice')

    typer.echo('\nOrder response details:')
    typer.echo(f"  orderId: {order_id}")
    typer.echo(f"  status: {status}")
    typer.echo(f"  executedQty: {executed_qty}")
    if avg_price is not None:
        typer.echo(f"  avgPrice: {avg_price}")

    typer.echo('\nSuccess')


if __name__ == '__main__':
    app()
