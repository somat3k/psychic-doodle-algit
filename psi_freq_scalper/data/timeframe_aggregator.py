"""
Multi-timeframe analysis module
Aggregates and analyzes data across multiple timeframes
"""
from typing import List, Dict
from datetime import datetime, timedelta
import numpy as np
from ..core.data_structures import Candle


class TimeframeAggregator:
    """
    Aggregates candle data across multiple timeframes
    """
    
    def __init__(self, timeframes: List[int]):
        """
        Initialize aggregator
        
        Args:
            timeframes: List of timeframes in minutes (e.g., [1, 5, 15, 30, 60])
        """
        self.timeframes = sorted(timeframes)
        self.candle_buffers: Dict[int, List[Candle]] = {tf: [] for tf in timeframes}
    
    def add_candle(self, candle: Candle, timeframe: int):
        """Add a candle to the buffer for a specific timeframe"""
        if timeframe in self.candle_buffers:
            self.candle_buffers[timeframe].append(candle)
    
    def aggregate_to_timeframe(self, base_candles: List[Candle], target_timeframe: int) -> List[Candle]:
        """
        Aggregate base timeframe candles to a higher timeframe
        
        Args:
            base_candles: List of base candles (e.g., 1-minute)
            target_timeframe: Target timeframe in minutes
            
        Returns:
            List of aggregated candles
        """
        if not base_candles:
            return []
        
        base_timeframe = base_candles[0].timeframe
        ratio = target_timeframe // base_timeframe
        
        if ratio <= 1:
            return base_candles
        
        aggregated = []
        
        for i in range(0, len(base_candles), ratio):
            chunk = base_candles[i:i + ratio]
            if len(chunk) == ratio:  # Only aggregate complete periods
                agg_candle = self._aggregate_candle_group(chunk, target_timeframe)
                aggregated.append(agg_candle)
        
        return aggregated
    
    def _aggregate_candle_group(self, candles: List[Candle], timeframe: int) -> Candle:
        """Aggregate a group of candles into one"""
        return Candle(
            timestamp=candles[0].timestamp,
            open=candles[0].open,
            high=max(c.high for c in candles),
            low=min(c.low for c in candles),
            close=candles[-1].close,
            volume=sum(c.volume for c in candles),
            timeframe=timeframe
        )
    
    def get_candles(self, timeframe: int, limit: int = 100) -> List[Candle]:
        """Get candles for a specific timeframe"""
        if timeframe not in self.candle_buffers:
            return []
        return self.candle_buffers[timeframe][-limit:]


class CandleAnalyzer:
    """
    Analyzes candle patterns and characteristics
    """
    
    @staticmethod
    def calculate_candle_features(candle: Candle) -> Dict[str, float]:
        """
        Calculate comprehensive features from a candle
        
        Returns:
            Dictionary of candle features
        """
        features = {
            'body_size': candle.body,
            'upper_wick': candle.upper_wick,
            'lower_wick': candle.lower_wick,
            'total_range': candle.total_range,
            'body_ratio': candle.body_ratio,
            'is_bullish': float(candle.is_bullish),
            'volume': candle.volume,
            'vwap': candle.volume_weighted_price,
            'high_low_ratio': candle.high / candle.low if candle.low > 0 else 0,
        }
        
        # Wick ratios
        if candle.total_range > 0:
            features['upper_wick_ratio'] = candle.upper_wick / candle.total_range
            features['lower_wick_ratio'] = candle.lower_wick / candle.total_range
        else:
            features['upper_wick_ratio'] = 0.0
            features['lower_wick_ratio'] = 0.0
        
        return features
    
    @staticmethod
    def calculate_sequence_features(candles: List[Candle]) -> Dict[str, float]:
        """
        Calculate features from a sequence of candles
        
        Returns:
            Dictionary of sequence features
        """
        if not candles:
            return {}
        
        closes = np.array([c.close for c in candles])
        volumes = np.array([c.volume for c in candles])
        highs = np.array([c.high for c in candles])
        lows = np.array([c.low for c in candles])
        
        features = {
            # Price features
            'price_mean': float(np.mean(closes)),
            'price_std': float(np.std(closes)),
            'price_range': float(np.max(closes) - np.min(closes)),
            'price_change': float(closes[-1] - closes[0]),
            'price_change_pct': float((closes[-1] - closes[0]) / closes[0] * 100) if closes[0] > 0 else 0,
            
            # Volume features
            'volume_mean': float(np.mean(volumes)),
            'volume_std': float(np.std(volumes)),
            'volume_trend': float(np.polyfit(range(len(volumes)), volumes, 1)[0]) if len(volumes) > 1 else 0,
            
            # Volatility features
            'atr': CandleAnalyzer._calculate_atr(candles),
            'volatility': float(np.std(np.diff(closes) / closes[:-1])) if len(closes) > 1 else 0,
            
            # Trend features
            'trend_strength': CandleAnalyzer._calculate_trend_strength(closes),
            'higher_highs': float(sum(1 for i in range(1, len(highs)) if highs[i] > highs[i-1])),
            'lower_lows': float(sum(1 for i in range(1, len(lows)) if lows[i] < lows[i-1])),
            
            # Pattern features
            'bullish_candles': float(sum(1 for c in candles if c.is_bullish)),
            'bearish_candles': float(sum(1 for c in candles if not c.is_bullish)),
        }
        
        return features
    
    @staticmethod
    def _calculate_atr(candles: List[Candle], period: int = 14) -> float:
        """Calculate Average True Range"""
        if len(candles) < 2:
            return 0.0
        
        true_ranges = []
        for i in range(1, len(candles)):
            high = candles[i].high
            low = candles[i].low
            prev_close = candles[i-1].close
            
            tr = max(
                high - low,
                abs(high - prev_close),
                abs(low - prev_close)
            )
            true_ranges.append(tr)
        
        if not true_ranges:
            return 0.0
        
        # Use last 'period' values or all if less
        recent_tr = true_ranges[-min(period, len(true_ranges)):]
        return float(np.mean(recent_tr))
    
    @staticmethod
    def _calculate_trend_strength(prices: np.ndarray) -> float:
        """Calculate trend strength using linear regression R-squared"""
        if len(prices) < 2:
            return 0.0
        
        x = np.arange(len(prices))
        
        # Linear regression
        coeffs = np.polyfit(x, prices, 1)
        y_pred = np.polyval(coeffs, x)
        
        # Calculate R-squared
        ss_res = np.sum((prices - y_pred) ** 2)
        ss_tot = np.sum((prices - np.mean(prices)) ** 2)
        
        if ss_tot == 0:
            return 0.0
        
        r_squared = 1 - (ss_res / ss_tot)
        
        # Direction-aware: positive for uptrend, negative for downtrend
        direction = np.sign(coeffs[0])
        
        return float(r_squared * direction)
