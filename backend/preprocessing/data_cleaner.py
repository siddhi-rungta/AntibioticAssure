"""
Data Preprocessing Module
Cleans and standardizes prescription data
"""

import pandas as pd
import numpy as np
from typing import Dict, List
import re


class DataCleaner:
    """Cleans and preprocesses prescription data"""

    def __init__(self):
        """Initialize data cleaner"""
        self.diagnosis_mapping = {
            'cap': 'community_acquired_pneumonia',
            'pneumonia': 'community_acquired_pneumonia',
            'uti': 'urinary_tract_infection',
            'urinary tract infection': 'urinary_tract_infection',
            'throat infection': 'streptococcal_pharyngitis',
            'strep throat': 'streptococcal_pharyngitis',
            'ear infection': 'acute_otitis_media',
            'otitis media': 'acute_otitis_media',
            'cold': 'common_cold',
            'flu': 'influenza',
            'bronchitis': 'acute_bronchitis'
        }

    def clean_dataframe(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Clean and standardize a dataframe of prescriptions

        Args:
            df: Raw prescription dataframe

        Returns:
            Cleaned dataframe
        """
        df = df.copy()

        # Handle missing values
        df = self._handle_missing_values(df)

        # Standardize column names
        df.columns = [col.lower().strip().replace(' ', '_') for col in df.columns]

        # Clean text fields
        if 'diagnosis' in df.columns:
            df['diagnosis'] = df['diagnosis'].apply(self._standardize_diagnosis)

        if 'antibiotic_prescribed' in df.columns:
            df['antibiotic_prescribed'] = df['antibiotic_prescribed'].apply(self._standardize_antibiotic_name)

        if 'patient_allergies' in df.columns:
            df['patient_allergies'] = df['patient_allergies'].fillna('none')

        if 'comorbidities' in df.columns:
            df['comorbidities'] = df['comorbidities'].fillna('none')

        # Convert numeric columns
        numeric_columns = ['patient_age', 'patient_weight_kg', 'dosage_mg',
                          'frequency_per_day', 'duration_days']
        for col in numeric_columns:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')

        # Remove rows with critical missing values
        critical_columns = ['patient_age', 'diagnosis', 'antibiotic_prescribed',
                           'dosage_mg', 'frequency_per_day', 'duration_days']
        df = df.dropna(subset=[col for col in critical_columns if col in df.columns])

        return df

    def _handle_missing_values(self, df: pd.DataFrame) -> pd.DataFrame:
        """Handle missing values in dataframe"""
        df = df.copy()

        # Fill missing weight with median based on age group
        if 'patient_weight_kg' in df.columns and 'patient_age' in df.columns:
            df['patient_weight_kg'] = df.groupby(
                pd.cut(df['patient_age'], bins=[0, 12, 18, 65, 120])
            )['patient_weight_kg'].transform(lambda x: x.fillna(x.median()))

        return df

    def _standardize_diagnosis(self, diagnosis: str) -> str:
        """
        Standardize diagnosis names

        Args:
            diagnosis: Raw diagnosis string

        Returns:
            Standardized diagnosis name
        """
        if pd.isna(diagnosis):
            return 'unknown'

        diagnosis_lower = diagnosis.lower().strip()

        # Check mapping
        if diagnosis_lower in self.diagnosis_mapping:
            return self.diagnosis_mapping[diagnosis_lower]

        # Replace spaces with underscores
        standardized = re.sub(r'\s+', '_', diagnosis_lower)
        standardized = re.sub(r'[^a-z0-9_]', '', standardized)

        return standardized

    def _standardize_antibiotic_name(self, antibiotic: str) -> str:
        """
        Standardize antibiotic names

        Args:
            antibiotic: Raw antibiotic name

        Returns:
            Standardized antibiotic name
        """
        if pd.isna(antibiotic):
            return 'unknown'

        # Convert to lowercase and remove extra spaces
        standardized = antibiotic.lower().strip()

        # Remove brand name suffixes
        standardized = re.sub(r'\s+(tablet|capsule|suspension|injection).*$', '', standardized)

        # Remove dosage forms
        standardized = re.sub(r'\s+\d+mg.*$', '', standardized)

        return standardized

    def clean_prescription_dict(self, prescription: Dict) -> Dict:
        """
        Clean a single prescription dictionary

        Args:
            prescription: Raw prescription dictionary

        Returns:
            Cleaned prescription dictionary
        """
        cleaned = prescription.copy()

        # Standardize diagnosis
        if 'diagnosis' in cleaned:
            cleaned['diagnosis'] = self._standardize_diagnosis(cleaned['diagnosis'])

        # Standardize antibiotic name
        if 'antibiotic_prescribed' in cleaned:
            cleaned['antibiotic_prescribed'] = self._standardize_antibiotic_name(
                cleaned['antibiotic_prescribed']
            )

        # Convert numeric fields
        numeric_fields = ['patient_age', 'patient_weight_kg', 'dosage_mg',
                         'frequency_per_day', 'duration_days']
        for field in numeric_fields:
            if field in cleaned and cleaned[field] is not None:
                try:
                    cleaned[field] = float(cleaned[field])
                except (ValueError, TypeError):
                    cleaned[field] = None

        return cleaned
