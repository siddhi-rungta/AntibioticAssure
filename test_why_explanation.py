#!/usr/bin/env python3
"""
Test Script for "Why This Matters" Explanations
Demonstrates the new educational explanations for patients/clinicians
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from backend.preprocessing.data_cleaner import DataCleaner
from backend.models.rule_engine import RuleEngine
from backend.explainability.explainer import ExplainabilityEngine
from backend.utils.guidelines import ClinicalGuidelines


def test_paracetamol_for_pneumonia():
    """
    Test the exact case from the screenshot:
    Paracetamol prescribed for Community Acquired Pneumonia
    """
    print("\n" + "=" * 100)
    print("TEST: Paracetamol for Community Acquired Pneumonia (From Screenshot)")
    print("=" * 100)
    print("\nThis demonstrates the new 'Why This Matters' explanation feature")
    print("-" * 100)

    prescription = {
        'prescription_id': 'TEST001',
        'patient_age': 45,
        'patient_weight_kg': 70,
        'diagnosis': 'community_acquired_pneumonia',
        'antibiotic_prescribed': 'paracetamol',  # Wrong! Paracetamol is NOT an antibiotic
        'dosage_mg': 500,
        'frequency_per_day': 3,
        'duration_days': 7,
        'patient_allergies': 'none',
        'comorbidities': 'none'
    }

    # Initialize components
    guidelines = ClinicalGuidelines()
    cleaner = DataCleaner()
    rule_engine = RuleEngine(guidelines)
    explainer = ExplainabilityEngine()

    # Clean and evaluate
    cleaned = cleaner.clean_prescription_dict(prescription)
    is_appropriate, violations = rule_engine.evaluate_prescription(cleaned)
    explanation = explainer.generate_explanation(cleaned, violations)

    # Display results
    print("\n📋 PRESCRIPTION SUMMARY")
    print("-" * 100)
    summary = explanation['prescription_summary']
    print(f"  Patient Age:   {summary['patient_age']}")
    print(f"  Diagnosis:     {summary['diagnosis']}")
    print(f"  Antibiotic:    {summary['antibiotic']}")
    print(f"  Dosage:        {summary['dosage']}")
    print(f"  Duration:      {summary['duration']}")

    print("\n⚠️  OVERALL ASSESSMENT")
    print("-" * 100)
    assessment = explanation['overall_assessment']
    print(f"  Status:        {assessment['status']}")
    print(f"  Risk Level:    {assessment['risk_level']}")
    print(f"  Message:       {assessment['message']}")

    if violations:
        print("\n🚨 ISSUES DETECTED (with NEW 'Why This Matters' explanations)")
        print("=" * 100)

        for i, v in enumerate(explanation['violations'], 1):
            print(f"\n{v['icon']} ISSUE #{i}: {v['severity_label']}")
            print("-" * 100)
            print(f"  📌 Problem:    {v['message']}")

            # ⭐ NEW FEATURE: Why This Matters explanation
            if v.get('why_explanation'):
                print(f"\n  {v['why_explanation']}")

            print(f"\n  ✅ Recommendation: {v['recommendation']}")
            print("-" * 100)

    print("\n💡 KEY RECOMMENDATIONS")
    print("-" * 100)
    for i, rec in enumerate(explanation['recommendations'], 1):
        print(f"  {i}. {rec}")

    print("\n" + "=" * 100)
    print("✅ Test complete! The 'Why This Matters' explanations help patients and clinicians")
    print("   understand not just WHAT is wrong, but WHY it matters for patient safety and")
    print("   the global fight against antimicrobial resistance.")
    print("=" * 100)


def test_other_violations():
    """Test other types of violations to show various explanations"""
    print("\n\n" + "=" * 100)
    print("ADDITIONAL TESTS: Other Violation Types")
    print("=" * 100)

    test_cases = [
        {
            'name': 'Antibiotic for Viral Infection',
            'prescription': {
                'patient_age': 30,
                'patient_weight_kg': 65,
                'diagnosis': 'common_cold',
                'antibiotic_prescribed': 'amoxicillin',
                'dosage_mg': 500,
                'frequency_per_day': 3,
                'duration_days': 7,
                'patient_allergies': 'none',
                'comorbidities': 'none'
            }
        },
        {
            'name': 'Under-dosing (Resistance Risk)',
            'prescription': {
                'patient_age': 45,
                'patient_weight_kg': 70,
                'diagnosis': 'community_acquired_pneumonia',
                'antibiotic_prescribed': 'amoxicillin',
                'dosage_mg': 50,  # Way too low!
                'frequency_per_day': 3,
                'duration_days': 7,
                'patient_allergies': 'none',
                'comorbidities': 'none'
            }
        }
    ]

    for test_case in test_cases:
        print(f"\n\n📝 TEST: {test_case['name']}")
        print("-" * 100)

        guidelines = ClinicalGuidelines()
        cleaner = DataCleaner()
        rule_engine = RuleEngine(guidelines)
        explainer = ExplainabilityEngine()

        cleaned = cleaner.clean_prescription_dict(test_case['prescription'])
        is_appropriate, violations = rule_engine.evaluate_prescription(cleaned)
        explanation = explainer.generate_explanation(cleaned, violations)

        if violations:
            for v in explanation['violations']:
                print(f"\n{v['icon']} {v['severity_label']}: {v['message']}")
                if v.get('why_explanation'):
                    print(f"\n📚 Why: {v['why_explanation']}")
                print(f"\n✅ Fix: {v['recommendation']}")


if __name__ == '__main__':
    print("\n" + "=" * 100)
    print("  🏥 AI-DRIVEN ANTIBIOTIC PRESCRIPTION MONITORING SYSTEM")
    print("  ✨ NEW FEATURE: 'Why This Matters' Patient-Friendly Explanations")
    print("=" * 100)

    test_paracetamol_for_pneumonia()
    test_other_violations()

    print("\n\n" + "=" * 100)
    print("🎉 ALL TESTS COMPLETE!")
    print("-" * 100)
    print("The system now provides clear, educational explanations that help both")
    print("patients and clinicians understand:")
    print("  • WHY each violation is problematic")
    print("  • HOW it contributes to antimicrobial resistance")
    print("  • WHAT risks it poses to patient safety")
    print("\nTo see this in the web interface, run:")
    print("  FLASK_APP=backend.app python3 -m flask run")
    print("Then open http://localhost:5000 and evaluate a prescription!")
    print("=" * 100 + "\n")
