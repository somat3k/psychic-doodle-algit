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
- [ ] Configure API keys for exchanges (see config/.env.example)
- [ ] Set up logging configuration
- [ ] Initialize database for trade history

### Core Trading Engine
- [ ] Implement exchange connectors
  - [ ] Hyperliquid integration
  - [ ] Bitget integration
  - [ ] Unified interface
- [ ] Build multi-timeframe data aggregator
- [ ] Develop Psi-frequency calculator
- [ ] Create position management system

### ML Models
- [ ] Train XGBoost model for trend detection
- [ ] Train XGBoost model for entry/exit signals
- [ ] Export models to ONNX format
- [ ] Implement model inference pipeline
- [ ] Create feature engineering module

### Trading Strategies
- [ ] Implement trend swing detection algorithm
- [ ] Build pyramiding strategy
- [ ] Configure leverage management
- [ ] Develop stop loss system (positive balance tracking)
- [ ] Create stop limit order execution logic

### Testing and Validation
- [ ] Unit tests for core modules
- [ ] Integration tests for exchange APIs
- [ ] Backtesting framework
- [ ] Paper trading validation
- [ ] Performance benchmarking

### Documentation
- [ ] API documentation
- [ ] Strategy documentation
- [ ] Configuration guide
- [ ] Deployment guide

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
