"""
Hyperliquid exchange implementation
"""
from typing import List, Optional, Dict
from datetime import datetime, timedelta
import time
from .base import BaseExchange
from ..core.data_structures import Candle, Order, Position, Trade, PositionSide, OrderSide, OrderType

try:
    from hyperliquid.info import Info
    from hyperliquid.exchange import Exchange
    HYPERLIQUID_AVAILABLE = True
except ImportError:
    HYPERLIQUID_AVAILABLE = False


class HyperliquidExchange(BaseExchange):
    """Hyperliquid exchange implementation"""
    
    def __init__(self, api_key: str, api_secret: str, testnet: bool = True):
        """Initialize Hyperliquid exchange"""
        super().__init__(api_key, api_secret, testnet)
        
        if not HYPERLIQUID_AVAILABLE:
            raise ImportError("hyperliquid-python-sdk not installed. Install with: pip install hyperliquid-python-sdk")
        
        # Initialize Hyperliquid clients
        self.info = Info(testnet=testnet)
        self.exchange = Exchange(
            api_key=api_key,
            secret=api_secret,
            testnet=testnet
        ) if api_key and api_secret else None
    
    def get_candles(self, symbol: str, timeframe: int, limit: int = 100) -> List[Candle]:
        """Get historical candles from Hyperliquid"""
        try:
            # Convert timeframe to Hyperliquid format
            interval = self._convert_timeframe(timeframe)
            
            # Get current timestamp
            end_time = int(time.time() * 1000)
            start_time = end_time - (limit * timeframe * 60 * 1000)
            
            # Fetch candles
            candles_data = self.info.candles(
                symbol=symbol,
                interval=interval,
                start_time=start_time,
                end_time=end_time
            )
            
            candles = []
            for candle_data in candles_data:
                candle = Candle(
                    timestamp=datetime.fromtimestamp(candle_data['t'] / 1000),
                    open=float(candle_data['o']),
                    high=float(candle_data['h']),
                    low=float(candle_data['l']),
                    close=float(candle_data['c']),
                    volume=float(candle_data['v']),
                    timeframe=timeframe
                )
                candles.append(candle)
            
            return candles[-limit:]
        
        except Exception as e:
            print(f"Error fetching candles from Hyperliquid: {e}")
            return []
    
    def place_order(self, order: Order) -> str:
        """Place an order on Hyperliquid"""
        if not self.exchange:
            raise ValueError("Exchange not initialized with credentials")
        
        try:
            # Convert order to Hyperliquid format
            order_params = {
                'symbol': order.symbol,
                'is_buy': order.side == OrderSide.BUY,
                'sz': order.size,
                'limit_px': order.price,
                'reduce_only': False,
            }
            
            if order.order_type == OrderType.MARKET:
                order_params['order_type'] = {'market': {}}
            elif order.order_type == OrderType.LIMIT:
                order_params['order_type'] = {'limit': {'tif': 'Gtc'}}
            
            # Place order
            result = self.exchange.order(order_params)
            
            return result.get('response', {}).get('data', {}).get('statuses', [{}])[0].get('resting', {}).get('oid', '')
        
        except Exception as e:
            print(f"Error placing order on Hyperliquid: {e}")
            return ""
    
    def cancel_order(self, order_id: str, symbol: str) -> bool:
        """Cancel an order on Hyperliquid"""
        if not self.exchange:
            return False
        
        try:
            result = self.exchange.cancel(order_id, symbol)
            return result.get('status') == 'ok'
        except Exception as e:
            print(f"Error canceling order on Hyperliquid: {e}")
            return False
    
    def get_position(self, symbol: str) -> Optional[Position]:
        """Get current position from Hyperliquid"""
        try:
            positions = self.info.user_state(self.api_key)
            
            for pos in positions.get('assetPositions', []):
                if pos['position']['coin'] == symbol:
                    size = float(pos['position']['szi'])
                    if size == 0:
                        return None
                    
                    return Position(
                        symbol=symbol,
                        side=PositionSide.LONG if size > 0 else PositionSide.SHORT,
                        entry_price=float(pos['position']['entryPx']),
                        size=abs(size),
                        leverage=int(pos['position'].get('leverage', {}).get('value', 1)),
                        stop_loss=0.0,  # Need to fetch from orders
                        take_profit=0.0,  # Need to fetch from orders
                        timestamp=datetime.now(),
                        unrealized_pnl=float(pos['position'].get('unrealizedPnl', 0))
                    )
            
            return None
        
        except Exception as e:
            print(f"Error getting position from Hyperliquid: {e}")
            return None
    
    def get_balance(self) -> Dict[str, float]:
        """Get account balance from Hyperliquid"""
        try:
            state = self.info.user_state(self.api_key)
            
            balance = {
                'total': float(state.get('marginSummary', {}).get('accountValue', 0)),
                'available': float(state.get('marginSummary', {}).get('totalMarginUsed', 0)),
            }
            
            return balance
        
        except Exception as e:
            print(f"Error getting balance from Hyperliquid: {e}")
            return {'total': 0.0, 'available': 0.0}
    
    def get_current_price(self, symbol: str) -> float:
        """Get current market price from Hyperliquid"""
        try:
            ticker = self.info.all_mids()
            return float(ticker.get(symbol, 0))
        except Exception as e:
            print(f"Error getting price from Hyperliquid: {e}")
            return 0.0
    
    def _convert_timeframe(self, minutes: int) -> str:
        """Convert timeframe in minutes to Hyperliquid interval format"""
        if minutes == 1:
            return '1m'
        elif minutes == 5:
            return '5m'
        elif minutes == 15:
            return '15m'
        elif minutes == 30:
            return '30m'
        elif minutes == 60:
            return '1h'
        elif minutes == 240:
            return '4h'
        elif minutes == 1440:
            return '1d'
        else:
            return '1m'  # Default to 1 minute
