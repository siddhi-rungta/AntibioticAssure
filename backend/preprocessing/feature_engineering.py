"""
Feature Engineering Module
Creates features for machine learning model
"""

import pandas as pd
import numpy as np
from typing import Dict, List
from backend.utils.guidelines import ClinicalGuidelines


class FeatureEngineer:
    """Creates features from prescription data for ML model"""

    def __init__(self, guidelines: ClinicalGuidelines = None):
        """
        Initialize feature engineer

        Args:
            guidelines: ClinicalGuidelines instance
        """
        self.guidelines = guidelines or ClinicalGuidelines()

    def create_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Create features from prescription data

        Args:
            df: Cleaned prescription dataframe

        Returns:
            Dataframe with engineered features
        """
        df = df.copy()

        # Age group features
        df['is_pediatric'] = (df['patient_age'] < 18).astype(int)
        df['is_elderly'] = (df['patient_age'] >= 65).astype(int)
        df['age_group'] = pd.cut(df['patient_age'],
                                  bins=[0, 12, 18, 65, 120],
                                  labels=['child', 'adolescent', 'adult', 'elderly'])

        # Dosage features
        if 'dosage_mg' in df.columns and 'patient_weight_kg' in df.columns:
            df['dosage_per_kg'] = df['dosage_mg'] / df['patient_weight_kg'].replace(0, np.nan)

        # Total daily dose
        if 'dosage_mg' in df.columns and 'frequency_per_day' in df.columns:
            df['total_daily_dose'] = df['dosage_mg'] * df['frequency_per_day']

        # Total course dose
        if 'total_daily_dose' in df.columns and 'duration_days' in df.columns:
            df['total_course_dose'] = df['total_daily_dose'] * df['duration_days']

        # Duration features
        df['is_short_course'] = (df['duration_days'] <= 5).astype(int)
        df['is_long_course'] = (df['duration_days'] > 14).astype(int)
        df['is_excessive_duration'] = (df['duration_days'] > 21).astype(int)

        # Antibiotic spectrum
        df['is_broad_spectrum'] = df['antibiotic_prescribed'].apply(
            lambda x: 1 if self.guidelines.is_broad_spectrum(x) else 0
        )

        # Viral infection flag
        df['is_viral_diagnosis'] = df['diagnosis'].apply(
            lambda x: 1 if self.guidelines.is_viral_infection(x) else 0
        )

        # Has allergies
        df['has_allergies'] = df['patient_allergies'].apply(
            lambda x: 0 if str(x).lower() == 'none' else 1
        )

        # Has comorbidities
        df['has_comorbidities'] = df['comorbidities'].apply(
            lambda x: 0 if str(x).lower() == 'none' else 1
        )

        # Antibiotic class (one-hot encoding)
        antibiotic_classes = []
        for antibiotic in df['antibiotic_prescribed']:
            ab_info = self.guidelines.get_antibiotic_info(antibiotic)
            if ab_info:
                antibiotic_classes.append(ab_info.get('class', 'unknown'))
            else:
                antibiotic_classes.append('unknown')

        df['antibiotic_class'] = antibiotic_classes

        return df

    def create_features_dict(self, prescription: Dict) -> Dict:
        """
        Create features from a single prescription dictionary

        Args:
            prescription: Prescription dictionary

        Returns:
            Dictionary with features
        """
        features = prescription.copy()

        # Age group features
        age = features.get('patient_age', 0)
        features['is_pediatric'] = 1 if age < 18 else 0
        features['is_elderly'] = 1 if age >= 65 else 0

        if age < 12:
            features['age_group'] = 'child'
        elif age < 18:
            features['age_group'] = 'adolescent'
        elif age < 65:
            features['age_group'] = 'adult'
        else:
            features['age_group'] = 'elderly'

        # Dosage features
        weight = features.get('patient_weight_kg', 70)
        dosage = features.get('dosage_mg', 0)
        frequency = features.get('frequency_per_day', 0)
        duration = features.get('duration_days', 0)

        features['dosage_per_kg'] = dosage / weight if weight > 0 else 0
        features['total_daily_dose'] = dosage * frequency
        features['total_course_dose'] = dosage * frequency * duration

        # Duration features
        features['is_short_course'] = 1 if duration <= 5 else 0
        features['is_long_course'] = 1 if duration > 14 else 0
        features['is_excessive_duration'] = 1 if duration > 21 else 0

        # Antibiotic features
        antibiotic = features.get('antibiotic_prescribed', '')
        features['is_broad_spectrum'] = 1 if self.guidelines.is_broad_spectrum(antibiotic) else 0

        # Diagnosis features
        diagnosis = features.get('diagnosis', '')
        features['is_viral_diagnosis'] = 1 if self.guidelines.is_viral_infection(diagnosis) else 0

        # Allergies and comorbidities
        allergies = str(features.get('patient_allergies', 'none')).lower()
        features['has_allergies'] = 0 if allergies == 'none' else 1

        comorbidities = str(features.get('comorbidities', 'none')).lower()
        features['has_comorbidities'] = 0 if comorbidities == 'none' else 1

        # Antibiotic class
        ab_info = self.guidelines.get_antibiotic_info(antibiotic)
        features['antibiotic_class'] = ab_info.get('class', 'unknown') if ab_info else 'unknown'

        return features

    def get_feature_names(self) -> List[str]:
        """Get list of feature names for ML model"""
        return [
            'patient_age', 'is_pediatric', 'is_elderly',
            'dosage_mg', 'dosage_per_kg', 'frequency_per_day',
            'total_daily_dose', 'total_course_dose', 'duration_days',
            'is_short_course', 'is_long_course', 'is_excessive_duration',
            'is_broad_spectrum', 'is_viral_diagnosis',
            'has_allergies', 'has_comorbidities'
        ]
