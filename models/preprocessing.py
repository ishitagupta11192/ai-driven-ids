"""
Data preprocessing pipeline for network flow data.
Handles feature encoding, normalization, and sequence preparation.
"""

import pandas as pd
import numpy as np
from sklearn.preprocessing import LabelEncoder, StandardScaler, MinMaxScaler
from sklearn.model_selection import train_test_split
import pickle
import os
from typing import Tuple, Dict, List

class NetworkFlowPreprocessor:
    """Preprocessor for network flow data."""
    
    def __init__(self):
        self.label_encoders = {}
        self.scalers = {}
        self.feature_columns = []
        self.categorical_columns = ['protocol_type', 'service', 'flag']
        self.numerical_columns = []
        self.is_fitted = False
        
    def _identify_columns(self, df: pd.DataFrame):
        """Identify categorical and numerical columns."""
        self.categorical_columns = ['protocol_type', 'service', 'flag']
        self.numerical_columns = [col for col in df.columns 
                                if col not in self.categorical_columns + ['label', 'timestamp']]
        self.feature_columns = self.categorical_columns + self.numerical_columns
        
    def fit(self, df: pd.DataFrame):
        """Fit preprocessors on training data."""
        self._identify_columns(df)
        
        # Fit label encoders for categorical variables
        for col in self.categorical_columns:
            if col in df.columns:
                le = LabelEncoder()
                le.fit(df[col].astype(str))
                self.label_encoders[col] = le
        
        # Fit scaler for numerical variables
        numerical_data = df[self.numerical_columns].values
        self.scalers['numerical'] = StandardScaler()
        self.scalers['numerical'].fit(numerical_data)
        
        self.is_fitted = True
        
    @property
    def n_features(self):
        """Get the number of features after preprocessing."""
        if not self.is_fitted:
            return 0
        # Categorical features are encoded as single values
        n_categorical = len(self.categorical_columns)
        # Numerical features
        n_numerical = len(self.numerical_columns)
        return n_categorical + n_numerical
        
    def transform(self, df: pd.DataFrame) -> np.ndarray:
        """Transform data using fitted preprocessors."""
        if not self.is_fitted:
            raise ValueError("Preprocessor must be fitted before transform")
        
        # Encode categorical variables
        encoded_data = []
        for col in self.categorical_columns:
            if col in df.columns:
                le = self.label_encoders[col]
                encoded = le.transform(df[col].astype(str))
                encoded_data.append(encoded.reshape(-1, 1))
        
        # Scale numerical variables
        numerical_data = df[self.numerical_columns].values
        scaled_numerical = self.scalers['numerical'].transform(numerical_data)
        encoded_data.append(scaled_numerical)
        
        # Combine all features
        processed_data = np.hstack(encoded_data)
        return processed_data
    
    def fit_transform(self, df: pd.DataFrame) -> np.ndarray:
        """Fit and transform data."""
        self.fit(df)
        return self.transform(df)
    
    def inverse_transform_labels(self, encoded_labels: np.ndarray) -> List[str]:
        """Convert encoded labels back to original labels."""
        if 'label' in self.label_encoders:
            return self.label_encoders['label'].inverse_transform(encoded_labels)
        return encoded_labels
    
    def encode_labels(self, labels: pd.Series) -> np.ndarray:
        """Encode string labels to integers."""
        if 'label' not in self.label_encoders:
            le = LabelEncoder()
            encoded = le.fit_transform(labels)
            self.label_encoders['label'] = le
        else:
            encoded = self.label_encoders['label'].transform(labels)
        return encoded
    
    def get_feature_names(self) -> List[str]:
        """Get feature names after preprocessing."""
        feature_names = []
        
        # Add categorical feature names
        for col in self.categorical_columns:
            if col in self.label_encoders:
                feature_names.append(f"{col}_encoded")
        
        # Add numerical feature names
        feature_names.extend(self.numerical_columns)
        
        return feature_names
    
    def save(self, filepath: str):
        """Save preprocessor to file."""
        with open(filepath, 'wb') as f:
            pickle.dump({
                'label_encoders': self.label_encoders,
                'scalers': self.scalers,
                'feature_columns': self.feature_columns,
                'categorical_columns': self.categorical_columns,
                'numerical_columns': self.numerical_columns,
                'is_fitted': self.is_fitted
            }, f)
    
    def load(self, filepath: str):
        """Load preprocessor from file."""
        with open(filepath, 'rb') as f:
            data = pickle.load(f)
            self.label_encoders = data['label_encoders']
            self.scalers = data['scalers']
            self.feature_columns = data['feature_columns']
            self.categorical_columns = data['categorical_columns']
            self.numerical_columns = data['numerical_columns']
            self.is_fitted = data['is_fitted']

def create_sequences(data: np.ndarray, labels: np.ndarray, 
                    sequence_length: int = 10) -> Tuple[np.ndarray, np.ndarray]:
    """
    Create sequences for LSTM input.
    
    Args:
        data: Feature data (n_samples, n_features)
        labels: Corresponding labels (n_samples,)
        sequence_length: Length of each sequence
        
    Returns:
        Tuple of (sequences, sequence_labels)
    """
    sequences = []
    sequence_labels = []
    
    for i in range(len(data) - sequence_length + 1):
        seq = data[i:i + sequence_length]
        label = labels[i + sequence_length - 1]  # Use last label in sequence
        sequences.append(seq)
        sequence_labels.append(label)
    
    return np.array(sequences), np.array(sequence_labels)

def prepare_data_for_training(df: pd.DataFrame, 
                            test_size: float = 0.2,
                            sequence_length: int = 10) -> Dict:
    """
    Prepare data for training the hybrid model.
    
    Args:
        df: Input DataFrame
        test_size: Fraction of data for testing
        sequence_length: Length of sequences for LSTM
        
    Returns:
        Dictionary containing prepared data
    """
    # Initialize preprocessor
    preprocessor = NetworkFlowPreprocessor()
    
    # Separate features and labels
    X = df.drop(['label', 'timestamp'], axis=1, errors='ignore')
    y = df['label']
    
    # Split data
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=test_size, random_state=42, stratify=y
    )
    
    # Fit preprocessor on training data
    X_train_processed = preprocessor.fit_transform(X_train)
    X_test_processed = preprocessor.transform(X_test)
    
    # Encode labels
    y_train_encoded = preprocessor.encode_labels(y_train)
    y_test_encoded = preprocessor.encode_labels(y_test)
    
    # Create sequences for LSTM
    X_train_seq, y_train_seq = create_sequences(
        X_train_processed, y_train_encoded, sequence_length
    )
    X_test_seq, y_test_seq = create_sequences(
        X_test_processed, y_test_encoded, sequence_length
    )
    
    return {
        'X_train': X_train_seq,
        'X_test': X_test_seq,
        'y_train': y_train_seq,
        'y_test': y_test_seq,
        'preprocessor': preprocessor,
        'n_features': X_train_processed.shape[1],
        'n_classes': len(np.unique(y_train_encoded)),
        'class_names': preprocessor.label_encoders['label'].classes_
    }

def load_and_preprocess_data(data_path: str, 
                           preprocessor_path: str = None) -> Dict:
    """
    Load and preprocess data from CSV file.
    
    Args:
        data_path: Path to CSV file
        preprocessor_path: Path to saved preprocessor (optional)
        
    Returns:
        Dictionary containing prepared data
    """
    # Load data
    df = pd.read_csv(data_path)
    print(f"Loaded data: {len(df)} samples")
    print(f"Label distribution: {df['label'].value_counts().to_dict()}")
    
    # Load preprocessor if provided
    if preprocessor_path and os.path.exists(preprocessor_path):
        preprocessor = NetworkFlowPreprocessor()
        preprocessor.load(preprocessor_path)
        print("Loaded existing preprocessor")
    else:
        preprocessor = None
    
    # Prepare data
    if preprocessor is None:
        data_dict = prepare_data_for_training(df)
    else:
        # Use existing preprocessor
        X = df.drop(['label', 'timestamp'], axis=1, errors='ignore')
        y = df['label']
        
        X_processed = preprocessor.transform(X)
        y_encoded = preprocessor.encode_labels(y)
        
        X_seq, y_seq = create_sequences(X_processed, y_encoded)
        
        data_dict = {
            'X_train': X_seq,
            'X_test': X_seq,  # Use same data for both if no split
            'y_train': y_seq,
            'y_test': y_seq,
            'preprocessor': preprocessor,
            'n_features': X_processed.shape[1],
            'n_classes': len(np.unique(y_encoded)),
            'class_names': preprocessor.label_encoders['label'].classes_
        }
    
    return data_dict

if __name__ == "__main__":
    # Test the preprocessing pipeline
    from generate_sample_data import generate_network_flow_data
    
    # Generate sample data
    df = generate_network_flow_data(n_samples=1000, attack_ratio=0.2)
    
    # Test preprocessing
    data_dict = prepare_data_for_training(df)
    
    print(f"Training sequences: {data_dict['X_train'].shape}")
    print(f"Test sequences: {data_dict['X_test'].shape}")
    print(f"Number of features: {data_dict['n_features']}")
    print(f"Number of classes: {data_dict['n_classes']}")
    print(f"Class names: {data_dict['class_names']}")
