#!/usr/bin/env python3
"""
Synthea Data Importer
Imports and processes Synthea synthetic patient data for antibiotic prescription monitoring
"""

import sys
import os
import pandas as pd
import json
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


def import_synthea_data(input_dir, output_dir, limit=None):
    """
    Import Synthea data and convert to prescription format

    Args:
        input_dir: Directory containing Synthea CSV files
        output_dir: Directory to save processed data
        limit: Optional limit on number of prescriptions to process
    """

    print("=" * 70)
    print("Synthea Data Import")
    print("=" * 70)

    # Check if input directory exists
    if not os.path.exists(input_dir):
        print(f"❌ Input directory not found: {input_dir}")
        return False

    # Create output directory
    os.makedirs(output_dir, exist_ok=True)

    # Load Synthea data files
    print(f"\n📂 Loading Synthea data from: {input_dir}")

    try:
        # Load required files
        print("  Loading patients.csv...")
        patients = pd.read_csv(os.path.join(input_dir, 'patients.csv'))
        print(f"  ✓ Loaded {len(patients)} patients")

        print("  Loading medications.csv...")
        medications = pd.read_csv(os.path.join(input_dir, 'medications.csv'))
        print(f"  ✓ Loaded {len(medications)} medication records")

        print("  Loading conditions.csv...")
        conditions = pd.read_csv(os.path.join(input_dir, 'conditions.csv'))
        print(f"  ✓ Loaded {len(conditions)} condition records")

    except FileNotFoundError as e:
        print(f"❌ Required file not found: {e}")
        return False

    # Define antibiotic keywords
    antibiotic_keywords = [
        'amoxicillin', 'azithromycin', 'ciprofloxacin', 'doxycycline',
        'ceftriaxone', 'vancomycin', 'metronidazole', 'colistin',
        'penicillin', 'ampicillin', 'cephalexin', 'levofloxacin',
        'trimethoprim', 'sulfamethoxazole', 'clarithromycin', 'erythromycin'
    ]

    # Filter for antibiotic prescriptions
    print(f"\n🔍 Filtering for antibiotic prescriptions...")
    medications['DESCRIPTION_LOWER'] = medications['DESCRIPTION'].str.lower()

    antibiotic_mask = medications['DESCRIPTION_LOWER'].str.contains('|'.join(antibiotic_keywords), na=False)
    antibiotics = medications[antibiotic_mask].copy()

    print(f"  ✓ Found {len(antibiotics)} antibiotic prescriptions")

    if len(antibiotics) == 0:
        print("  ⚠️  No antibiotic prescriptions found in dataset")
        return False

    # Apply limit if specified
    if limit and len(antibiotics) > limit:
        print(f"  ℹ️  Limiting to first {limit} prescriptions")
        antibiotics = antibiotics.head(limit)

    # Process prescriptions
    print(f"\n🔄 Processing prescriptions...")
    prescriptions = []
    errors = 0

    for idx, med in antibiotics.iterrows():
        try:
            # Get patient info
            patient_match = patients[patients['Id'] == med['PATIENT']]
            if len(patient_match) == 0:
                errors += 1
                continue
            patient = patient_match.iloc[0]

            # Get diagnosis (most recent condition for this patient)
            patient_conditions = conditions[conditions['PATIENT'] == med['PATIENT']]

            diagnosis = 'unknown'
            if len(patient_conditions) > 0:
                # Just use the first condition found (simplified)
                diagnosis = patient_conditions.iloc[0]['DESCRIPTION'].lower()
                # Standardize common diagnoses
                if 'cold' in diagnosis or 'rhinitis' in diagnosis:
                    diagnosis = 'common_cold'
                elif 'pneumonia' in diagnosis:
                    diagnosis = 'community_acquired_pneumonia'
                elif 'urinary' in diagnosis or 'uti' in diagnosis:
                    diagnosis = 'urinary_tract_infection'
                elif 'sinusitis' in diagnosis:
                    diagnosis = 'acute_sinusitis'
                elif 'bronchitis' in diagnosis:
                    diagnosis = 'acute_bronchitis'
                elif 'pharyngitis' in diagnosis or 'strep' in diagnosis:
                    diagnosis = 'streptococcal_pharyngitis'
                elif 'otitis' in diagnosis:
                    diagnosis = 'acute_otitis_media'

            # Calculate age (simplified - use 2020 as reference year)
            from datetime import datetime
            try:
                birth_year = int(str(patient['BIRTHDATE'])[:4])
                age = max(1, 2020 - birth_year)
            except:
                age = 45  # Default adult age

            # Extract antibiotic name
            antibiotic_name = med['DESCRIPTION'].lower()
            for keyword in antibiotic_keywords:
                if keyword in antibiotic_name:
                    antibiotic_name = keyword
                    break

            # Generate dosage (simplified - real data would have this)
            # Standard adult dosages for common antibiotics
            dosage_map = {
                'amoxicillin': 500,
                'azithromycin': 250,
                'ciprofloxacin': 500,
                'doxycycline': 100,
                'ceftriaxone': 1000,
                'vancomycin': 1000,
                'metronidazole': 500,
                'colistin': 300
            }
            dosage = dosage_map.get(antibiotic_name, 500)

            # Standard frequency and duration
            frequency = 2 if antibiotic_name in ['azithromycin', 'doxycycline'] else 3
            duration = 7

            # Weight estimation based on age (simplified)
            if age < 12:
                weight = 30 + (age * 3)
            else:
                weight = 70

            # Create prescription record
            prescription = {
                'prescription_id': f'SYN{idx}',
                'patient_id': med['PATIENT'],
                'patient_age': age,
                'patient_weight_kg': weight,
                'diagnosis': diagnosis,
                'antibiotic_prescribed': antibiotic_name,
                'dosage_mg': dosage,
                'frequency_per_day': frequency,
                'duration_days': duration,
                'prescriber_id': med.get('REASONCODE', 'unknown'),
                'date_prescribed': med['START'],
                'patient_allergies': 'none',
                'comorbidities': 'none'
            }

            prescriptions.append(prescription)

            if (len(prescriptions) % 1000 == 0):
                print(f"  Processed {len(prescriptions)} prescriptions...")

        except Exception as e:
            # Skip prescriptions that can't be processed
            errors += 1
            if errors <= 5:  # Print first 5 errors for debugging
                print(f"  ⚠️  Error processing prescription {idx}: {str(e)}")
            continue

    print(f"  ✓ Successfully processed {len(prescriptions)} prescriptions")
    if errors > 0:
        print(f"  ⚠️  Skipped {errors} prescriptions due to errors")

    if len(prescriptions) == 0:
        print(f"\n❌ No prescriptions could be processed successfully")
        return False

    # Create DataFrame
    print(f"\n💾 Saving processed data...")
    df = pd.DataFrame(prescriptions)

    # Save to CSV
    output_file = os.path.join(output_dir, 'synthea_prescriptions.csv')
    df.to_csv(output_file, index=False)
    print(f"  ✓ Saved to: {output_file}")

    # Create import summary
    summary = {
        'import_date': datetime.now().isoformat(),
        'source': 'Synthea Synthetic Data',
        'input_directory': input_dir,
        'output_directory': output_dir,
        'statistics': {
            'total_patients': int(len(patients)),
            'total_medications': int(len(medications)),
            'total_conditions': int(len(conditions)),
            'antibiotic_prescriptions': int(len(prescriptions)),
            'unique_antibiotics': int(df['antibiotic_prescribed'].nunique()),
            'unique_diagnoses': int(df['diagnosis'].nunique()),
            'age_range': {
                'min': int(df['patient_age'].min()),
                'max': int(df['patient_age'].max()),
                'mean': float(df['patient_age'].mean())
            }
        },
        'antibiotics': df['antibiotic_prescribed'].value_counts().to_dict(),
        'diagnoses': df['diagnosis'].value_counts().head(10).to_dict()
    }

    summary_file = os.path.join(output_dir, 'import_summary.json')
    with open(summary_file, 'w') as f:
        json.dump(summary, f, indent=2)
    print(f"  ✓ Saved summary to: {summary_file}")

    # Display summary
    print(f"\n" + "=" * 70)
    print("Import Summary")
    print("=" * 70)
    print(f"✓ Total prescriptions: {len(prescriptions)}")
    print(f"✓ Unique antibiotics: {df['antibiotic_prescribed'].nunique()}")
    print(f"✓ Unique diagnoses: {df['diagnosis'].nunique()}")
    print(f"✓ Age range: {df['patient_age'].min()}-{df['patient_age'].max()} years")

    print(f"\nTop 5 Antibiotics:")
    for antibiotic, count in df['antibiotic_prescribed'].value_counts().head(5).items():
        print(f"  • {antibiotic}: {count}")

    print(f"\nTop 5 Diagnoses:")
    for diagnosis, count in df['diagnosis'].value_counts().head(5).items():
        print(f"  • {diagnosis}: {count}")

    print(f"\n" + "=" * 70)
    print("✅ Import Complete!")
    print("=" * 70)
    print(f"\nNext steps:")
    print(f"  1. Review data: {output_file}")
    print(f"  2. Label data: python scripts/label_data.py")
    print(f"  3. Train model: python scripts/train_model.py")

    return True


def main():
    """Main function"""
    import argparse

    parser = argparse.ArgumentParser(description='Import Synthea data')
    parser.add_argument('--input', default='data/synthea',
                       help='Input directory with Synthea CSV files')
    parser.add_argument('--output', default='data/synthea_processed',
                       help='Output directory for processed data')
    parser.add_argument('--limit', type=int, default=None,
                       help='Limit number of prescriptions to process')

    args = parser.parse_args()

    success = import_synthea_data(args.input, args.output, args.limit)

    if not success:
        sys.exit(1)


if __name__ == '__main__':
    main()
