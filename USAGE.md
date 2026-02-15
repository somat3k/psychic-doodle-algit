# Psi-freq Scalper Usage Guide

This guide will help you get started with the Psi-freq Scalper trading bot.

## Table of Contents
1. [Installation](#installation)
2. [Configuration](#configuration)
3. [Training Models](#training-models)
4. [Running Paper Trading](#running-paper-trading)
5. [Running Live Trading](#running-live-trading)
6. [Monitoring and Logs](#monitoring-and-logs)
7. [Troubleshooting](#troubleshooting)

## Installation

### Prerequisites
- Python 3.8 or higher
- pip package manager
- Git

### Step 1: Clone the Repository
```bash
git clone https://github.com/somat3k/psychic-doodle-algit.git
cd psychic-doodle-algit
```

### Step 2: Install Dependencies
```bash
pip install -r requirements.txt
```

This will install all required packages including:
- NumPy, Pandas, scikit-learn (data processing)
- XGBoost (machine learning)
- ONNX and ONNXRuntime (model deployment)
- Pydantic (configuration management)
- Loguru (logging)
- Exchange SDKs (Hyperliquid, Bitget)

### Step 3: Validate Installation
```bash
python scripts/validate_setup.py
```

You should see:
```
✅ TODO.md exists
✅ Configuration example exists
✅ Requirements file exists
✅ Validation complete!
```

## Configuration

### Step 1: Create Environment File
```bash
cp config/.env.example config/.env
```

### Step 2: Edit Configuration
Open `config/.env` and configure your settings:

```bash
# Trading Mode (start with paper!)
TRADING_MODE=paper

# Exchange API Keys (only needed for live trading)
HYPERLIQUID_API_KEY=your_key_here
HYPERLIQUID_API_SECRET=your_secret_here
BITGET_API_KEY=your_key_here
BITGET_API_SECRET=your_secret_here

# Trading Parameters
DEFAULT_LEVERAGE=5          # Start conservative
PYRAMIDING_LEVELS=3         # Max 3 pyramid levels
POSITION_SIZE_PERCENT=2.0   # 2% of balance per trade

# Risk Management
STOP_LOSS_PERCENT=1.5       # 1.5% stop loss
TAKE_PROFIT_PERCENT=3.0     # 3% take profit
MAX_DAILY_LOSS_PERCENT=5.0  # Stop if 5% daily loss

# Psi-frequency Settings
PSI_FREQ_THRESHOLD=0.7      # Minimum signal strength
PSI_TRAJECTORY_WINDOW=20    # Look-back window
PSI_SENSITIVITY=1.5         # Sensitivity multiplier
```

### Configuration Tips
- **Start Conservative**: Use lower leverage (3-5x) initially
- **Small Position Size**: Keep position size at 1-2% of capital
- **Strict Stop Loss**: Don't increase stop loss beyond 2%
- **Test in Paper Mode**: Always test strategy changes in paper mode first

## Training Models

The bot includes two XGBoost models:
1. **Trend Detector**: Identifies market trend direction
2. **Signal Generator**: Generates buy/sell signals

### Quick Start (Synthetic Data)
For testing purposes, generate models with synthetic data:

```bash
python scripts/train_models.py
```

This creates:
- `models/trend_detector.onnx`
- `models/signal_generator.onnx`

### Production Training (Real Data)
For production use, train on real historical data:

```python
from psi_freq_scalper.models.ml_models import TrendDetectorModel
import pandas as pd

# Load your historical data
# Format: columns = [timestamp, open, high, low, close, volume]
data = pd.read_csv('historical_data.csv')

# Extract features and labels
# ... your feature engineering code ...

# Train model
model = TrendDetectorModel()
model.train(X_train, y_train, X_val, y_val)
model.export_to_onnx('models/trend_detector.onnx')
```

## Running Paper Trading

Paper trading simulates trades without real money. Perfect for testing!

### Start Paper Trading
```bash
python main.py --symbol BTC-USDT --mode paper
```

### Run for Specific Duration
```bash
# Run for 1 hour
python main.py --symbol BTC-USDT --mode paper --duration 3600
```

### What You'll See
```
============================================================
           PSI-FREQ SCALPER TRADING BOT
============================================================
Symbol: BTC-USDT
Mode: PAPER
Leverage: 5x
Pyramiding Levels: 3
Stop Loss: 1.5%
Psi-freq Threshold: 0.7
============================================================

2026-02-15 02:00:00 | INFO | Starting trading bot
2026-02-15 02:01:00 | INFO | Signal: buy | Confidence: 0.85 | Reason: Bullish trend with Psi-freq 0.78
2026-02-15 02:01:01 | INFO | Placed BUY order: paper_1 | Size: 0.0200 | Price: 50000.00
```

### Demo Script
Test paper trading quickly:
```bash
PYTHONPATH=. python scripts/demo_paper_trading.py
```

## Running Live Trading

⚠️ **WARNING**: Live trading involves real money. Only proceed when:
- You've tested extensively in paper mode
- Your strategy is profitable in paper trading
- You understand the risks
- You have API keys configured

### Prerequisites
1. Exchange account (Hyperliquid or Bitget)
2. API keys with trading permissions (no withdrawal!)
3. Two-factor authentication enabled
4. Start with testnet if available

### Start Live Trading
```bash
python main.py --symbol BTC-USDT --mode live
```

You'll be prompted:
```
⚠️  WARNING: LIVE TRADING MODE ENABLED ⚠️
This will execute real trades with real money.
Type 'YES' to continue: 
```

### Safety Tips for Live Trading
1. **Start Small**: Use minimal position sizes initially
2. **Monitor Closely**: Watch the bot especially in first hours
3. **Set Daily Limits**: Use MAX_DAILY_LOSS_PERCENT strictly
4. **Test Hours**: Don't start during high volatility events
5. **Have Exit Plan**: Know how to stop the bot quickly

### Stopping the Bot
Press `Ctrl+C` to gracefully stop:
```
^C
2026-02-15 02:30:00 | INFO | Received interrupt signal, stopping bot
2026-02-15 02:30:00 | INFO | Trading bot stopped
```

## Monitoring and Logs

### Console Output
Real-time information displayed:
- Trading signals with confidence scores
- Order placements and executions
- Current balance and positions
- Profit/Loss updates

### Log Files
Detailed logs saved to: `logs/psi_freq_scalper.log`

View live logs:
```bash
tail -f logs/psi_freq_scalper.log
```

Search for errors:
```bash
grep ERROR logs/psi_freq_scalper.log
```

### Key Metrics to Monitor
- **Win Rate**: Percentage of profitable trades
- **Total Return**: Overall profit/loss percentage
- **Daily Trades**: Number of trades per day
- **Max Drawdown**: Largest peak-to-trough decline
- **Sharpe Ratio**: Risk-adjusted return (implement separately)

### Paper Trading Statistics
At the end of paper trading session:
```
==================================================
PAPER TRADING STATISTICS
==================================================
Total Trades: 25
Total PnL: $234.50
Total Commission: $12.30
Win Rate: 64.00%
Current Balance: $10234.50
Total Return: 2.35%
==================================================
```

## Troubleshooting

### Issue: Module Not Found
```
ModuleNotFoundError: No module named 'psi_freq_scalper'
```

**Solution**: Add to PYTHONPATH or install as package:
```bash
# Option 1: Add to PYTHONPATH
export PYTHONPATH=/path/to/psychic-doodle-algit:$PYTHONPATH

# Option 2: Install as package
pip install -e .
```

### Issue: No API Keys
```
WARNING: No exchange credentials provided, using paper trading
```

**Solution**: Configure API keys in `config/.env`

### Issue: Exchange Connection Failed
```
Error fetching candles from Hyperliquid: Connection timeout
```

**Solutions**:
1. Check internet connection
2. Verify API keys are correct
3. Try testnet mode first
4. Check exchange status page

### Issue: Model Not Found
```
Model file not found: models/trend_detector.onnx
```

**Solution**: Train models first:
```bash
python scripts/train_models.py
```

### Issue: High CPU Usage
**Solutions**:
1. Increase sleep time between iterations
2. Reduce number of timeframes
3. Use fewer candles for analysis
4. Optimize model inference

### Issue: Memory Leak
**Solutions**:
1. Limit candle buffer size
2. Clear old data periodically
3. Restart bot daily
4. Monitor with `htop` or `top`

## Advanced Usage

### Custom Timeframes
Edit `config/.env`:
```bash
TIMEFRAMES=1,5,15,60,240  # Minutes
```

### Adjust Risk Parameters
Fine-tune in `config/.env`:
```bash
STOP_LOSS_PERCENT=1.0      # Tighter stop
TAKE_PROFIT_PERCENT=5.0    # Larger target
POSITION_SIZE_PERCENT=1.0  # Smaller positions
```

### Multiple Symbols
Run multiple instances:
```bash
# Terminal 1
python main.py --symbol BTC-USDT --mode paper

# Terminal 2
python main.py --symbol ETH-USDT --mode paper
```

### Backtesting (Future Enhancement)
```python
# Coming soon: Backtesting framework
from psi_freq_scalper.backtest import Backtester

backtester = Backtester(config)
results = backtester.run(historical_data)
```

## Best Practices

### 1. Always Start with Paper Trading
Test every change in paper mode before live trading.

### 2. Gradual Optimization
Make one change at a time and measure impact.

### 3. Keep Logs
Maintain logs for analysis and debugging.

### 4. Monitor Performance
Review daily/weekly performance metrics.

### 5. Stay Updated
Check for updates and security patches regularly.

### 6. Risk Management
- Never risk more than you can afford to lose
- Use stop losses always
- Diversify across symbols and strategies
- Don't overtrade or chase losses

## Support

For help:
1. Check TODO.md for known issues
2. Review logs for error details
3. Run validation script
4. Search existing GitHub issues
5. Open new issue with details

## Additional Resources

- [README.md](README.md) - Main documentation
- [TODO.md](TODO.md) - Task list and roadmap
- [config/.env.example](config/.env.example) - Configuration reference
- Exchange documentation:
  - [Hyperliquid API](https://hyperliquid.gitbook.io/)
  - [Bitget API](https://www.bitget.com/api-doc/)

---

**Remember**: Trading carries risk. This bot is provided as-is. Always validate in paper trading first!
