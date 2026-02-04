#!/usr/bin/env python3
"""
Auto-label prescriptions using the rule engine
"""

import sys
import os
import pandas as pd
import argparse

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from backend.models.rule_engine import RuleEngine
from backend.utils.guidelines import ClinicalGuidelines

def main():
    # Parse command-line arguments
    parser = argparse.ArgumentParser(description='Auto-label prescriptions')
    parser.add_argument('--input', default='data/sample_prescriptions.csv',
                       help='Input CSV file with prescriptions')
    parser.add_argument('--output', default='data/sample_prescriptions.csv',
                       help='Output CSV file for labeled data')
    args = parser.parse_args()

    print("=" * 60)
    print("Auto-Labeling Prescriptions")
    print("=" * 60)

    # Initialize rule engine
    print("\n🔧 Initializing rule engine...")
    guidelines = ClinicalGuidelines()
    rule_engine = RuleEngine(guidelines)

    # Load data
    print(f"\n📂 Loading prescription data from: {args.input}")
    input_file = args.input if os.path.isabs(args.input) else os.path.join(os.path.dirname(__file__), '..', args.input)
    df = pd.read_csv(input_file)
    print(f"✓ Loaded {len(df)} prescriptions")

    # Label each prescription
    print("\n🏷️  Labeling prescriptions...")
    labels = []
    appropriate_count = 0
    inappropriate_count = 0

    for idx, row in df.iterrows():
        # Convert row to dict for evaluation
        prescription = row.to_dict()

        # Evaluate with rule engine
        is_appropriate_bool, violations = rule_engine.evaluate_prescription(prescription)

        # Label: 1 if appropriate (no violations), 0 if inappropriate
        is_appropriate = 1 if is_appropriate_bool else 0
        labels.append(is_appropriate)

        if is_appropriate:
            appropriate_count += 1
        else:
            inappropriate_count += 1

        # Show progress
        if (idx + 1) % 10 == 0:
            print(f"  Processed {idx + 1}/{len(df)} prescriptions...")

    # Add labels to dataframe
    df['is_appropriate'] = labels

    # Save labeled data
    output_file = args.output if os.path.isabs(args.output) else os.path.join(os.path.dirname(__file__), '..', args.output)
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    df.to_csv(output_file, index=False)

    print(f"\n✅ Labeled data saved to: {output_file}")
    print(f"\n📊 Summary:")
    print(f"   Total: {len(df)}")
    print(f"   Appropriate: {appropriate_count} ({appropriate_count/len(df)*100:.1f}%)")
    print(f"   Inappropriate: {inappropriate_count} ({inappropriate_count/len(df)*100:.1f}%)")

    print("\n" + "=" * 60)
    print("✅ Labeling Complete!")
    print("=" * 60)
    print("\nNext step: Train model with labeled data")
    print("  python scripts/train_model.py")

if __name__ == '__main__':
    main()
