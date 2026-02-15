"""
Psi-freq Scalper Trading Strategy
Implements trend swing trading with pyramiding and positive stop loss
"""
from typing import Optional, List
from datetime import datetime
from ..core.data_structures import Candle, Signal, Position, Order, OrderSide, OrderType, PositionSide
from ..core.psi_frequency import PsiFrequencyCalculator
from ..data.timeframe_aggregator import CandleAnalyzer
from ..models.ml_models import TrendDetectorModel, SignalGeneratorModel, FeatureEngineering


class PsiFreqScalperStrategy:
    """
    Main trading strategy combining:
    - Psi-frequency analysis
    - Multi-timeframe trend detection
    - ML-based signal generation
    - Pyramiding with leverage
    - Positive stop loss management
    """
    
    def __init__(
        self,
        psi_calculator: PsiFrequencyCalculator,
        trend_model: TrendDetectorModel,
        signal_model: SignalGeneratorModel,
        config,
        symbol: str = "BTC-USDT"
    ):
        """
        Initialize strategy
        
        Args:
            psi_calculator: Psi-frequency calculator
            trend_model: ML model for trend detection
            signal_model: ML model for signal generation
            config: Configuration object
            symbol: Trading symbol
        """
        self.psi_calculator = psi_calculator
        self.trend_model = trend_model
        self.signal_model = signal_model
        self.config = config
        self.symbol = symbol
        self.feature_engineer = FeatureEngineering()
        
        # Strategy state
        self.last_signal_time = None
        self.entry_prices: List[float] = []
    
    def analyze(self, candles: List[Candle], current_position: Optional[Position] = None) -> Signal:
        """
        Analyze market and generate trading signal
        
        Args:
            candles: List of candles for analysis
            current_position: Current position if any
            
        Returns:
            Trading signal
        """
        if len(candles) < self.config.psi_freq.trajectory_window:
            return self._create_hold_signal(candles, "Insufficient data")
        
        # Calculate Psi-frequency
        psi_freq = self.psi_calculator.calculate_psi_frequency(candles)
        
        # Detect trend swing
        trend = self.psi_calculator.detect_trend_swing(candles)
        
        # Extract features for ML models
        candle_features = [CandleAnalyzer.calculate_candle_features(c) for c in candles[-10:]]
        sequence_features = CandleAnalyzer.calculate_sequence_features(candles[-50:])
        
        # Prepare features for models
        features = self.feature_engineer.extract_features(
            candle_features,
            sequence_features,
            psi_freq
        )
        
        # Get ML predictions
        trend_pred, trend_probs = self.trend_model.predict(features.reshape(1, -1))
        signal_pred, signal_probs = self.signal_model.predict(features.reshape(1, -1))
        
        # Interpret predictions
        trend_strength = float(trend_probs[0].max())
        signal_confidence = float(signal_probs[0].max())
        
        # Generate signal
        if current_position is None:
            # No position - look for entry
            return self._generate_entry_signal(
                candles, trend, psi_freq, trend_strength,
                signal_pred[0], signal_confidence
            )
        else:
            # Has position - check for exit or pyramiding
            return self._generate_exit_or_pyramid_signal(
                candles, current_position, trend, psi_freq,
                trend_strength, signal_pred[0], signal_confidence
            )
    
    def _generate_entry_signal(
        self, candles: List[Candle], trend: str, psi_freq: float,
        trend_strength: float, signal_action: int, signal_confidence: float
    ) -> Signal:
        """Generate entry signal"""
        current_price = candles[-1].close
        
        # Check if signal is strong enough
        if psi_freq < self.config.psi_freq.threshold:
            return self._create_hold_signal(candles, "Psi-frequency too low")
        
        if signal_confidence < self.config.ml.prediction_threshold:
            return self._create_hold_signal(candles, "ML confidence too low")
        
        # Determine action based on trend and ML signal
        # signal_action: 0=hold, 1=buy, 2=sell
        if trend == "bullish" and signal_action == 1:
            return Signal(
                timestamp=datetime.now(),
                symbol=self.symbol,
                action="buy",
                confidence=signal_confidence,
                reason=f"Bullish trend with Psi-freq {psi_freq:.2f}",
                psi_frequency=psi_freq,
                trend_strength=trend_strength
            )
        elif trend == "bearish" and signal_action == 2:
            return Signal(
                timestamp=datetime.now(),
                symbol=self.symbol,
                action="sell",
                confidence=signal_confidence,
                reason=f"Bearish trend with Psi-freq {psi_freq:.2f}",
                psi_frequency=psi_freq,
                trend_strength=trend_strength
            )
        
        return self._create_hold_signal(candles, "No strong signal")
    
    def _generate_exit_or_pyramid_signal(
        self, candles: List[Candle], position: Position, trend: str,
        psi_freq: float, trend_strength: float, signal_action: int,
        signal_confidence: float
    ) -> Signal:
        """Generate exit or pyramiding signal"""
        current_price = candles[-1].close
        
        # Check if trend reversed
        trend_matches_position = (
            (position.side == PositionSide.LONG and trend == "bullish") or
            (position.side == PositionSide.SHORT and trend == "bearish")
        )
        
        if not trend_matches_position or trend == "neutral":
            return Signal(
                timestamp=datetime.now(),
                symbol=position.symbol,
                action="close",
                confidence=0.8,
                reason="Trend reversal detected",
                psi_frequency=psi_freq,
                trend_strength=trend_strength
            )
        
        # Check for pyramiding opportunity
        if position.pyramiding_level < self.config.trading.pyramiding_levels:
            # Check if price moved in favorable direction
            profit_pct = (current_price - position.entry_price) / position.entry_price * 100
            
            if position.side == PositionSide.LONG:
                should_pyramid = profit_pct > 1.0 and signal_action == 1
            else:
                profit_pct = -profit_pct
                should_pyramid = profit_pct > 1.0 and signal_action == 2
            
            if should_pyramid and signal_confidence > self.config.ml.prediction_threshold:
                return Signal(
                    timestamp=datetime.now(),
                    symbol=position.symbol,
                    action="pyramid",
                    confidence=signal_confidence,
                    reason=f"Pyramiding opportunity at level {position.pyramiding_level + 1}",
                    psi_frequency=psi_freq,
                    trend_strength=trend_strength
                )
        
        return self._create_hold_signal(candles, "Holding position")
    
    def _create_hold_signal(self, candles: List[Candle], reason: str) -> Signal:
        """Create a hold signal"""
        return Signal(
            timestamp=datetime.now(),
            symbol="",
            action="hold",
            confidence=0.0,
            reason=reason,
            psi_frequency=0.0,
            trend_strength=0.0
        )
    
    def calculate_position_size(self, balance: float, leverage: int, current_price: float) -> float:
        """
        Calculate position size based on risk management
        
        Args:
            balance: Available balance
            leverage: Leverage to use
            current_price: Current market price
            
        Returns:
            Position size
        """
        # Use percentage of balance for position
        position_value = balance * (self.config.trading.position_size_percent / 100)
        
        # Apply leverage
        position_value *= leverage
        
        # Calculate size
        size = position_value / current_price
        
        # Ensure minimum position size
        if position_value < self.config.trading.min_position_size:
            return 0.0
        
        return size
    
    def calculate_stop_loss(self, entry_price: float, position_side: PositionSide) -> float:
        """
        Calculate stop loss price
        
        Args:
            entry_price: Entry price
            position_side: Position side
            
        Returns:
            Stop loss price
        """
        stop_loss_pct = self.config.risk.stop_loss_percent / 100
        
        if position_side == PositionSide.LONG:
            return entry_price * (1 - stop_loss_pct)
        else:
            return entry_price * (1 + stop_loss_pct)
    
    def calculate_take_profit(self, entry_price: float, position_side: PositionSide) -> float:
        """
        Calculate take profit price
        
        Args:
            entry_price: Entry price
            position_side: Position side
            
        Returns:
            Take profit price
        """
        take_profit_pct = self.config.risk.take_profit_percent / 100
        
        if position_side == PositionSide.LONG:
            return entry_price * (1 + take_profit_pct)
        else:
            return entry_price * (1 - take_profit_pct)
    
    def update_trailing_stop(self, position: Position, current_price: float) -> float:
        """
        Update trailing stop loss to lock in profits
        
        Args:
            position: Current position
            current_price: Current market price
            
        Returns:
            New stop loss price
        """
        trailing_pct = self.config.risk.trailing_stop_percent / 100
        
        if position.side == PositionSide.LONG:
            # For long positions, move stop loss up
            potential_stop = current_price * (1 - trailing_pct)
            
            # Only move stop loss up, never down
            if potential_stop > position.stop_loss:
                # Ensure stop loss stays positive (above break-even)
                if potential_stop > position.entry_price:
                    return potential_stop
        else:
            # For short positions, move stop loss down
            potential_stop = current_price * (1 + trailing_pct)
            
            # Only move stop loss down, never up
            if potential_stop < position.stop_loss or position.stop_loss == 0:
                # Ensure stop loss stays positive (below break-even)
                if potential_stop < position.entry_price:
                    return potential_stop
        
        return position.stop_loss
