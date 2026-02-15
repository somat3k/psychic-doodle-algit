"""
Bitget exchange implementation
"""
from typing import List, Optional, Dict
from datetime import datetime, timedelta
import time
import hmac
import hashlib
import base64
import requests
from .base import BaseExchange
from ..core.data_structures import Candle, Order, Position, Trade, PositionSide, OrderSide, OrderType


class BitgetExchange(BaseExchange):
    """Bitget exchange implementation using pybit library"""
    
    def __init__(self, api_key: str, api_secret: str, passphrase: str = "", testnet: bool = True):
        """Initialize Bitget exchange"""
        super().__init__(api_key, api_secret, testnet)
        self.passphrase = passphrase
        
        # Set base URL
        if testnet:
            self.base_url = "https://api.bitget.com"  # Bitget doesn't have a separate testnet URL
        else:
            self.base_url = "https://api.bitget.com"
        
        self.session = requests.Session()
    
    def _sign_request(self, timestamp: str, method: str, request_path: str, body: str = "") -> str:
        """Sign request for Bitget API"""
        message = timestamp + method + request_path + body
        mac = hmac.new(
            bytes(self.api_secret, encoding='utf8'),
            bytes(message, encoding='utf-8'),
            digestmod=hashlib.sha256
        )
        return base64.b64encode(mac.digest()).decode()
    
    def _get_headers(self, method: str, request_path: str, body: str = "") -> Dict[str, str]:
        """Get headers for API request"""
        timestamp = str(int(time.time() * 1000))
        sign = self._sign_request(timestamp, method, request_path, body)
        
        return {
            'ACCESS-KEY': self.api_key,
            'ACCESS-SIGN': sign,
            'ACCESS-TIMESTAMP': timestamp,
            'ACCESS-PASSPHRASE': self.passphrase,
            'Content-Type': 'application/json',
        }
    
    def get_candles(self, symbol: str, timeframe: int, limit: int = 100) -> List[Candle]:
        """Get historical candles from Bitget"""
        try:
            # Convert timeframe to Bitget format
            interval = self._convert_timeframe(timeframe)
            
            # Prepare request
            endpoint = f"/api/mix/v1/market/candles"
            params = {
                'symbol': symbol,
                'granularity': interval,
                'limit': limit
            }
            
            # Make request
            response = self.session.get(
                f"{self.base_url}{endpoint}",
                params=params
            )
            
            if response.status_code != 200:
                print(f"Error fetching candles: {response.text}")
                return []
            
            data = response.json()
            
            if data.get('code') != '00000':
                print(f"API error: {data.get('msg')}")
                return []
            
            candles = []
            for candle_data in data.get('data', []):
                candle = Candle(
                    timestamp=datetime.fromtimestamp(int(candle_data[0]) / 1000),
                    open=float(candle_data[1]),
                    high=float(candle_data[2]),
                    low=float(candle_data[3]),
                    close=float(candle_data[4]),
                    volume=float(candle_data[5]),
                    timeframe=timeframe
                )
                candles.append(candle)
            
            return candles[-limit:]
        
        except Exception as e:
            print(f"Error fetching candles from Bitget: {e}")
            return []
    
    def place_order(self, order: Order) -> str:
        """Place an order on Bitget"""
        try:
            endpoint = "/api/mix/v1/order/placeOrder"
            
            # Prepare order data
            order_data = {
                'symbol': order.symbol,
                'marginCoin': 'USDT',  # Default margin coin
                'side': 'open_long' if order.side == OrderSide.BUY else 'open_short',
                'orderType': 'market' if order.order_type == OrderType.MARKET else 'limit',
                'size': str(order.size),
            }
            
            if order.price:
                order_data['price'] = str(order.price)
            
            if order.leverage:
                order_data['leverage'] = str(order.leverage)
            
            body = str(order_data)
            headers = self._get_headers('POST', endpoint, body)
            
            # Place order
            response = self.session.post(
                f"{self.base_url}{endpoint}",
                json=order_data,
                headers=headers
            )
            
            if response.status_code != 200:
                print(f"Error placing order: {response.text}")
                return ""
            
            data = response.json()
            
            if data.get('code') != '00000':
                print(f"API error: {data.get('msg')}")
                return ""
            
            return data.get('data', {}).get('orderId', '')
        
        except Exception as e:
            print(f"Error placing order on Bitget: {e}")
            return ""
    
    def cancel_order(self, order_id: str, symbol: str) -> bool:
        """Cancel an order on Bitget"""
        try:
            endpoint = "/api/mix/v1/order/cancel-order"
            
            order_data = {
                'symbol': symbol,
                'orderId': order_id,
                'marginCoin': 'USDT',
            }
            
            body = str(order_data)
            headers = self._get_headers('POST', endpoint, body)
            
            response = self.session.post(
                f"{self.base_url}{endpoint}",
                json=order_data,
                headers=headers
            )
            
            if response.status_code != 200:
                return False
            
            data = response.json()
            return data.get('code') == '00000'
        
        except Exception as e:
            print(f"Error canceling order on Bitget: {e}")
            return False
    
    def get_position(self, symbol: str) -> Optional[Position]:
        """Get current position from Bitget"""
        try:
            endpoint = f"/api/mix/v1/position/singlePosition"
            params = {
                'symbol': symbol,
                'marginCoin': 'USDT',
            }
            
            headers = self._get_headers('GET', endpoint)
            
            response = self.session.get(
                f"{self.base_url}{endpoint}",
                params=params,
                headers=headers
            )
            
            if response.status_code != 200:
                return None
            
            data = response.json()
            
            if data.get('code') != '00000':
                return None
            
            pos_data = data.get('data', [])
            if not pos_data:
                return None
            
            pos = pos_data[0]
            total = float(pos.get('total', 0))
            
            if total == 0:
                return None
            
            return Position(
                symbol=symbol,
                side=PositionSide.LONG if pos.get('holdSide') == 'long' else PositionSide.SHORT,
                entry_price=float(pos.get('averageOpenPrice', 0)),
                size=total,
                leverage=int(pos.get('leverage', 1)),
                stop_loss=0.0,
                take_profit=0.0,
                timestamp=datetime.now(),
                unrealized_pnl=float(pos.get('unrealizedPL', 0))
            )
        
        except Exception as e:
            print(f"Error getting position from Bitget: {e}")
            return None
    
    def get_balance(self) -> Dict[str, float]:
        """Get account balance from Bitget"""
        try:
            endpoint = "/api/mix/v1/account/accounts"
            params = {'productType': 'umcbl'}  # USDT-M futures
            
            headers = self._get_headers('GET', endpoint)
            
            response = self.session.get(
                f"{self.base_url}{endpoint}",
                params=params,
                headers=headers
            )
            
            if response.status_code != 200:
                return {'total': 0.0, 'available': 0.0}
            
            data = response.json()
            
            if data.get('code') != '00000':
                return {'total': 0.0, 'available': 0.0}
            
            accounts = data.get('data', [])
            if not accounts:
                return {'total': 0.0, 'available': 0.0}
            
            account = accounts[0]
            
            return {
                'total': float(account.get('equity', 0)),
                'available': float(account.get('available', 0)),
            }
        
        except Exception as e:
            print(f"Error getting balance from Bitget: {e}")
            return {'total': 0.0, 'available': 0.0}
    
    def get_current_price(self, symbol: str) -> float:
        """Get current market price from Bitget"""
        try:
            endpoint = "/api/mix/v1/market/ticker"
            params = {'symbol': symbol}
            
            response = self.session.get(
                f"{self.base_url}{endpoint}",
                params=params
            )
            
            if response.status_code != 200:
                return 0.0
            
            data = response.json()
            
            if data.get('code') != '00000':
                return 0.0
            
            ticker = data.get('data', {})
            return float(ticker.get('last', 0))
        
        except Exception as e:
            print(f"Error getting price from Bitget: {e}")
            return 0.0
    
    def _convert_timeframe(self, minutes: int) -> str:
        """Convert timeframe in minutes to Bitget granularity format"""
        if minutes == 1:
            return '1m'
        elif minutes == 5:
            return '5m'
        elif minutes == 15:
            return '15m'
        elif minutes == 30:
            return '30m'
        elif minutes == 60:
            return '1H'
        elif minutes == 240:
            return '4H'
        elif minutes == 1440:
            return '1D'
        else:
            return '1m'  # Default to 1 minute
