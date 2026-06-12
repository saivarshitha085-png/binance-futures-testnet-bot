import logging
from typing import Optional

from .client import BinanceFuturesClient, BinanceAPIError

logger = logging.getLogger('trading_bot.orders')


def place_order(client: BinanceFuturesClient, symbol: str, side: str, order_type: str, quantity: float, price: Optional[float] = None) -> dict:
    """High-level order placement that logs useful summary and normalizes response."""
    try:
        resp = client.place_order(symbol=symbol, side=side, order_type=order_type, quantity=quantity, price=price)
        logger.info('Order successful: %s', {k: resp.get(k) for k in ('orderId', 'status', 'executedQty', 'avgPrice')})
        return resp
    except BinanceAPIError as e:
        logger.error('API error placing order: %s', e)
        raise
    except Exception as e:
        logger.exception('Unexpected error placing order')
        raise
