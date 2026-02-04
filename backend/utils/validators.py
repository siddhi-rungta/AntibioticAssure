"""
Input Validation Module
Validates and sanitizes prescription data
"""

from typing import Dict, List, Optional
import re


class PrescriptionValidator:
    """Validates prescription data before processing"""

    @staticmethod
    def validate_prescription(prescription: Dict) -> tuple[bool, List[str]]:
        """
        Validate prescription data

        Args:
            prescription: Dictionary containing prescription data

        Returns:
            Tuple of (is_valid, error_messages)
        """
        errors = []

        # Required fields
        required_fields = [
            'patient_age', 'diagnosis',
            'antibiotic_prescribed', 'dosage_mg',
            'frequency_per_day', 'duration_days'
        ]

        for field in required_fields:
            if field not in prescription or prescription[field] is None or prescription[field] == '':
                errors.append(f"Missing required field: {field}")

        # If basic validation fails, return early
        if errors:
            return False, errors

        # Validate data types and ranges
        try:
            age = int(prescription['patient_age'])
            if age < 0 or age > 120:
                errors.append("Patient age must be between 0 and 120")
        except (ValueError, TypeError):
            errors.append("Patient age must be a valid number")

        try:
            dosage = float(prescription['dosage_mg'])
            if dosage <= 0:
                errors.append("Dosage must be positive")
        except (ValueError, TypeError):
            errors.append("Dosage must be a valid number")

        try:
            frequency = int(prescription['frequency_per_day'])
            if frequency < 1 or frequency > 6:
                errors.append("Frequency must be between 1 and 6 times per day")
        except (ValueError, TypeError):
            errors.append("Frequency must be a valid number")

        try:
            duration = int(prescription['duration_days'])
            if duration < 1 or duration > 365:
                errors.append("Duration must be between 1 and 365 days")
        except (ValueError, TypeError):
            errors.append("Duration must be a valid number")

        # Validate patient weight if provided
        if 'patient_weight_kg' in prescription and prescription['patient_weight_kg']:
            try:
                weight = float(prescription['patient_weight_kg'])
                if weight <= 0 or weight > 300:
                    errors.append("Patient weight must be between 0 and 300 kg")
            except (ValueError, TypeError):
                errors.append("Patient weight must be a valid number")

        # Validate antibiotic name (alphanumeric and hyphens only)
        antibiotic = prescription['antibiotic_prescribed']
        if not re.match(r'^[a-zA-Z0-9\-]+$', antibiotic):
            errors.append("Invalid antibiotic name format")

        return len(errors) == 0, errors

    @staticmethod
    def sanitize_string(value: str) -> str:
        """Remove potentially harmful characters from string"""
        if not isinstance(value, str):
            return str(value)
        # Remove special characters, keep alphanumeric, spaces, hyphens, underscores
        return re.sub(r'[^a-zA-Z0-9\s\-_]', '', value)

    @staticmethod
    def parse_allergies(allergies_str: str) -> List[str]:
        """
        Parse allergies string into list

        Args:
            allergies_str: Comma-separated allergies or 'none'

        Returns:
            List of allergies
        """
        if not allergies_str or allergies_str.lower() == 'none':
            return []

        return [a.strip().lower() for a in allergies_str.split(',') if a.strip()]

    @staticmethod
    def parse_comorbidities(comorbidities_str: str) -> List[str]:
        """
        Parse comorbidities string into list

        Args:
            comorbidities_str: Comma-separated comorbidities or 'none'

        Returns:
            List of comorbidities
        """
        if not comorbidities_str or comorbidities_str.lower() == 'none':
            return []

        return [c.strip().lower() for c in comorbidities_str.split(',') if c.strip()]
