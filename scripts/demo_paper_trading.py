"""
Quick demo to test paper trading functionality
"""
from datetime import datetime, timedelta
import numpy as np
from psi_freq_scalper.exchanges.paper_trading import PaperTradingExchange
from psi_freq_scalper.core.data_structures import Candle, Order, OrderSide, OrderType


def generate_demo_candles(n=50, start_price=50000.0):
    """Generate demo candle data"""
    candles = []
    current_price = start_price
    
    for i in range(n):
        # Simulate upward trend with some volatility
        change = np.random.randn() * 200 + 50  # Slight upward bias
        current_price += change
        
        high = current_price + abs(np.random.randn() * 100)
        low = current_price - abs(np.random.randn() * 100)
        open_price = current_price + np.random.randn() * 50
        
        candle = Candle(
            timestamp=datetime.now() - timedelta(minutes=n-i),
            open=open_price,
            high=high,
            low=low,
            close=current_price,
            volume=np.random.uniform(1000, 5000),
            timeframe=1
        )
        candles.append(candle)
    
    return candles


def main():
    print("=" * 60)
    print("PSI-FREQ SCALPER - PAPER TRADING DEMO")
    print("=" * 60)
    
    # Initialize paper trading exchange
    exchange = PaperTradingExchange(initial_balance=10000.0)
    print(f"\n✅ Initialized paper trading with $10,000")
    
    # Generate demo candles
    candles = generate_demo_candles(50)
    exchange.add_candles("BTC-USDT", 1, candles)
    print(f"✅ Generated {len(candles)} demo candles")
    
    # Get initial balance
    balance = exchange.get_balance()
    print(f"\n📊 Initial Balance: ${balance['total']:.2f}")
    
    # Place a BUY order
    current_price = candles[-1].close
    print(f"\n📈 Current Price: ${current_price:.2f}")
    
    buy_order = Order(
        symbol="BTC-USDT",
        side=OrderSide.BUY,
        order_type=OrderType.MARKET,
        size=0.1,
        leverage=5
    )
    
    order_id = exchange.place_order(buy_order)
    print(f"✅ Placed BUY order: {order_id}")
    
    # Check position
    position = exchange.get_position("BTC-USDT")
    if position:
        print(f"\n📍 Position opened:")
        print(f"   Side: {position.side.value}")
        print(f"   Size: {position.size}")
        print(f"   Entry Price: ${position.entry_price:.2f}")
        print(f"   Leverage: {position.leverage}x")
    
    # Simulate price movement
    new_price = current_price * 1.02  # 2% profit
    candles.append(Candle(
        timestamp=datetime.now(),
        open=current_price,
        high=new_price,
        low=current_price * 0.99,
        close=new_price,
        volume=2000.0,
        timeframe=1
    ))
    exchange.add_candles("BTC-USDT", 1, [candles[-1]])
    
    # Update position
    exchange.update_positions("BTC-USDT")
    position = exchange.get_position("BTC-USDT")
    
    print(f"\n📈 Price moved to: ${new_price:.2f} (+2%)")
    if position:
        print(f"💰 Unrealized PnL: ${position.unrealized_pnl:.2f}")
    
    # Close position
    sell_order = Order(
        symbol="BTC-USDT",
        side=OrderSide.SELL,
        order_type=OrderType.MARKET,
        size=0.1
    )
    
    order_id = exchange.place_order(sell_order)
    print(f"\n✅ Closed position: {order_id}")
    
    # Get final balance
    balance = exchange.get_balance()
    print(f"\n📊 Final Balance: ${balance['total']:.2f}")
    
    # Get statistics
    stats = exchange.get_statistics()
    print("\n" + "=" * 60)
    print("TRADING STATISTICS")
    print("=" * 60)
    print(f"Total Trades: {stats['total_trades']}")
    print(f"Total PnL: ${stats['total_pnl']:.2f}")
    print(f"Total Commission: ${stats['total_commission']:.2f}")
    print(f"Current Balance: ${stats['current_balance']:.2f}")
    print(f"Total Return: {stats['total_return']:.2f}%")
    print("=" * 60)
    
    print("\n✅ Paper trading demo completed successfully!")


if __name__ == "__main__":
    main()
