from decimal import Decimal
from typing import Optional

from typer import BadParameter


def validate_inputs(symbol: str, side: str, order_type: str, quantity: str, price: Optional[str]):
    side = side.upper()
    if side not in ('BUY', 'SELL'):
        raise BadParameter('side must be BUY or SELL')

    order_type = order_type.upper()
    if order_type not in ('MARKET', 'LIMIT'):
        raise BadParameter('type must be MARKET or LIMIT')

    try:
        qty = Decimal(quantity)
        if qty <= 0:
            raise BadParameter('quantity must be > 0')
    except Exception as e:
        raise BadParameter(f'Invalid quantity: {e}')

    if order_type == 'LIMIT':
        if price is None:
            raise BadParameter('price is required for LIMIT orders')
        try:
            pr = Decimal(price)
            if pr <= 0:
                raise BadParameter('price must be > 0')
        except Exception as e:
            raise BadParameter(f'Invalid price: {e}')

    return side, order_type
