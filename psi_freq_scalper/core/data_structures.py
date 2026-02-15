"""
Data structures for trading
"""
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Optional


class OrderSide(Enum):
    """Order side enumeration"""
    BUY = "buy"
    SELL = "sell"


class OrderType(Enum):
    """Order type enumeration"""
    MARKET = "market"
    LIMIT = "limit"
    STOP_LIMIT = "stop_limit"


class PositionSide(Enum):
    """Position side enumeration"""
    LONG = "long"
    SHORT = "short"


@dataclass
class Candle:
    """
    Candle/Bar data structure
    Represents OHLCV data for a specific timeframe
    """
    timestamp: datetime
    open: float
    high: float
    low: float
    close: float
    volume: float
    timeframe: int  # in minutes
    
    @property
    def body(self) -> float:
        """Candle body size"""
        return abs(self.close - self.open)
    
    @property
    def upper_wick(self) -> float:
        """Upper wick/shadow size"""
        return self.high - max(self.open, self.close)
    
    @property
    def lower_wick(self) -> float:
        """Lower wick/shadow size"""
        return min(self.open, self.close) - self.low
    
    @property
    def total_range(self) -> float:
        """Total price range of the candle"""
        return self.high - self.low
    
    @property
    def is_bullish(self) -> bool:
        """Check if candle is bullish"""
        return self.close > self.open
    
    @property
    def body_ratio(self) -> float:
        """Ratio of body to total range"""
        if self.total_range == 0:
            return 0.0
        return self.body / self.total_range
    
    @property
    def volume_weighted_price(self) -> float:
        """Volume weighted average price"""
        return (self.high + self.low + self.close) / 3


@dataclass
class Position:
    """Trading position"""
    symbol: str
    side: PositionSide
    entry_price: float
    size: float
    leverage: int
    stop_loss: float
    take_profit: float
    timestamp: datetime
    pyramiding_level: int = 0
    unrealized_pnl: float = 0.0
    
    def update_pnl(self, current_price: float):
        """Update unrealized PnL"""
        if self.side == PositionSide.LONG:
            self.unrealized_pnl = (current_price - self.entry_price) * self.size
        else:
            self.unrealized_pnl = (self.entry_price - current_price) * self.size


@dataclass
class Order:
    """Trading order"""
    symbol: str
    side: OrderSide
    order_type: OrderType
    size: float
    price: Optional[float] = None
    stop_price: Optional[float] = None
    leverage: int = 1
    timestamp: Optional[datetime] = None
    order_id: Optional[str] = None


@dataclass
class Trade:
    """Executed trade"""
    trade_id: str
    symbol: str
    side: OrderSide
    price: float
    size: float
    timestamp: datetime
    commission: float = 0.0
    pnl: float = 0.0


@dataclass
class Signal:
    """Trading signal from ML models or strategy"""
    timestamp: datetime
    symbol: str
    action: str  # "buy", "sell", "hold"
    confidence: float  # 0.0 to 1.0
    reason: str
    psi_frequency: float
    trend_strength: float
