"""
Main Trading Engine
Orchestrates all components of the Psi-freq Scalper
"""
import time
from datetime import datetime
from typing import Optional
from loguru import logger
from ..config import Config
from ..core.psi_frequency import PsiFrequencyCalculator
from ..data.timeframe_aggregator import TimeframeAggregator, CandleAnalyzer
from ..models.ml_models import TrendDetectorModel, SignalGeneratorModel
from ..strategies.psi_freq_strategy import PsiFreqScalperStrategy
from ..exchanges.base import BaseExchange
from ..exchanges.hyperliquid import HyperliquidExchange
from ..exchanges.bitget import BitgetExchange
from ..exchanges.paper_trading import PaperTradingExchange
from ..core.data_structures import Order, OrderSide, OrderType, PositionSide


class TradingEngine:
    """
    Main trading engine that coordinates all components
    """
    
    def __init__(self, config: Config, symbol: str = "BTC-USDT"):
        """
        Initialize trading engine
        
        Args:
            config: Configuration object
            symbol: Trading symbol
        """
        self.config = config
        self.symbol = symbol
        
        # Setup logging
        logger.add(
            config.log_file,
            rotation="1 day",
            retention="30 days",
            level=config.log_level
        )
        
        logger.info(f"Initializing Psi-freq Scalper for {symbol}")
        
        # Initialize exchange
        self.exchange = self._initialize_exchange()
        
        # Initialize Psi-frequency calculator
        self.psi_calculator = PsiFrequencyCalculator(
            threshold=config.psi_freq.threshold,
            window=config.psi_freq.trajectory_window,
            sensitivity=config.psi_freq.sensitivity
        )
        
        # Initialize timeframe aggregator
        self.timeframe_aggregator = TimeframeAggregator(config.timeframes)
        
        # Initialize ML models
        self.trend_model = TrendDetectorModel(config.ml.model1_path)
        self.signal_model = SignalGeneratorModel(config.ml.model2_path)
        
        # Initialize strategy
        self.strategy = PsiFreqScalperStrategy(
            self.psi_calculator,
            self.trend_model,
            self.signal_model,
            config
        )
        
        # State
        self.is_running = False
        self.daily_pnl = 0.0
        self.daily_trades = 0
        
        logger.info("Trading engine initialized successfully")
    
    def _initialize_exchange(self) -> BaseExchange:
        """Initialize the appropriate exchange based on configuration"""
        if self.config.trading.mode == "paper":
            logger.info("Initializing paper trading mode")
            return PaperTradingExchange(initial_balance=10000.0)
        
        # For live trading, determine which exchange to use
        # Priority: Hyperliquid if configured, otherwise Bitget
        if self.config.hyperliquid.api_key:
            logger.info("Initializing Hyperliquid exchange")
            return HyperliquidExchange(
                api_key=self.config.hyperliquid.api_key,
                api_secret=self.config.hyperliquid.api_secret,
                testnet=self.config.hyperliquid.testnet
            )
        elif self.config.bitget.api_key:
            logger.info("Initializing Bitget exchange")
            return BitgetExchange(
                api_key=self.config.bitget.api_key,
                api_secret=self.config.bitget.api_secret,
                passphrase=self.config.bitget.passphrase or "",
                testnet=self.config.bitget.testnet
            )
        else:
            logger.warning("No exchange credentials provided, using paper trading")
            return PaperTradingExchange(initial_balance=10000.0)
    
    def run(self, duration: Optional[int] = None):
        """
        Run the trading bot
        
        Args:
            duration: Run duration in seconds (None = run indefinitely)
        """
        self.is_running = True
        start_time = time.time()
        
        logger.info("Starting trading bot")
        
        try:
            while self.is_running:
                # Check duration
                if duration and (time.time() - start_time) > duration:
                    logger.info("Duration limit reached, stopping bot")
                    break
                
                # Main trading loop
                self._trading_loop()
                
                # Wait before next iteration (use smallest timeframe)
                sleep_time = min(self.config.timeframes) * 60  # Convert to seconds
                time.sleep(sleep_time)
        
        except KeyboardInterrupt:
            logger.info("Received interrupt signal, stopping bot")
        except Exception as e:
            logger.error(f"Error in trading loop: {e}", exc_info=True)
        finally:
            self.stop()
    
    def _trading_loop(self):
        """Main trading loop iteration"""
        try:
            # Fetch latest candles
            candles = self.exchange.get_candles(
                self.symbol,
                timeframe=min(self.config.timeframes),
                limit=200
            )
            
            if not candles:
                logger.warning("No candles received from exchange")
                return
            
            # Update timeframe aggregator
            for candle in candles[-10:]:  # Process last 10 candles
                self.timeframe_aggregator.add_candle(candle, candle.timeframe)
            
            # Get current position
            current_position = self.exchange.get_position(self.symbol)
            
            # Update position if exists
            if current_position and isinstance(self.exchange, PaperTradingExchange):
                self.exchange.update_positions(self.symbol)
                self.exchange.check_stop_loss_take_profit(self.symbol)
            
            # Analyze market and get signal
            signal = self.strategy.analyze(candles, current_position)
            
            logger.info(f"Signal: {signal.action} | Confidence: {signal.confidence:.2f} | Reason: {signal.reason}")
            
            # Execute signal
            self._execute_signal(signal, current_position)
            
            # Log status
            self._log_status(current_position)
            
        except Exception as e:
            logger.error(f"Error in trading loop: {e}", exc_info=True)
    
    def _execute_signal(self, signal, current_position):
        """Execute trading signal"""
        if signal.action == "hold":
            return
        
        # Get current balance
        balance = self.exchange.get_balance()
        available_balance = balance.get('available', 0)
        
        # Get current price
        current_price = self.exchange.get_current_price(self.symbol)
        
        if signal.action == "buy":
            # Calculate position size
            leverage = self.config.trading.default_leverage
            size = self.strategy.calculate_position_size(available_balance, leverage, current_price)
            
            if size > 0:
                # Create order
                order = Order(
                    symbol=self.symbol,
                    side=OrderSide.BUY,
                    order_type=OrderType.LIMIT,
                    size=size,
                    price=current_price,
                    leverage=leverage
                )
                
                # Place order
                order_id = self.exchange.place_order(order)
                
                if order_id:
                    logger.info(f"Placed BUY order: {order_id} | Size: {size:.4f} | Price: {current_price:.2f}")
                    self.daily_trades += 1
        
        elif signal.action == "sell":
            leverage = self.config.trading.default_leverage
            size = self.strategy.calculate_position_size(available_balance, leverage, current_price)
            
            if size > 0:
                order = Order(
                    symbol=self.symbol,
                    side=OrderSide.SELL,
                    order_type=OrderType.LIMIT,
                    size=size,
                    price=current_price,
                    leverage=leverage
                )
                
                order_id = self.exchange.place_order(order)
                
                if order_id:
                    logger.info(f"Placed SELL order: {order_id} | Size: {size:.4f} | Price: {current_price:.2f}")
                    self.daily_trades += 1
        
        elif signal.action == "close" and current_position:
            # Close position
            close_side = OrderSide.SELL if current_position.side == PositionSide.LONG else OrderSide.BUY
            
            order = Order(
                symbol=self.symbol,
                side=close_side,
                order_type=OrderType.MARKET,
                size=current_position.size
            )
            
            order_id = self.exchange.place_order(order)
            
            if order_id:
                logger.info(f"Closed position: {order_id}")
                self.daily_trades += 1
        
        elif signal.action == "pyramid" and current_position:
            # Add to position (pyramiding)
            leverage = min(current_position.leverage, self.config.trading.max_leverage)
            size = self.strategy.calculate_position_size(available_balance, leverage, current_price) * 0.5
            
            pyramid_side = OrderSide.BUY if current_position.side == PositionSide.LONG else OrderSide.SELL
            
            order = Order(
                symbol=self.symbol,
                side=pyramid_side,
                order_type=OrderType.LIMIT,
                size=size,
                price=current_price,
                leverage=leverage
            )
            
            order_id = self.exchange.place_order(order)
            
            if order_id:
                logger.info(f"Added to position (pyramid): {order_id} | Size: {size:.4f}")
                self.daily_trades += 1
    
    def _log_status(self, current_position):
        """Log current status"""
        balance = self.exchange.get_balance()
        
        status = f"Balance: ${balance.get('total', 0):.2f}"
        
        if current_position:
            status += f" | Position: {current_position.side.value} {current_position.size:.4f} @ ${current_position.entry_price:.2f}"
            status += f" | PnL: ${current_position.unrealized_pnl:.2f}"
        
        status += f" | Daily Trades: {self.daily_trades}"
        
        logger.info(status)
        
        # Check daily loss limit
        if balance.get('unrealized_pnl', 0) < 0:
            loss_pct = abs(balance['unrealized_pnl']) / balance['total'] * 100
            if loss_pct > self.config.risk.max_daily_loss_percent:
                logger.warning(f"Daily loss limit exceeded: {loss_pct:.2f}%")
                self.stop()
    
    def stop(self):
        """Stop the trading bot"""
        self.is_running = False
        logger.info("Trading bot stopped")
        
        # Print final statistics if paper trading
        if isinstance(self.exchange, PaperTradingExchange):
            stats = self.exchange.get_statistics()
            logger.info("=" * 50)
            logger.info("PAPER TRADING STATISTICS")
            logger.info(f"Total Trades: {stats['total_trades']}")
            logger.info(f"Total PnL: ${stats['total_pnl']:.2f}")
            logger.info(f"Total Commission: ${stats['total_commission']:.2f}")
            logger.info(f"Win Rate: {stats['win_rate']:.2f}%")
            logger.info(f"Current Balance: ${stats['current_balance']:.2f}")
            logger.info(f"Total Return: {stats['total_return']:.2f}%")
            logger.info("=" * 50)
