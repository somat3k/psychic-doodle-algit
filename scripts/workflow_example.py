"""
Complete workflow example for Psi-freq Scalper
Demonstrates the full pipeline from data to trading
"""
import sys
from datetime import datetime, timedelta
import numpy as np

# Add to path
sys.path.insert(0, '/home/runner/work/psychic-doodle-algit/psychic-doodle-algit')

from psi_freq_scalper.config import Config
from psi_freq_scalper.core.data_structures import Candle
from psi_freq_scalper.core.psi_frequency import PsiFrequencyCalculator
from psi_freq_scalper.data.timeframe_aggregator import CandleAnalyzer, TimeframeAggregator
from psi_freq_scalper.exchanges.paper_trading import PaperTradingExchange


def generate_realistic_candles(n=200, start_price=50000.0, trend='bullish'):
    """Generate realistic candle data with trend"""
    candles = []
    current_price = start_price
    
    for i in range(n):
        # Add trend bias
        if trend == 'bullish':
            trend_change = np.random.uniform(0, 100)
        elif trend == 'bearish':
            trend_change = np.random.uniform(-100, 0)
        else:
            trend_change = np.random.uniform(-50, 50)
        
        # Add volatility
        volatility = np.random.randn() * 50
        current_price += trend_change + volatility
        current_price = max(current_price, 1000)  # Keep price positive
        
        # Generate OHLC
        high = current_price + abs(np.random.randn() * 100)
        low = current_price - abs(np.random.randn() * 100)
        open_price = low + np.random.uniform(0, high - low)
        
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
    print("=" * 70)
    print("PSI-FREQ SCALPER - COMPLETE WORKFLOW EXAMPLE")
    print("=" * 70)
    
    # Step 1: Configuration
    print("\n[1/6] Loading Configuration...")
    config = Config.from_env()
    print(f"   ✅ Trading mode: {config.trading.mode}")
    print(f"   ✅ Leverage: {config.trading.default_leverage}x")
    print(f"   ✅ Psi-freq threshold: {config.psi_freq.threshold}")
    
    # Step 2: Generate Market Data
    print("\n[2/6] Generating Market Data...")
    candles = generate_realistic_candles(200, trend='bullish')
    print(f"   ✅ Generated {len(candles)} candles")
    print(f"   ✅ Start price: ${candles[0].close:.2f}")
    print(f"   ✅ End price: ${candles[-1].close:.2f}")
    print(f"   ✅ Price change: {((candles[-1].close/candles[0].close - 1) * 100):.2f}%")
    
    # Step 3: Multi-timeframe Analysis
    print("\n[3/6] Multi-timeframe Analysis...")
    aggregator = TimeframeAggregator([1, 5, 15])
    
    for candle in candles:
        aggregator.add_candle(candle, 1)
    
    tf_5min = aggregator.aggregate_to_timeframe(candles, 5)
    tf_15min = aggregator.aggregate_to_timeframe(candles, 15)
    
    print(f"   ✅ 1-minute candles: {len(candles)}")
    print(f"   ✅ 5-minute candles: {len(tf_5min)}")
    print(f"   ✅ 15-minute candles: {len(tf_15min)}")
    
    # Step 4: Psi-frequency Calculation
    print("\n[4/6] Calculating Psi-frequency...")
    psi_calc = PsiFrequencyCalculator(
        threshold=config.psi_freq.threshold,
        window=config.psi_freq.trajectory_window,
        sensitivity=config.psi_freq.sensitivity
    )
    
    psi_freq = psi_calc.calculate_psi_frequency(candles)
    trend = psi_calc.detect_trend_swing(candles)
    trajectory = psi_calc.calculate_trajectory(candles[-50:])
    
    print(f"   ✅ Psi-frequency: {psi_freq:.4f}")
    print(f"   ✅ Detected trend: {trend}")
    print(f"   ✅ Trajectory points: {len(trajectory)}")
    print(f"   ✅ Avg trajectory: {np.mean(trajectory):.2f}")
    
    # Step 5: Feature Extraction
    print("\n[5/6] Feature Extraction...")
    candle_features = [CandleAnalyzer.calculate_candle_features(c) for c in candles[-10:]]
    sequence_features = CandleAnalyzer.calculate_sequence_features(candles[-50:])
    
    print(f"   ✅ Candle features extracted: {len(candle_features)} candles")
    print(f"   ✅ Price trend strength: {sequence_features['trend_strength']:.4f}")
    print(f"   ✅ ATR: ${sequence_features['atr']:.2f}")
    print(f"   ✅ Volatility: {sequence_features['volatility']:.4f}")
    print(f"   ✅ Bullish candles: {int(sequence_features['bullish_candles'])}/{len(candles[-50:])}")
    
    # Step 6: Paper Trading Simulation
    print("\n[6/6] Paper Trading Simulation...")
    exchange = PaperTradingExchange(initial_balance=10000.0)
    exchange.add_candles("BTC-USDT", 1, candles)
    
    print(f"   ✅ Initial balance: ${exchange.get_balance()['total']:.2f}")
    
    # Simulate trading based on signals
    from psi_freq_scalper.core.data_structures import Order, OrderSide, OrderType
    
    if trend == 'bullish' and psi_freq > config.psi_freq.threshold:
        print("   📈 Signal: BUY (Bullish trend + high Psi-freq)")
        
        order = Order(
            symbol="BTC-USDT",
            side=OrderSide.BUY,
            order_type=OrderType.MARKET,
            size=0.1,
            leverage=config.trading.default_leverage
        )
        order_id = exchange.place_order(order)
        print(f"   ✅ Order placed: {order_id}")
        
        position = exchange.get_position("BTC-USDT")
        if position:
            print(f"   ✅ Position: {position.side.value} {position.size} @ ${position.entry_price:.2f}")
    else:
        print("   ⏸️  Signal: HOLD (Conditions not met)")
    
    # Final statistics
    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)
    
    balance = exchange.get_balance()
    print(f"Final Balance: ${balance['total']:.2f}")
    
    if balance.get('unrealized_pnl', 0) != 0:
        print(f"Unrealized PnL: ${balance['unrealized_pnl']:.2f}")
    
    stats = exchange.get_statistics()
    print(f"Total Trades: {stats['total_trades']}")
    if stats['total_trades'] > 0:
        print(f"Total Return: {stats.get('total_return', 0.0):.2f}%")
    
    print("\n✅ Workflow completed successfully!")
    print("=" * 70)


if __name__ == "__main__":
    main()
