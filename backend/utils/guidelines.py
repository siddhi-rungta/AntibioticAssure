"""
Clinical Guidelines Module
Loads and manages antibiotic prescribing guidelines
"""

import json
import os
from typing import Dict, List, Optional


class ClinicalGuidelines:
    """Manages clinical guidelines for antibiotic prescribing"""

    def __init__(self, guidelines_path: str = None):
        """
        Initialize guidelines from JSON file

        Args:
            guidelines_path: Path to guidelines JSON file
        """
        if guidelines_path is None:
            base_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
            guidelines_path = os.path.join(base_dir, 'data', 'clinical_guidelines.json')

        with open(guidelines_path, 'r') as f:
            self.guidelines = json.load(f)

        self.antibiotic_guidelines = self.guidelines.get('antibiotic_guidelines', {})
        self.diagnosis_to_antibiotic = self.guidelines.get('diagnosis_to_antibiotic', {})
        self.stewardship_rules = self.guidelines.get('stewardship_rules', {})

    def get_antibiotic_info(self, antibiotic: str) -> Optional[Dict]:
        """
        Get information about a specific antibiotic

        Args:
            antibiotic: Name of the antibiotic (lowercase)

        Returns:
            Dictionary with antibiotic information or None
        """
        return self.antibiotic_guidelines.get(antibiotic.lower())

    def get_recommended_antibiotics(self, diagnosis: str) -> Optional[Dict]:
        """
        Get recommended antibiotics for a diagnosis

        Args:
            diagnosis: Diagnosis code or name

        Returns:
            Dictionary with recommended antibiotics
        """
        return self.diagnosis_to_antibiotic.get(diagnosis.lower().replace(' ', '_'))

    def is_viral_infection(self, diagnosis: str) -> bool:
        """
        Check if diagnosis is viral (antibiotics not needed)

        Args:
            diagnosis: Diagnosis name

        Returns:
            True if viral, False otherwise
        """
        viral_diagnoses = self.stewardship_rules.get('no_antibiotics_for_viral', {}).get('viral_diagnoses', [])
        return diagnosis.lower().replace(' ', '_') in viral_diagnoses

    def is_broad_spectrum(self, antibiotic: str) -> bool:
        """
        Check if antibiotic is broad-spectrum

        Args:
            antibiotic: Antibiotic name

        Returns:
            True if broad-spectrum, False otherwise
        """
        ab_info = self.get_antibiotic_info(antibiotic)
        if ab_info:
            return ab_info.get('spectrum') == 'broad'
        return False

    def get_dosage_range(self, antibiotic: str, patient_age: int, patient_weight: float = None) -> Optional[Dict]:
        """
        Get appropriate dosage range for antibiotic

        Args:
            antibiotic: Antibiotic name
            patient_age: Patient age in years
            patient_weight: Patient weight in kg (for pediatric dosing)

        Returns:
            Dictionary with dosage information
        """
        ab_info = self.get_antibiotic_info(antibiotic)
        if not ab_info:
            return None

        # Pediatric dosing (under 18)
        if patient_age < 18:
            return ab_info.get('pediatric_dosage', ab_info.get('adult_dosage'))
        else:
            return ab_info.get('adult_dosage')

    def check_contraindications(self, antibiotic: str, patient_allergies: List[str],
                                patient_age: int, comorbidities: List[str]) -> List[str]:
        """
        Check for contraindications

        Args:
            antibiotic: Antibiotic name
            patient_allergies: List of patient allergies
            patient_age: Patient age
            comorbidities: List of patient comorbidities

        Returns:
            List of contraindication warnings
        """
        warnings = []
        ab_info = self.get_antibiotic_info(antibiotic)

        if not ab_info:
            return warnings

        contraindications = ab_info.get('contraindications', [])

        # Check allergies
        for allergy in patient_allergies:
            if allergy.lower() in [c.lower() for c in contraindications]:
                warnings.append(f"CONTRAINDICATION: Patient allergic to {allergy}")

        # Check age-related contraindications
        if patient_age < 18 and 'children_under_18' in contraindications:
            warnings.append(f"CONTRAINDICATION: {antibiotic} not recommended for patients under 18")

        if patient_age < 8 and 'children_under_8' in contraindications:
            warnings.append(f"CONTRAINDICATION: {antibiotic} not recommended for children under 8")

        # Check comorbidities
        for condition in comorbidities:
            if condition.lower() in [c.lower() for c in contraindications]:
                warnings.append(f"CONTRAINDICATION: {antibiotic} contraindicated with {condition}")

        # Check for special warnings
        if 'warnings' in ab_info:
            for warning in ab_info['warnings']:
                warnings.append(f"WARNING: {warning}")

        return warnings

    def get_all_antibiotics(self) -> List[str]:
        """Get list of all antibiotics in guidelines"""
        return list(self.antibiotic_guidelines.keys())
