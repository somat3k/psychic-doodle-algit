"""
Psi-frequency Calculator
Calculates trajectory for candle column on XY scale (time vs price)
"""
import numpy as np
from typing import List, Tuple
from ..core.data_structures import Candle


class PsiFrequencyCalculator:
    """
    Psi-frequency calculator for trajectory development
    Analyzes candle momentum and price action on XY scale
    """
    
    def __init__(self, threshold: float = 0.7, window: int = 20, sensitivity: float = 1.5):
        """
        Initialize Psi-frequency calculator
        
        Args:
            threshold: Minimum threshold for signal generation
            window: Look-back window for trajectory calculation
            sensitivity: Sensitivity factor for frequency detection
        """
        self.threshold = threshold
        self.window = window
        self.sensitivity = sensitivity
    
    def calculate_trajectory(self, candles: List[Candle]) -> np.ndarray:
        """
        Calculate price trajectory on XY scale
        
        Args:
            candles: List of candle data
            
        Returns:
            Array of trajectory values
        """
        if len(candles) < 2:
            return np.array([0.0])
        
        # Extract price and time data
        prices = np.array([c.close for c in candles])
        times = np.arange(len(candles))
        
        # Calculate velocity (price change rate)
        velocity = np.diff(prices)
        velocity = np.concatenate([[0], velocity])
        
        # Calculate acceleration (rate of velocity change)
        acceleration = np.diff(velocity)
        acceleration = np.concatenate([[0], acceleration])
        
        # Combine velocity and acceleration for trajectory
        trajectory = velocity + (acceleration * self.sensitivity)
        
        return trajectory
    
    def calculate_psi_frequency(self, candles: List[Candle]) -> float:
        """
        Calculate Psi-frequency value for current market state
        
        Args:
            candles: List of candle data
            
        Returns:
            Psi-frequency value (0.0 to 1.0+)
        """
        if len(candles) < self.window:
            return 0.0
        
        # Use last 'window' candles
        recent_candles = candles[-self.window:]
        
        # Calculate trajectory
        trajectory = self.calculate_trajectory(recent_candles)
        
        # Calculate frequency components
        price_momentum = self._calculate_price_momentum(recent_candles)
        volume_momentum = self._calculate_volume_momentum(recent_candles)
        wave_strength = self._calculate_wave_strength(recent_candles)
        
        # Combine components with weights
        psi_freq = (
            price_momentum * 0.4 +
            volume_momentum * 0.3 +
            wave_strength * 0.3
        )
        
        # Normalize to 0-1 range
        psi_freq = np.clip(psi_freq, 0.0, 1.0)
        
        return float(psi_freq)
    
    def _calculate_price_momentum(self, candles: List[Candle]) -> float:
        """Calculate price momentum component"""
        prices = np.array([c.close for c in candles])
        
        # Calculate momentum as normalized rate of change
        returns = np.diff(prices) / prices[:-1]
        momentum = np.mean(np.abs(returns))
        
        # Apply sensitivity
        momentum *= self.sensitivity
        
        return float(momentum)
    
    def _calculate_volume_momentum(self, candles: List[Candle]) -> float:
        """Calculate volume momentum component"""
        volumes = np.array([c.volume for c in candles])
        
        if np.sum(volumes) == 0:
            return 0.0
        
        # Calculate volume-weighted momentum
        prices = np.array([c.close for c in candles])
        volume_weights = volumes / np.sum(volumes)
        
        weighted_price_change = np.sum(np.abs(np.diff(prices)) * volume_weights[1:])
        
        return float(weighted_price_change)
    
    def _calculate_wave_strength(self, candles: List[Candle]) -> float:
        """Calculate wave form strength"""
        highs = np.array([c.high for c in candles])
        lows = np.array([c.low for c in candles])
        
        # Calculate wave amplitude
        wave_amplitude = highs - lows
        avg_amplitude = np.mean(wave_amplitude)
        
        # Calculate wave consistency (lower std = more consistent)
        wave_std = np.std(wave_amplitude)
        
        if avg_amplitude == 0:
            return 0.0
        
        # Strength is amplitude with penalty for inconsistency
        consistency_factor = 1.0 / (1.0 + wave_std / avg_amplitude)
        strength = (avg_amplitude / highs[-1]) * consistency_factor
        
        return float(strength)
    
    def calculate_xy_coordinates(self, candles: List[Candle]) -> Tuple[np.ndarray, np.ndarray]:
        """
        Calculate XY coordinates for trajectory visualization
        
        Args:
            candles: List of candle data
            
        Returns:
            Tuple of (x_coords, y_coords)
        """
        x_coords = np.arange(len(candles))
        y_coords = np.array([c.close for c in candles])
        
        return x_coords, y_coords
    
    def detect_trend_swing(self, candles: List[Candle]) -> str:
        """
        Detect trend swing based on Psi-frequency
        
        Args:
            candles: List of candle data
            
        Returns:
            Trend direction: "bullish", "bearish", or "neutral"
        """
        if len(candles) < self.window:
            return "neutral"
        
        psi_freq = self.calculate_psi_frequency(candles)
        trajectory = self.calculate_trajectory(candles[-self.window:])
        
        # Analyze trajectory direction
        recent_trajectory = trajectory[-5:]  # Last 5 points
        avg_trajectory = np.mean(recent_trajectory)
        
        if psi_freq > self.threshold and avg_trajectory > 0:
            return "bullish"
        elif psi_freq > self.threshold and avg_trajectory < 0:
            return "bearish"
        else:
            return "neutral"
