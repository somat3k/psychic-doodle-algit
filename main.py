"""
Main entry point for Psi-freq Scalper
"""
import sys
import argparse
from loguru import logger
from psi_freq_scalper.config import Config
from psi_freq_scalper.core.engine import TradingEngine


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="Psi-freq Scalper - Advanced Trading Bot"
    )
    
    parser.add_argument(
        "--symbol",
        type=str,
        default="BTC-USDT",
        help="Trading symbol (default: BTC-USDT)"
    )
    
    parser.add_argument(
        "--mode",
        type=str,
        choices=["paper", "live"],
        default="paper",
        help="Trading mode: paper or live (default: paper)"
    )
    
    parser.add_argument(
        "--duration",
        type=int,
        default=None,
        help="Run duration in seconds (default: run indefinitely)"
    )
    
    args = parser.parse_args()
    
    # Load configuration
    config = Config.from_env()
    config.trading.mode = args.mode
    
    # Print startup banner
    print("=" * 60)
    print("           PSI-FREQ SCALPER TRADING BOT")
    print("=" * 60)
    print(f"Symbol: {args.symbol}")
    print(f"Mode: {args.mode.upper()}")
    print(f"Leverage: {config.trading.default_leverage}x")
    print(f"Pyramiding Levels: {config.trading.pyramiding_levels}")
    print(f"Stop Loss: {config.risk.stop_loss_percent}%")
    print(f"Psi-freq Threshold: {config.psi_freq.threshold}")
    print("=" * 60)
    
    if args.mode == "live":
        print("\n⚠️  WARNING: LIVE TRADING MODE ENABLED ⚠️")
        print("This will execute real trades with real money.")
        confirm = input("Type 'YES' to continue: ")
        if confirm != "YES":
            print("Aborted.")
            sys.exit(0)
    
    # Initialize and run trading engine
    try:
        engine = TradingEngine(config, symbol=args.symbol)
        engine.run(duration=args.duration)
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
