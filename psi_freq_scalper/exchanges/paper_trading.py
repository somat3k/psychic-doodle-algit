"""
Paper trading simulator
"""
from typing import List, Optional, Dict
from datetime import datetime
from ..exchanges.base import BaseExchange
from ..core.data_structures import Candle, Order, Position, Trade, PositionSide, OrderSide, OrderType


class PaperTradingExchange(BaseExchange):
    """
    Paper trading exchange simulator
    Simulates order execution without real money
    """
    
    def __init__(self, initial_balance: float = 10000.0):
        """
        Initialize paper trading exchange
        
        Args:
            initial_balance: Starting balance for simulation
        """
        super().__init__("", "", testnet=True)
        self.balance = initial_balance
        self.initial_balance = initial_balance
        self.positions: Dict[str, Position] = {}
        self.orders: Dict[str, Order] = {}
        self.trades: List[Trade] = []
        self.order_counter = 0
        self.candle_cache: Dict[str, List[Candle]] = {}
    
    def get_candles(self, symbol: str, timeframe: int, limit: int = 100) -> List[Candle]:
        """Get simulated candles (must be provided externally)"""
        key = f"{symbol}_{timeframe}"
        return self.candle_cache.get(key, [])[-limit:]
    
    def add_candles(self, symbol: str, timeframe: int, candles: List[Candle]):
        """Add candles to cache for simulation"""
        key = f"{symbol}_{timeframe}"
        if key not in self.candle_cache:
            self.candle_cache[key] = []
        self.candle_cache[key].extend(candles)
    
    def place_order(self, order: Order) -> str:
        """Simulate order placement"""
        self.order_counter += 1
        order_id = f"paper_{self.order_counter}"
        order.order_id = order_id
        order.timestamp = datetime.now()
        
        # Simulate immediate execution for market orders
        if order.order_type == OrderType.MARKET:
            current_price = self.get_current_price(order.symbol)
            self._execute_order(order, current_price)
        else:
            self.orders[order_id] = order
        
        return order_id
    
    def cancel_order(self, order_id: str, symbol: str) -> bool:
        """Cancel a pending order"""
        if order_id in self.orders:
            del self.orders[order_id]
            return True
        return False
    
    def get_position(self, symbol: str) -> Optional[Position]:
        """Get current position for symbol"""
        return self.positions.get(symbol)
    
    def get_balance(self) -> Dict[str, float]:
        """Get account balance"""
        # Calculate total equity including unrealized PnL
        total_pnl = sum(pos.unrealized_pnl for pos in self.positions.values())
        
        return {
            'total': self.balance + total_pnl,
            'available': self.balance,
            'unrealized_pnl': total_pnl,
        }
    
    def get_current_price(self, symbol: str) -> float:
        """Get current market price from cached candles"""
        candles = self.get_candles(symbol, 1, 1)
        if candles:
            return candles[-1].close
        return 0.0
    
    def _execute_order(self, order: Order, price: float):
        """Execute an order at given price"""
        # Calculate commission (0.1% for simulation)
        commission = order.size * price * 0.001
        
        # Check if we have enough balance
        required_margin = (order.size * price) / order.leverage
        if required_margin + commission > self.balance:
            print(f"Insufficient balance for order: {order}")
            return
        
        # Update balance
        self.balance -= commission
        
        # Handle position
        if order.symbol in self.positions:
            self._update_position(order, price)
        else:
            self._open_position(order, price)
        
        # Record trade
        trade = Trade(
            trade_id=f"trade_{len(self.trades) + 1}",
            symbol=order.symbol,
            side=order.side,
            price=price,
            size=order.size,
            timestamp=datetime.now(),
            commission=commission
        )
        self.trades.append(trade)
    
    def _open_position(self, order: Order, price: float):
        """Open a new position"""
        position = Position(
            symbol=order.symbol,
            side=PositionSide.LONG if order.side == OrderSide.BUY else PositionSide.SHORT,
            entry_price=price,
            size=order.size,
            leverage=order.leverage,
            stop_loss=0.0,
            take_profit=0.0,
            timestamp=datetime.now()
        )
        self.positions[order.symbol] = position
    
    def _update_position(self, order: Order, price: float):
        """Update existing position (add or reduce)"""
        position = self.positions[order.symbol]
        
        # Check if closing position
        is_closing = (
            (position.side == PositionSide.LONG and order.side == OrderSide.SELL) or
            (position.side == PositionSide.SHORT and order.side == OrderSide.BUY)
        )
        
        if is_closing:
            # Close or reduce position
            if order.size >= position.size:
                # Full close
                pnl = self._calculate_pnl(position, price)
                self.balance += pnl
                del self.positions[order.symbol]
            else:
                # Partial close
                pnl = self._calculate_pnl(position, price) * (order.size / position.size)
                self.balance += pnl
                position.size -= order.size
        else:
            # Add to position (pyramiding)
            total_size = position.size + order.size
            position.entry_price = (
                (position.entry_price * position.size + price * order.size) / total_size
            )
            position.size = total_size
            position.pyramiding_level += 1
    
    def _calculate_pnl(self, position: Position, exit_price: float) -> float:
        """Calculate profit/loss for position"""
        if position.side == PositionSide.LONG:
            pnl = (exit_price - position.entry_price) * position.size
        else:
            pnl = (position.entry_price - exit_price) * position.size
        
        return pnl
    
    def update_positions(self, symbol: str):
        """Update position unrealized PnL"""
        if symbol in self.positions:
            current_price = self.get_current_price(symbol)
            self.positions[symbol].update_pnl(current_price)
    
    def check_stop_loss_take_profit(self, symbol: str):
        """Check and execute stop loss / take profit"""
        if symbol not in self.positions:
            return
        
        position = self.positions[symbol]
        current_price = self.get_current_price(symbol)
        
        should_close = False
        
        # Check stop loss
        if position.stop_loss > 0:
            if position.side == PositionSide.LONG and current_price <= position.stop_loss:
                should_close = True
            elif position.side == PositionSide.SHORT and current_price >= position.stop_loss:
                should_close = True
        
        # Check take profit
        if position.take_profit > 0:
            if position.side == PositionSide.LONG and current_price >= position.take_profit:
                should_close = True
            elif position.side == PositionSide.SHORT and current_price <= position.take_profit:
                should_close = True
        
        if should_close:
            # Close position
            close_order = Order(
                symbol=symbol,
                side=OrderSide.SELL if position.side == PositionSide.LONG else OrderSide.BUY,
                order_type=OrderType.MARKET,
                size=position.size
            )
            self._execute_order(close_order, current_price)
    
    def get_statistics(self) -> Dict[str, float]:
        """Get trading statistics"""
        if not self.trades:
            return {
                'total_trades': 0,
                'total_pnl': 0.0,
                'total_commission': 0.0,
                'win_rate': 0.0,
            }
        
        total_pnl = sum(t.pnl for t in self.trades)
        total_commission = sum(t.commission for t in self.trades)
        winning_trades = sum(1 for t in self.trades if t.pnl > 0)
        
        return {
            'total_trades': len(self.trades),
            'total_pnl': total_pnl,
            'total_commission': total_commission,
            'win_rate': winning_trades / len(self.trades) * 100 if self.trades else 0,
            'current_balance': self.balance,
            'total_return': (self.balance - self.initial_balance) / self.initial_balance * 100,
        }
