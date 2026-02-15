"""
Base exchange interface
"""
from abc import ABC, abstractmethod
from typing import List, Optional, Dict
from datetime import datetime
from ..core.data_structures import Candle, Order, Position, Trade


class BaseExchange(ABC):
    """Base class for exchange implementations"""
    
    def __init__(self, api_key: str, api_secret: str, testnet: bool = True):
        """
        Initialize exchange
        
        Args:
            api_key: API key
            api_secret: API secret
            testnet: Use testnet if True
        """
        self.api_key = api_key
        self.api_secret = api_secret
        self.testnet = testnet
    
    @abstractmethod
    def get_candles(self, symbol: str, timeframe: int, limit: int = 100) -> List[Candle]:
        """
        Get historical candles
        
        Args:
            symbol: Trading symbol
            timeframe: Timeframe in minutes
            limit: Number of candles to fetch
            
        Returns:
            List of candles
        """
        pass
    
    @abstractmethod
    def place_order(self, order: Order) -> str:
        """
        Place an order
        
        Args:
            order: Order object
            
        Returns:
            Order ID
        """
        pass
    
    @abstractmethod
    def cancel_order(self, order_id: str, symbol: str) -> bool:
        """
        Cancel an order
        
        Args:
            order_id: Order ID to cancel
            symbol: Trading symbol
            
        Returns:
            True if successful
        """
        pass
    
    @abstractmethod
    def get_position(self, symbol: str) -> Optional[Position]:
        """
        Get current position
        
        Args:
            symbol: Trading symbol
            
        Returns:
            Position object or None
        """
        pass
    
    @abstractmethod
    def get_balance(self) -> Dict[str, float]:
        """
        Get account balance
        
        Returns:
            Dictionary of balances
        """
        pass
    
    @abstractmethod
    def get_current_price(self, symbol: str) -> float:
        """
        Get current market price
        
        Args:
            symbol: Trading symbol
            
        Returns:
            Current price
        """
        pass
