"""
Basic tests for Psi-freq Scalper
"""
import pytest
import numpy as np
from datetime import datetime, timedelta
from psi_freq_scalper.core.data_structures import Candle, Position, Order, OrderSide, OrderType, PositionSide
from psi_freq_scalper.core.psi_frequency import PsiFrequencyCalculator
from psi_freq_scalper.data.timeframe_aggregator import CandleAnalyzer, TimeframeAggregator


def generate_test_candles(n: int = 100, start_price: float = 50000.0) -> list:
    """Generate test candle data"""
    candles = []
    current_price = start_price
    
    for i in range(n):
        # Simulate random price movement
        change = np.random.randn() * 100
        current_price += change
        
        high = current_price + abs(np.random.randn() * 50)
        low = current_price - abs(np.random.randn() * 50)
        open_price = current_price + np.random.randn() * 20
        
        candle = Candle(
            timestamp=datetime.now() - timedelta(minutes=n-i),
            open=open_price,
            high=high,
            low=low,
            close=current_price,
            volume=np.random.uniform(1000, 10000),
            timeframe=1
        )
        candles.append(candle)
    
    return candles


class TestDataStructures:
    """Test core data structures"""
    
    def test_candle_properties(self):
        """Test candle properties calculation"""
        candle = Candle(
            timestamp=datetime.now(),
            open=100.0,
            high=110.0,
            low=95.0,
            close=105.0,
            volume=1000.0,
            timeframe=1
        )
        
        assert candle.body == 5.0
        assert candle.upper_wick == 5.0
        assert candle.lower_wick == 5.0
        assert candle.total_range == 15.0
        assert candle.is_bullish == True
        assert 0 < candle.body_ratio < 1
    
    def test_position_pnl_calculation(self):
        """Test position PnL calculation"""
        position = Position(
            symbol="BTC-USDT",
            side=PositionSide.LONG,
            entry_price=50000.0,
            size=1.0,
            leverage=5,
            stop_loss=49000.0,
            take_profit=51000.0,
            timestamp=datetime.now()
        )
        
        # Test profit
        position.update_pnl(51000.0)
        assert position.unrealized_pnl == 1000.0
        
        # Test loss
        position.update_pnl(49000.0)
        assert position.unrealized_pnl == -1000.0


class TestPsiFrequency:
    """Test Psi-frequency calculator"""
    
    def test_psi_frequency_calculation(self):
        """Test Psi-frequency calculation"""
        calculator = PsiFrequencyCalculator(threshold=0.7, window=20)
        candles = generate_test_candles(50)
        
        psi_freq = calculator.calculate_psi_frequency(candles)
        
        assert 0.0 <= psi_freq <= 1.0
    
    def test_trajectory_calculation(self):
        """Test trajectory calculation"""
        calculator = PsiFrequencyCalculator()
        candles = generate_test_candles(30)
        
        trajectory = calculator.calculate_trajectory(candles)
        
        assert len(trajectory) == len(candles)
        assert isinstance(trajectory, np.ndarray)
    
    def test_trend_swing_detection(self):
        """Test trend swing detection"""
        calculator = PsiFrequencyCalculator(threshold=0.5, window=20)
        candles = generate_test_candles(50)
        
        trend = calculator.detect_trend_swing(candles)
        
        assert trend in ["bullish", "bearish", "neutral"]


class TestCandleAnalyzer:
    """Test candle analyzer"""
    
    def test_candle_features(self):
        """Test candle feature extraction"""
        candle = Candle(
            timestamp=datetime.now(),
            open=100.0,
            high=110.0,
            low=95.0,
            close=105.0,
            volume=1000.0,
            timeframe=1
        )
        
        features = CandleAnalyzer.calculate_candle_features(candle)
        
        assert 'body_size' in features
        assert 'upper_wick' in features
        assert 'body_ratio' in features
        assert 'volume' in features
        assert features['is_bullish'] == 1.0
    
    def test_sequence_features(self):
        """Test sequence feature extraction"""
        candles = generate_test_candles(50)
        
        features = CandleAnalyzer.calculate_sequence_features(candles)
        
        assert 'price_mean' in features
        assert 'volume_mean' in features
        assert 'atr' in features
        assert 'trend_strength' in features


class TestTimeframeAggregator:
    """Test timeframe aggregator"""
    
    def test_aggregation(self):
        """Test candle aggregation to higher timeframe"""
        aggregator = TimeframeAggregator([1, 5, 15])
        base_candles = generate_test_candles(10, start_price=50000.0)
        
        aggregated = aggregator.aggregate_to_timeframe(base_candles, 5)
        
        assert len(aggregated) == len(base_candles) // 5
        assert all(c.timeframe == 5 for c in aggregated)
    
    def test_add_and_get_candles(self):
        """Test adding and retrieving candles"""
        aggregator = TimeframeAggregator([1, 5])
        candles = generate_test_candles(10)
        
        for candle in candles:
            aggregator.add_candle(candle, 1)
        
        retrieved = aggregator.get_candles(1, limit=5)
        assert len(retrieved) == 5


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
