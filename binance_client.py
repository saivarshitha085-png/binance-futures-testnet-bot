import time
import hmac
import hashlib
import logging
import requests
from typing import Optional

logger = logging.getLogger(__name__)


class BinanceAPIError(Exception):
    pass


class BinanceFuturesClient:
    def __init__(self, api_key: str, api_secret: str, base_url: str = "https://testnet.binancefuture.com"):
        if not api_key or not api_secret:
            raise ValueError("API key and secret are required")
        self.api_key = api_key
        self.api_secret = api_secret
        self.base_url = base_url.rstrip('/')

    def _sign(self, params: dict) -> dict:
        params = params.copy()
        params.setdefault('timestamp', int(time.time() * 1000))
        # build query string in sorted order for deterministic signing
        query = '&'.join([f"{k}={params[k]}" for k in sorted(params.keys())])
        signature = hmac.new(self.api_secret.encode('utf-8'), query.encode('utf-8'), hashlib.sha256).hexdigest()
        params['signature'] = signature
        return params

    def place_order(self, symbol: str, side: str, order_type: str, quantity: float, price: Optional[float] = None, recvWindow: int = 5000) -> dict:
        """Place an order on Binance Futures Testnet (USDT-M).

        symbol: e.g., BTCUSDT
        side: BUY or SELL
        order_type: MARKET or LIMIT
        quantity: numeric quantity
        price: required for LIMIT
        """
        path = "/fapi/v1/order"
        url = self.base_url + path

        params = {
            'symbol': symbol,
            'side': side,
            'type': order_type,
            'quantity': float(quantity),
            'recvWindow': int(recvWindow),
        }
        if order_type.upper() == 'LIMIT':
            if price is None:
                raise ValueError('price is required for LIMIT orders')
            params['price'] = float(price)
            params['timeInForce'] = 'GTC'

        signed = self._sign(params)
        headers = {'X-MBX-APIKEY': self.api_key}

        # Log request details (avoid logging secrets)
        safe_log = {k: v for k, v in signed.items() if k != 'signature'}
        logger.debug('POST %s payload: %s', url, safe_log)

        try:
            resp = requests.post(url, headers=headers, data=signed, timeout=10)
            text = resp.text
            logger.debug('Response status %s body %s', resp.status_code, text)
            resp.raise_for_status()
            data = resp.json()
            return data
        except requests.exceptions.RequestException as e:
            logger.exception('Network/API error while placing order')
            # try to extract JSON error message if present
            try:
                err = getattr(e.response, 'text', None) or str(e)
            except Exception:
                err = str(e)
            raise BinanceAPIError(f'Failed to place order: {err}') from e
