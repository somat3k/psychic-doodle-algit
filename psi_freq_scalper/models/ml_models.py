"""
ML Model Manager - XGBoost models with ONNX export
Two models: Trend Detector and Signal Generator
"""
import numpy as np
from typing import Dict, List, Tuple, Optional
import xgboost as xgb
from sklearn.preprocessing import StandardScaler
import onnxruntime as ort
import pickle
import os


class FeatureEngineering:
    """
    Feature engineering for ML models
    Extracts features from candle data without using TA-Lib
    """
    
    @staticmethod
    def extract_features(candle_features: List[Dict[str, float]], 
                        sequence_features: Dict[str, float],
                        psi_frequency: float) -> np.ndarray:
        """
        Extract and combine all features for ML model
        
        Args:
            candle_features: List of individual candle features
            sequence_features: Features from candle sequence
            psi_frequency: Current Psi-frequency value
            
        Returns:
            Feature array
        """
        features = []
        
        # Add recent candle features (last 10 candles)
        for candle_feat in candle_features[-10:]:
            features.extend([
                candle_feat.get('body_size', 0),
                candle_feat.get('body_ratio', 0),
                candle_feat.get('is_bullish', 0),
                candle_feat.get('upper_wick_ratio', 0),
                candle_feat.get('lower_wick_ratio', 0),
            ])
        
        # Pad if less than 10 candles
        while len(features) < 50:  # 10 candles * 5 features
            features.append(0.0)
        
        # Add sequence features
        features.extend([
            sequence_features.get('price_change_pct', 0),
            sequence_features.get('volume_trend', 0),
            sequence_features.get('atr', 0),
            sequence_features.get('volatility', 0),
            sequence_features.get('trend_strength', 0),
            sequence_features.get('bullish_candles', 0) / max(len(candle_features), 1),
        ])
        
        # Add Psi-frequency
        features.append(psi_frequency)
        
        return np.array(features, dtype=np.float32)


class TrendDetectorModel:
    """
    XGBoost model for trend detection
    Predicts trend direction and strength
    """
    
    def __init__(self, model_path: Optional[str] = None):
        """Initialize trend detector model"""
        self.model = None
        self.scaler = StandardScaler()
        self.model_path = model_path
        self.is_onnx = False
        self.onnx_session = None
        
        if model_path and os.path.exists(model_path):
            self.load_model(model_path)
    
    def train(self, X_train: np.ndarray, y_train: np.ndarray,
              X_val: Optional[np.ndarray] = None, y_val: Optional[np.ndarray] = None):
        """
        Train the trend detection model
        
        Args:
            X_train: Training features
            y_train: Training labels (0: bearish, 1: neutral, 2: bullish)
            X_val: Validation features
            y_val: Validation labels
        """
        # Scale features
        X_train_scaled = self.scaler.fit_transform(X_train)
        
        # Train XGBoost model
        params = {
            'objective': 'multi:softprob',
            'num_class': 3,
            'max_depth': 6,
            'learning_rate': 0.1,
            'n_estimators': 100,
            'subsample': 0.8,
            'colsample_bytree': 0.8,
            'random_state': 42
        }
        
        self.model = xgb.XGBClassifier(**params)
        
        if X_val is not None and y_val is not None:
            X_val_scaled = self.scaler.transform(X_val)
            self.model.fit(
                X_train_scaled, y_train,
                eval_set=[(X_val_scaled, y_val)],
                verbose=False
            )
        else:
            self.model.fit(X_train_scaled, y_train)
    
    def predict(self, X: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        """
        Predict trend
        
        Returns:
            Tuple of (predicted_class, probabilities)
        """
        if self.is_onnx and self.onnx_session:
            return self._predict_onnx(X)
        
        X_scaled = self.scaler.transform(X)
        predictions = self.model.predict(X_scaled)
        probabilities = self.model.predict_proba(X_scaled)
        
        return predictions, probabilities
    
    def _predict_onnx(self, X: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        """Predict using ONNX model"""
        X_scaled = self.scaler.transform(X)
        input_name = self.onnx_session.get_inputs()[0].name
        
        result = self.onnx_session.run(None, {input_name: X_scaled.astype(np.float32)})
        
        predictions = result[0]
        probabilities = result[1] if len(result) > 1 else result[0]
        
        return predictions, probabilities
    
    def export_to_onnx(self, output_path: str):
        """Export model to ONNX format"""
        if self.model is None:
            raise ValueError("Model not trained yet")
        
        from skl2onnx import to_onnx
        
        # Create sample input
        sample_input = np.zeros((1, self.scaler.n_features_in_), dtype=np.float32)
        
        # Convert to ONNX
        onnx_model = to_onnx(self.model, sample_input)
        
        # Save ONNX model
        with open(output_path, "wb") as f:
            f.write(onnx_model.SerializeToString())
        
        # Save scaler separately
        scaler_path = output_path.replace('.onnx', '_scaler.pkl')
        with open(scaler_path, 'wb') as f:
            pickle.dump(self.scaler, f)
    
    def load_model(self, model_path: str):
        """Load model from file"""
        if model_path.endswith('.onnx'):
            self.onnx_session = ort.InferenceSession(model_path)
            self.is_onnx = True
            
            # Load scaler
            scaler_path = model_path.replace('.onnx', '_scaler.pkl')
            if os.path.exists(scaler_path):
                with open(scaler_path, 'rb') as f:
                    self.scaler = pickle.load(f)
        else:
            self.model = xgb.XGBClassifier()
            self.model.load_model(model_path)


class SignalGeneratorModel:
    """
    XGBoost model for entry/exit signal generation
    Predicts optimal entry and exit points
    """
    
    def __init__(self, model_path: Optional[str] = None):
        """Initialize signal generator model"""
        self.model = None
        self.scaler = StandardScaler()
        self.model_path = model_path
        self.is_onnx = False
        self.onnx_session = None
        
        if model_path and os.path.exists(model_path):
            self.load_model(model_path)
    
    def train(self, X_train: np.ndarray, y_train: np.ndarray,
              X_val: Optional[np.ndarray] = None, y_val: Optional[np.ndarray] = None):
        """
        Train the signal generation model
        
        Args:
            X_train: Training features
            y_train: Training labels (0: no action, 1: buy, 2: sell)
            X_val: Validation features
            y_val: Validation labels
        """
        # Scale features
        X_train_scaled = self.scaler.fit_transform(X_train)
        
        # Train XGBoost model
        params = {
            'objective': 'multi:softprob',
            'num_class': 3,
            'max_depth': 5,
            'learning_rate': 0.05,
            'n_estimators': 150,
            'subsample': 0.9,
            'colsample_bytree': 0.9,
            'random_state': 42
        }
        
        self.model = xgb.XGBClassifier(**params)
        
        if X_val is not None and y_val is not None:
            X_val_scaled = self.scaler.transform(X_val)
            self.model.fit(
                X_train_scaled, y_train,
                eval_set=[(X_val_scaled, y_val)],
                verbose=False
            )
        else:
            self.model.fit(X_train_scaled, y_train)
    
    def predict(self, X: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        """
        Predict trading signal
        
        Returns:
            Tuple of (predicted_action, probabilities)
        """
        if self.is_onnx and self.onnx_session:
            return self._predict_onnx(X)
        
        X_scaled = self.scaler.transform(X)
        predictions = self.model.predict(X_scaled)
        probabilities = self.model.predict_proba(X_scaled)
        
        return predictions, probabilities
    
    def _predict_onnx(self, X: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        """Predict using ONNX model"""
        X_scaled = self.scaler.transform(X)
        input_name = self.onnx_session.get_inputs()[0].name
        
        result = self.onnx_session.run(None, {input_name: X_scaled.astype(np.float32)})
        
        predictions = result[0]
        probabilities = result[1] if len(result) > 1 else result[0]
        
        return predictions, probabilities
    
    def export_to_onnx(self, output_path: str):
        """Export model to ONNX format"""
        if self.model is None:
            raise ValueError("Model not trained yet")
        
        from skl2onnx import to_onnx
        
        # Create sample input
        sample_input = np.zeros((1, self.scaler.n_features_in_), dtype=np.float32)
        
        # Convert to ONNX
        onnx_model = to_onnx(self.model, sample_input)
        
        # Save ONNX model
        with open(output_path, "wb") as f:
            f.write(onnx_model.SerializeToString())
        
        # Save scaler separately
        scaler_path = output_path.replace('.onnx', '_scaler.pkl')
        with open(scaler_path, 'wb') as f:
            pickle.dump(self.scaler, f)
    
    def load_model(self, model_path: str):
        """Load model from file"""
        if model_path.endswith('.onnx'):
            self.onnx_session = ort.InferenceSession(model_path)
            self.is_onnx = True
            
            # Load scaler
            scaler_path = model_path.replace('.onnx', '_scaler.pkl')
            if os.path.exists(scaler_path):
                with open(scaler_path, 'rb') as f:
                    self.scaler = pickle.load(f)
        else:
            self.model = xgb.XGBClassifier()
            self.model.load_model(model_path)
