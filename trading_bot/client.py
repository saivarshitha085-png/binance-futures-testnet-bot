import time
import hmac
import hashlib
import logging
from typing import Optional

import requests

logger = logging.getLogger("trading_bot.client")


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
        query = '&'.join([f"{k}={params[k]}" for k in sorted(params.keys())])
        signature = hmac.new(self.api_secret.encode('utf-8'), query.encode('utf-8'), hashlib.sha256).hexdigest()
        params['signature'] = signature
        return params

    def place_order(self, symbol: str, side: str, order_type: str, quantity: float, price: Optional[float] = None, recvWindow: int = 5000) -> dict:
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

        # Log request (without signature)
        safe_log = {k: v for k, v in signed.items() if k != 'signature'}
        logger.info('POST %s payload=%s', url, safe_log)

        try:
            resp = requests.post(url, headers=headers, data=signed, timeout=10)
            logger.info('Response status=%s body=%s', resp.status_code, resp.text)
            resp.raise_for_status()
            return resp.json()
        except requests.exceptions.RequestException as e:
            logger.exception('Network/API error while placing order')
            try:
                err_text = e.response.text
            except Exception:
                err_text = str(e)
            raise BinanceAPIError(f'Failed to place order: {err_text}') from e
