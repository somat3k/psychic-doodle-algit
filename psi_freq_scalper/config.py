"""
Configuration management for Psi-freq Scalper
"""
import os
from typing import List, Optional
from pydantic import BaseModel, Field
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class ExchangeConfig(BaseModel):
    """Exchange connection configuration"""
    api_key: str = Field(default="")
    api_secret: str = Field(default="")
    passphrase: Optional[str] = Field(default=None)
    testnet: bool = Field(default=True)


class TradingConfig(BaseModel):
    """Trading parameters configuration"""
    mode: str = Field(default="paper")  # paper or live
    default_leverage: int = Field(default=5, ge=1, le=100)
    max_leverage: int = Field(default=10, ge=1, le=100)
    pyramiding_levels: int = Field(default=3, ge=1, le=10)
    position_size_percent: float = Field(default=2.0, ge=0.1, le=100.0)
    min_position_size: float = Field(default=10.0, ge=0.0)


class RiskManagementConfig(BaseModel):
    """Risk management parameters"""
    stop_loss_percent: float = Field(default=1.5, ge=0.1, le=50.0)
    take_profit_percent: float = Field(default=3.0, ge=0.1, le=100.0)
    trailing_stop_percent: float = Field(default=0.5, ge=0.1, le=10.0)
    max_daily_loss_percent: float = Field(default=5.0, ge=0.1, le=50.0)


class PsiFreqConfig(BaseModel):
    """Psi-frequency calculation parameters"""
    threshold: float = Field(default=0.7, ge=0.0, le=1.0)
    trajectory_window: int = Field(default=20, ge=5, le=200)
    sensitivity: float = Field(default=1.5, ge=0.1, le=10.0)


class MLConfig(BaseModel):
    """Machine learning model configuration"""
    model_update_interval: int = Field(default=3600, ge=60)
    feature_window: int = Field(default=100, ge=10, le=1000)
    prediction_threshold: float = Field(default=0.65, ge=0.0, le=1.0)
    model1_path: str = Field(default="models/trend_detector.onnx")
    model2_path: str = Field(default="models/signal_generator.onnx")


class Config(BaseModel):
    """Main configuration class"""
    # Exchange configurations
    hyperliquid: ExchangeConfig = Field(default_factory=ExchangeConfig)
    bitget: ExchangeConfig = Field(default_factory=ExchangeConfig)
    
    # Trading configuration
    trading: TradingConfig = Field(default_factory=TradingConfig)
    
    # Risk management
    risk: RiskManagementConfig = Field(default_factory=RiskManagementConfig)
    
    # Psi-frequency
    psi_freq: PsiFreqConfig = Field(default_factory=PsiFreqConfig)
    
    # ML models
    ml: MLConfig = Field(default_factory=MLConfig)
    
    # Timeframes (in minutes)
    timeframes: List[int] = Field(default=[1, 5, 15, 30, 60, 240])
    
    # Logging
    log_level: str = Field(default="INFO")
    log_file: str = Field(default="logs/psi_freq_scalper.log")

    @classmethod
    def from_env(cls) -> "Config":
        """Create configuration from environment variables"""
        return cls(
            hyperliquid=ExchangeConfig(
                api_key=os.getenv("HYPERLIQUID_API_KEY", ""),
                api_secret=os.getenv("HYPERLIQUID_API_SECRET", ""),
                testnet=os.getenv("HYPERLIQUID_TESTNET", "true").lower() == "true"
            ),
            bitget=ExchangeConfig(
                api_key=os.getenv("BITGET_API_KEY", ""),
                api_secret=os.getenv("BITGET_API_SECRET", ""),
                passphrase=os.getenv("BITGET_PASSPHRASE"),
                testnet=os.getenv("BITGET_TESTNET", "true").lower() == "true"
            ),
            trading=TradingConfig(
                mode=os.getenv("TRADING_MODE", "paper"),
                default_leverage=int(os.getenv("DEFAULT_LEVERAGE", "5")),
                max_leverage=int(os.getenv("MAX_LEVERAGE", "10")),
                pyramiding_levels=int(os.getenv("PYRAMIDING_LEVELS", "3")),
                position_size_percent=float(os.getenv("POSITION_SIZE_PERCENT", "2.0")),
                min_position_size=float(os.getenv("MIN_POSITION_SIZE", "10.0"))
            ),
            risk=RiskManagementConfig(
                stop_loss_percent=float(os.getenv("STOP_LOSS_PERCENT", "1.5")),
                take_profit_percent=float(os.getenv("TAKE_PROFIT_PERCENT", "3.0")),
                trailing_stop_percent=float(os.getenv("TRAILING_STOP_PERCENT", "0.5")),
                max_daily_loss_percent=float(os.getenv("MAX_DAILY_LOSS_PERCENT", "5.0"))
            ),
            psi_freq=PsiFreqConfig(
                threshold=float(os.getenv("PSI_FREQ_THRESHOLD", "0.7")),
                trajectory_window=int(os.getenv("PSI_TRAJECTORY_WINDOW", "20")),
                sensitivity=float(os.getenv("PSI_SENSITIVITY", "1.5"))
            ),
            ml=MLConfig(
                model_update_interval=int(os.getenv("MODEL_UPDATE_INTERVAL", "3600")),
                feature_window=int(os.getenv("FEATURE_WINDOW", "100")),
                prediction_threshold=float(os.getenv("PREDICTION_THRESHOLD", "0.65"))
            ),
            timeframes=[int(x) for x in os.getenv("TIMEFRAMES", "1,5,15,30,60,240").split(",")],
            log_level=os.getenv("LOG_LEVEL", "INFO"),
            log_file=os.getenv("LOG_FILE", "logs/psi_freq_scalper.log")
        )


# Global configuration instance
config = Config.from_env()
