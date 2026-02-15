# Psi-freq Scalper Trading Bot

**Advanced algorithmic trading bot** based on Psi-frequency analysis, trend swing detection, and machine learning models for cryptocurrency trading.

## 🚀 Features

- **Multi-Exchange Support**: Hyperliquid and Bitget SDK integration
- **Dual ML Models**: Two ONNX-exported XGBoost models for trend detection and signal generation
- **Psi-frequency Analysis**: Advanced trajectory calculation on XY scale (time vs price)
- **Multi-Timeframe Analysis**: Combines data from 1m, 5m, 15m, 30m, 1h, and 4h timeframes
- **Intelligent Position Management**: 
  - Leverage control (5-10x)
  - Pyramiding strategy (up to 3 levels)
  - Positive stop loss management
  - Trailing stop loss to lock profits
- **Risk Management**:
  - Configurable stop loss and take profit
  - Daily loss limits
  - Position sizing based on account balance
- **Two Trading Modes**:
  - **Paper Trading**: Risk-free simulation with virtual money
  - **Live Trading**: Real broker execution (use with caution)

## 📋 Prerequisites

**IMPORTANT**: Before starting, you must:
1. Read `TODO.md` completely
2. Run validation: `python scripts/validate_setup.py`
3. Configure API keys in `config/.env`
4. Install all dependencies

## 🛠️ Installation

1. **Clone the repository**
```bash
git clone https://github.com/somat3k/psychic-doodle-algit.git
cd psychic-doodle-algit
```

2. **Install dependencies**
```bash
pip install -r requirements.txt
```

3. **Configure environment**
```bash
cp config/.env.example config/.env
# Edit config/.env with your API keys and settings
```

4. **Validate setup**
```bash
python scripts/validate_setup.py
```

## 🎯 Quick Start

### Paper Trading (Recommended for Testing)
```bash
python main.py --symbol BTC-USDT --mode paper
```

### Live Trading (Real Money - Use with Caution!)
```bash
python main.py --symbol BTC-USDT --mode live
```

### Run for Specific Duration
```bash
python main.py --symbol BTC-USDT --mode paper --duration 3600
```

## 📚 Project Structure

```
psychic-doodle-algit/
├── psi_freq_scalper/
│   ├── core/
│   │   ├── data_structures.py    # Core data types (Candle, Position, Order, etc.)
│   │   ├── psi_frequency.py      # Psi-frequency calculator
│   │   └── engine.py             # Main trading engine
│   ├── models/
│   │   └── ml_models.py          # XGBoost ML models with ONNX export
│   ├── strategies/
│   │   └── psi_freq_strategy.py  # Main trading strategy
│   ├── exchanges/
│   │   ├── base.py               # Base exchange interface
│   │   ├── hyperliquid.py        # Hyperliquid implementation
│   │   ├── bitget.py             # Bitget implementation
│   │   └── paper_trading.py      # Paper trading simulator
│   ├── data/
│   │   └── timeframe_aggregator.py  # Multi-timeframe analysis
│   ├── utils/                    # Utility functions
│   └── config.py                 # Configuration management
├── config/
│   └── .env.example              # Environment variables template
├── scripts/
│   └── validate_setup.py         # Setup validation script
├── main.py                       # Main entry point
├── requirements.txt              # Python dependencies
├── TODO.md                       # Task list and rules
└── README.md                     # This file
```

## 🧠 How It Works

### 1. Psi-frequency Analysis
The bot calculates a "Psi-frequency" value that represents market momentum on an XY scale:
- **X-axis**: Time progression
- **Y-axis**: Price level
- Combines price momentum, volume momentum, and wave strength
- Used to detect trend swings and optimal entry points

### 2. Multi-Timeframe Analysis
Analyzes candles across multiple timeframes simultaneously:
- Aggregates 1-minute candles to higher timeframes
- Extracts features: body ratio, wick sizes, volume patterns
- Calculates ATR (Average True Range) for volatility
- Identifies trend strength using linear regression

### 3. ML Model Predictions
Two XGBoost models (exported to ONNX format):

**Model 1 - Trend Detector**:
- Predicts: Bullish, Neutral, or Bearish trend
- Input: 57 features from candle analysis and Psi-frequency
- Output: Trend direction with confidence score

**Model 2 - Signal Generator**:
- Predicts: Buy, Sell, or Hold signal
- Input: Same 57 features
- Output: Trading action with confidence score

### 4. Position Management
- **Entry**: Opens position when both models agree and Psi-frequency is high
- **Pyramiding**: Adds to winning positions (up to 3 levels)
- **Stop Loss**: Moves to positive territory after initial profit
- **Take Profit**: Exits at predefined profit targets
- **Trailing Stop**: Locks in profits as price moves favorably

### 5. Risk Management
- Position size: 2% of account per trade
- Leverage: 5x default, max 10x
- Stop loss: 1.5% from entry
- Take profit: 3.0% from entry
- Daily loss limit: 5% maximum

## ⚙️ Configuration

Edit `config/.env` to customize:

```bash
# Trading Mode
TRADING_MODE=paper              # paper or live

# Exchange API Keys
HYPERLIQUID_API_KEY=your_key
HYPERLIQUID_API_SECRET=your_secret
BITGET_API_KEY=your_key
BITGET_API_SECRET=your_secret

# Trading Parameters
DEFAULT_LEVERAGE=5
PYRAMIDING_LEVELS=3
POSITION_SIZE_PERCENT=2.0

# Risk Management
STOP_LOSS_PERCENT=1.5
TAKE_PROFIT_PERCENT=3.0
MAX_DAILY_LOSS_PERCENT=5.0

# Psi-frequency Settings
PSI_FREQ_THRESHOLD=0.7
PSI_TRAJECTORY_WINDOW=20
PSI_SENSITIVITY=1.5

# Timeframes (minutes)
TIMEFRAMES=1,5,15,30,60,240
```

## 🔐 Security Notes

- **Never commit** your `.env` file with real API keys
- Use **testnet** for initial testing
- Start with **paper trading** to validate strategy
- Use **small position sizes** when going live
- Enable **2FA** on exchange accounts
- Keep API keys **read + trade only** (no withdrawal permissions)

## 📊 Monitoring

The bot logs all activity to:
- Console output (INFO level)
- Log file: `logs/psi_freq_scalper.log`

Monitor:
- Trading signals and confidence scores
- Position entries and exits
- Profit/Loss in real-time
- Daily trade count
- Stop loss triggers

## 🧪 Testing

### Paper Trading Test
```bash
# Run for 1 hour in paper mode
python main.py --mode paper --duration 3600

# Check statistics in logs
tail -f logs/psi_freq_scalper.log
```

### Model Training (Advanced)
To train custom ML models, you'll need historical data:
```python
from psi_freq_scalper.models.ml_models import TrendDetectorModel

model = TrendDetectorModel()
model.train(X_train, y_train, X_val, y_val)
model.export_to_onnx("models/trend_detector.onnx")
```

## ⚠️ Risk Disclaimer

**IMPORTANT**: Cryptocurrency trading carries substantial risk of loss and is not suitable for every investor.

- This bot is provided **as-is** without warranties
- Past performance does not guarantee future results
- You are responsible for your own trading decisions
- Start with small amounts you can afford to lose
- Use **paper trading** extensively before live trading
- The developers are not liable for any financial losses

## 🤝 Contributing

1. Review `TODO.md` for pending tasks
2. Run `python scripts/validate_setup.py`
3. Make changes and test thoroughly
4. Submit pull requests with clear descriptions

## 📝 TODO List

See `TODO.md` for:
- Pending features
- Known issues
- Roadmap
- Task dependencies

## 📄 License

MIT License - See LICENSE file for details

## 🆘 Support

For issues and questions:
1. Check `TODO.md` for known issues
2. Review logs in `logs/` directory
3. Run validation script
4. Open GitHub issue with details

## 🔄 Version History

- **v1.0.0** (2026-02-15): Initial release
  - Psi-frequency calculator
  - Dual XGBoost models
  - Multi-exchange support
  - Paper and live trading modes
  - Pyramiding strategy
  - Positive stop loss management

---

**Remember**: Always run `python scripts/validate_setup.py` before starting any task!