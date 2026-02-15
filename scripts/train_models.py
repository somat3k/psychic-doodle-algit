"""
Model training script for generating synthetic data and training models
"""
import numpy as np
import os
from psi_freq_scalper.models.ml_models import TrendDetectorModel, SignalGeneratorModel


def generate_synthetic_training_data(n_samples: int = 1000):
    """
    Generate synthetic training data for demonstration
    In production, use real historical data
    """
    # Generate 57 features (as defined in FeatureEngineering)
    X = np.random.randn(n_samples, 57).astype(np.float32)
    
    # Normalize some features to 0-1 range
    X[:, :10] = np.abs(X[:, :10])  # Candle features
    X[:, -1] = np.clip(X[:, -1], 0, 1)  # Psi-frequency
    
    # Generate trend labels (0: bearish, 1: neutral, 2: bullish)
    y_trend = np.random.randint(0, 3, n_samples)
    
    # Generate signal labels (0: hold, 1: buy, 2: sell)
    # Make signals correlated with trends
    y_signal = np.zeros(n_samples, dtype=int)
    for i in range(n_samples):
        if y_trend[i] == 2:  # Bullish
            y_signal[i] = np.random.choice([0, 1], p=[0.3, 0.7])
        elif y_trend[i] == 0:  # Bearish
            y_signal[i] = np.random.choice([0, 2], p=[0.3, 0.7])
        else:  # Neutral
            y_signal[i] = 0
    
    return X, y_trend, y_signal


def train_models():
    """Train both ML models and export to ONNX"""
    print("Generating synthetic training data...")
    X, y_trend, y_signal = generate_synthetic_training_data(n_samples=5000)
    
    # Split into train and validation
    split_idx = int(len(X) * 0.8)
    X_train, X_val = X[:split_idx], X[split_idx:]
    y_trend_train, y_trend_val = y_trend[:split_idx], y_trend[split_idx:]
    y_signal_train, y_signal_val = y_signal[:split_idx], y_signal[split_idx:]
    
    # Create models directory
    os.makedirs("models", exist_ok=True)
    
    # Train Trend Detector Model
    print("\nTraining Trend Detector Model...")
    trend_model = TrendDetectorModel()
    trend_model.train(X_train, y_trend_train, X_val, y_trend_val)
    
    # Export to ONNX
    print("Exporting Trend Detector to ONNX...")
    trend_model.export_to_onnx("models/trend_detector.onnx")
    print("✅ Trend Detector model saved to models/trend_detector.onnx")
    
    # Train Signal Generator Model
    print("\nTraining Signal Generator Model...")
    signal_model = SignalGeneratorModel()
    signal_model.train(X_train, y_signal_train, X_val, y_signal_val)
    
    # Export to ONNX
    print("Exporting Signal Generator to ONNX...")
    signal_model.export_to_onnx("models/signal_generator.onnx")
    print("✅ Signal Generator model saved to models/signal_generator.onnx")
    
    print("\n" + "="*60)
    print("Model training complete!")
    print("="*60)
    print("\nNOTE: These are models trained on synthetic data.")
    print("For production use, train on real historical market data.")


if __name__ == "__main__":
    train_models()
