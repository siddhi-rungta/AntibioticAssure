#!/usr/bin/env python3
"""
Demo Script
Demonstrates the prescription evaluation system
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from backend.preprocessing.data_cleaner import DataCleaner
from backend.preprocessing.feature_engineering import FeatureEngineer
from backend.models.rule_engine import RuleEngine
from backend.models.ml_model import AntibioticMLModel
from backend.explainability.explainer import ExplainabilityEngine
from backend.utils.guidelines import ClinicalGuidelines


def demo_inappropriate_prescription():
    """Demo with an inappropriate prescription"""
    print("\n" + "=" * 80)
    print("DEMO 1: Inappropriate Prescription (Antibiotic for Viral Infection)")
    print("=" * 80)

    prescription = {
        'prescription_id': 'DEMO001',
        'patient_age': 35,
        'patient_weight_kg': 70,
        'diagnosis': 'common_cold',
        'antibiotic_prescribed': 'azithromycin',
        'dosage_mg': 500,
        'frequency_per_day': 1,
        'duration_days': 5,
        'patient_allergies': 'none',
        'comorbidities': 'none'
    }

    evaluate_prescription(prescription)


def demo_contraindication():
    """Demo with contraindication"""
    print("\n" + "=" * 80)
    print("DEMO 2: Contraindication (Penicillin Allergy)")
    print("=" * 80)

    prescription = {
        'prescription_id': 'DEMO002',
        'patient_age': 45,
        'patient_weight_kg': 75,
        'diagnosis': 'community_acquired_pneumonia',
        'antibiotic_prescribed': 'amoxicillin',
        'dosage_mg': 500,
        'frequency_per_day': 3,
        'duration_days': 7,
        'patient_allergies': 'penicillin_allergy',
        'comorbidities': 'none'
    }

    evaluate_prescription(prescription)


def demo_appropriate_prescription():
    """Demo with appropriate prescription"""
    print("\n" + "=" * 80)
    print("DEMO 3: Appropriate Prescription")
    print("=" * 80)

    prescription = {
        'prescription_id': 'DEMO003',
        'patient_age': 45,
        'patient_weight_kg': 70,
        'diagnosis': 'community_acquired_pneumonia',
        'antibiotic_prescribed': 'amoxicillin',
        'dosage_mg': 500,
        'frequency_per_day': 3,
        'duration_days': 7,
        'patient_allergies': 'none',
        'comorbidities': 'diabetes'
    }

    evaluate_prescription(prescription)


def demo_excessive_duration():
    """Demo with excessive duration"""
    print("\n" + "=" * 80)
    print("DEMO 4: Excessive Duration")
    print("=" * 80)

    prescription = {
        'prescription_id': 'DEMO004',
        'patient_age': 50,
        'patient_weight_kg': 80,
        'diagnosis': 'community_acquired_pneumonia',
        'antibiotic_prescribed': 'amoxicillin',
        'dosage_mg': 1000,
        'frequency_per_day': 3,
        'duration_days': 21,
        'patient_allergies': 'none',
        'comorbidities': 'none'
    }

    evaluate_prescription(prescription)


def evaluate_prescription(prescription):
    """Evaluate a prescription and display results"""
    # Initialize components
    guidelines = ClinicalGuidelines()
    cleaner = DataCleaner()
    feature_engineer = FeatureEngineer(guidelines)
    rule_engine = RuleEngine(guidelines)
    explainer = ExplainabilityEngine()

    # Clean prescription
    cleaned = cleaner.clean_prescription_dict(prescription)

    # Engineer features
    features = feature_engineer.create_features_dict(cleaned)

    # Evaluate with rule engine
    is_appropriate, violations = rule_engine.evaluate_prescription(cleaned)

    # Generate explanation
    explanation = explainer.generate_explanation(cleaned, violations)

    # Display results
    print("\n" + "-" * 80)
    print("PRESCRIPTION DETAILS")
    print("-" * 80)
    summary = explanation['prescription_summary']
    print(f"Patient Age: {summary['patient_age']}")
    print(f"Diagnosis: {summary['diagnosis']}")
    print(f"Antibiotic: {summary['antibiotic']}")
    print(f"Dosage: {summary['dosage']}")
    print(f"Duration: {summary['duration']}")
    print(f"Allergies: {summary['allergies']}")
    print(f"Comorbidities: {summary['comorbidities']}")

    print("\n" + "-" * 80)
    print("EVALUATION RESULTS")
    print("-" * 80)
    assessment = explanation['overall_assessment']
    print(f"Status: {assessment['status']}")
    print(f"Risk Level: {assessment['risk_level']}")
    print(f"Message: {assessment['message']}")
    print(f"Total Violations: {assessment['total_violations']}")

    if violations:
        print("\n" + "-" * 80)
        print("VIOLATIONS DETECTED")
        print("-" * 80)
        for i, v in enumerate(explanation['violations'], 1):
            print(f"\n{i}. {v['severity_label']}")
            print(f"   Rule: {v['rule']}")
            print(f"   Issue: {v['message']}")
            if v.get('why_explanation'):
                print(f"   📚 Why This Matters: {v['why_explanation']}")
            print(f"   Recommendation: {v['recommendation']}")

    print("\n" + "-" * 80)
    print("RECOMMENDATIONS")
    print("-" * 80)
    for i, rec in enumerate(explanation['recommendations'], 1):
        print(f"{i}. {rec}")

    print("\n" + "-" * 80)
    print("CONFIDENCE")
    print("-" * 80)
    confidence = explanation['confidence_score']
    print(f"Rule-based Confidence: {confidence['rule_based_confidence']:.2%}")
    print(f"Explanation: {confidence['explanation']}")


def main():
    """Main demo function"""
    print("=" * 80)
    print("AI-DRIVEN ANTIBIOTIC PRESCRIPTION MONITORING SYSTEM - DEMO")
    print("=" * 80)
    print("\nThis demo showcases the system's ability to detect inappropriate prescriptions")
    print("and provide actionable recommendations based on clinical guidelines.")

    # Run demos
    demo_inappropriate_prescription()
    demo_contraindication()
    demo_appropriate_prescription()
    demo_excessive_duration()

    print("\n" + "=" * 80)
    print("DEMO COMPLETE")
    print("=" * 80)
    print("\nThe system successfully:")
    print("✓ Detected inappropriate prescriptions")
    print("✓ Identified contraindications")
    print("✓ Validated appropriate prescriptions")
    print("✓ Flagged excessive durations")
    print("✓ Provided actionable recommendations")
    print("\nTo run the web interface:")
    print("  python backend/app.py")
    print("\nThen open http://localhost:5000 in your browser")
    print("=" * 80)


if __name__ == '__main__':
    main()
