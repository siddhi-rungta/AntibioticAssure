#!/usr/bin/env python3
"""
Training Script
Trains the ML model with sample data
"""

import sys
import os
import pandas as pd
import argparse

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from backend.preprocessing.data_cleaner import DataCleaner
from backend.preprocessing.feature_engineering import FeatureEngineer
from backend.models.ml_model import AntibioticMLModel
from backend.utils.guidelines import ClinicalGuidelines


def main():
    """Main training function"""
    # Parse command-line arguments
    parser = argparse.ArgumentParser(description='Train ML model')
    parser.add_argument('--input', default='data/sample_prescriptions.csv',
                       help='Input CSV file with labeled prescriptions')
    parser.add_argument('--output', default='models/trained_model.pkl',
                       help='Output path for trained model')
    args = parser.parse_args()

    print("=" * 60)
    print("Training Antibiotic Prescription ML Model")
    print("=" * 60)

    # Load data
    print(f"\n📂 Loading training data from: {args.input}")
    data_path = args.input if os.path.isabs(args.input) else os.path.join(os.path.dirname(__file__), '..', args.input)
    df = pd.read_csv(data_path)
    print(f"✓ Loaded {len(df)} prescriptions")

    # Initialize components
    print("\n🔧 Initializing components...")
    guidelines = ClinicalGuidelines()
    cleaner = DataCleaner()
    feature_engineer = FeatureEngineer(guidelines)
    ml_model = AntibioticMLModel(model_type='random_forest')

    # Clean data
    print("\n🧹 Cleaning data...")
    df_clean = cleaner.clean_dataframe(df)
    print(f"✓ Cleaned data: {len(df_clean)} records")

    # Engineer features
    print("\n⚙️  Engineering features...")
    df_features = feature_engineer.create_features(df_clean)
    print(f"✓ Created features: {len(df_features.columns)} columns")

    # Train model
    print("\n🤖 Training ML model...")
    metrics = ml_model.train(df_features, target_column='is_appropriate')

    print("\n" + "=" * 60)
    print("Training Results")
    print("=" * 60)
    print(f"Accuracy: {metrics['accuracy']:.4f}")
    print(f"Cross-validation Score: {metrics['cv_mean_score']:.4f} (±{metrics['cv_std_score']:.4f})")
    print(f"Training Size: {metrics['train_size']} samples")
    print(f"Test Size: {metrics['test_size']} samples")

    # Feature importance
    print("\n" + "=" * 60)
    print("Top 10 Most Important Features")
    print("=" * 60)
    for i, feat in enumerate(metrics['feature_importance'][:10], 1):
        print(f"{i:2d}. {feat['feature']:30s} {feat['importance']:.4f}")

    # Save model
    print("\n💾 Saving model...")
    model_path = args.output if os.path.isabs(args.output) else os.path.join(os.path.dirname(__file__), '..', args.output)
    os.makedirs(os.path.dirname(model_path), exist_ok=True)
    ml_model.save_model(model_path)
    print(f"✓ Model saved to {model_path}")

    print("\n" + "=" * 60)
    print("✅ Training Complete!")
    print("=" * 60)


if __name__ == '__main__':
    main()
