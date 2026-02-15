# TODO List for Psi-freq Scalper

## IMPORTANT: Read Before Starting Any Task
Before attempting any task, you must:
1. Review this TODO list completely
2. Check task dependencies and prerequisites
3. Verify all required configurations are in place
4. Run validation checks using `python scripts/validate_setup.py`
5. Ensure test environment is properly set up

## High Priority Tasks

### Setup and Configuration
- [x] Create project structure
- [x] Set up requirements.txt
- [x] Set up logging configuration
- [ ] Configure API keys for exchanges (see config/.env.example)
- [ ] Initialize database for trade history (optional enhancement)

### Core Trading Engine
- [x] Implement exchange connectors
  - [x] Hyperliquid integration
  - [x] Bitget integration
  - [x] Unified interface
- [x] Build multi-timeframe data aggregator
- [x] Develop Psi-frequency calculator
- [x] Create position management system

### ML Models
- [x] Train XGBoost model for trend detection
- [x] Train XGBoost model for entry/exit signals
- [x] Export models to ONNX format
- [x] Implement model inference pipeline
- [x] Create feature engineering module
- [ ] Train models on real historical data (currently using synthetic data)

### Trading Strategies
- [x] Implement trend swing detection algorithm
- [x] Build pyramiding strategy
- [x] Configure leverage management
- [x] Develop stop loss system (positive balance tracking)
- [x] Create stop limit order execution logic
- [x] Implement trailing stop mechanism

### Testing and Validation
- [x] Unit tests for core modules
- [x] Paper trading validation
- [ ] Integration tests for exchange APIs (requires API keys)
- [ ] Backtesting framework (optional enhancement)
- [ ] Performance benchmarking (optional enhancement)

### Documentation
- [x] API documentation (in docstrings)
- [x] Strategy documentation (in README)
- [x] Configuration guide (in README and .env.example)
- [x] Deployment guide (in README)

## Medium Priority Tasks
- [ ] Add risk management dashboard
- [ ] Implement alerting system
- [ ] Create performance analytics
- [ ] Add multi-symbol support
- [ ] Optimize execution speed

## Low Priority Tasks
- [ ] Web interface for monitoring
- [ ] Mobile notifications
- [ ] Advanced reporting features
- [ ] Historical data export

## Dependencies Map
- ML Models → Feature Engineering
- Trading Engine → Exchange Connectors
- Paper Trading → Trading Engine + ML Models
- Live Trading → Paper Trading + Risk Validation

## Notes
- Always test in paper trading mode before live trading
- Keep stop loss at positive balance to protect capital
- Monitor leverage usage to avoid liquidation
- Review model performance weekly
