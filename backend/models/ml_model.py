"""
Machine Learning Model Module
Detects complex prescribing patterns using ML
"""

import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score
import joblib
import os
from typing import Dict, List, Tuple, Optional


class AntibioticMLModel:
    """Machine Learning model for detecting inappropriate prescriptions"""

    def __init__(self, model_type='random_forest'):
        """
        Initialize ML model

        Args:
            model_type: Type of model ('random_forest' or 'gradient_boosting')
        """
        self.model_type = model_type
        self.model = None
        self.label_encoders = {}
        self.feature_columns = []
        self.is_trained = False

        if model_type == 'random_forest':
            self.model = RandomForestClassifier(
                n_estimators=100,
                max_depth=10,
                min_samples_split=5,
                min_samples_leaf=2,
                random_state=42,
                class_weight='balanced'
            )
        elif model_type == 'gradient_boosting':
            self.model = GradientBoostingClassifier(
                n_estimators=100,
                max_depth=5,
                learning_rate=0.1,
                random_state=42
            )
        else:
            raise ValueError(f"Unknown model type: {model_type}")

    def prepare_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Prepare features for training/prediction

        Args:
            df: Dataframe with engineered features

        Returns:
            Dataframe with encoded features ready for ML
        """
        df = df.copy()

        # Define categorical columns to encode
        categorical_columns = ['age_group', 'antibiotic_class']

        for col in categorical_columns:
            if col in df.columns:
                if col not in self.label_encoders:
                    self.label_encoders[col] = LabelEncoder()
                    df[f'{col}_encoded'] = self.label_encoders[col].fit_transform(df[col].astype(str))
                else:
                    # Handle unseen labels during prediction
                    known_labels = set(self.label_encoders[col].classes_)
                    df[col] = df[col].apply(lambda x: x if x in known_labels else 'unknown')
                    df[f'{col}_encoded'] = self.label_encoders[col].transform(df[col].astype(str))

        # Define feature columns for model
        self.feature_columns = [
            'patient_age', 'is_pediatric', 'is_elderly',
            'dosage_mg', 'dosage_per_kg', 'frequency_per_day',
            'total_daily_dose', 'duration_days',
            'is_short_course', 'is_long_course', 'is_excessive_duration',
            'is_broad_spectrum', 'is_viral_diagnosis',
            'has_allergies', 'has_comorbidities',
            'age_group_encoded', 'antibiotic_class_encoded'
        ]

        # Fill missing values
        for col in self.feature_columns:
            if col in df.columns:
                df[col] = df[col].fillna(0)
            else:
                df[col] = 0

        return df

    def train(self, df: pd.DataFrame, target_column='is_appropriate') -> Dict:
        """
        Train the model

        Args:
            df: Training dataframe with features and target
            target_column: Name of target column

        Returns:
            Dictionary with training metrics
        """
        # Prepare features
        df_prepared = self.prepare_features(df)

        # Extract features and target
        X = df_prepared[self.feature_columns]
        y = df_prepared[target_column]

        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42, stratify=y
        )

        # Train model
        self.model.fit(X_train, y_train)
        self.is_trained = True

        # Evaluate
        y_pred = self.model.predict(X_test)
        y_pred_proba = self.model.predict_proba(X_test)

        # Calculate metrics
        accuracy = accuracy_score(y_test, y_pred)
        cv_scores = cross_val_score(self.model, X_train, y_train, cv=5)

        # Classification report
        class_report = classification_report(y_test, y_pred, output_dict=True)
        conf_matrix = confusion_matrix(y_test, y_pred)

        # Feature importance
        feature_importance = pd.DataFrame({
            'feature': self.feature_columns,
            'importance': self.model.feature_importances_
        }).sort_values('importance', ascending=False)

        metrics = {
            'accuracy': accuracy,
            'cv_mean_score': cv_scores.mean(),
            'cv_std_score': cv_scores.std(),
            'classification_report': class_report,
            'confusion_matrix': conf_matrix.tolist(),
            'feature_importance': feature_importance.to_dict('records'),
            'test_size': len(y_test),
            'train_size': len(y_train)
        }

        return metrics

    def predict(self, prescription_features: pd.DataFrame) -> Tuple[np.ndarray, np.ndarray]:
        """
        Predict appropriateness of prescriptions

        Args:
            prescription_features: Dataframe with prescription features

        Returns:
            Tuple of (predictions, probabilities)
        """
        if not self.is_trained:
            raise ValueError("Model must be trained before prediction")

        # Prepare features
        df_prepared = self.prepare_features(prescription_features)
        X = df_prepared[self.feature_columns]

        # Predict
        predictions = self.model.predict(X)
        probabilities = self.model.predict_proba(X)

        return predictions, probabilities

    def predict_single(self, prescription_dict: Dict) -> Dict:
        """
        Predict for a single prescription

        Args:
            prescription_dict: Dictionary with prescription features

        Returns:
            Dictionary with prediction and confidence
        """
        # Convert to dataframe
        df = pd.DataFrame([prescription_dict])

        # Predict
        predictions, probabilities = self.predict(df)

        result = {
            'is_appropriate': bool(predictions[0]),
            'confidence': float(probabilities[0][1] if predictions[0] else probabilities[0][0]),
            'probability_appropriate': float(probabilities[0][1]),
            'probability_inappropriate': float(probabilities[0][0])
        }

        return result

    def save_model(self, filepath: str):
        """
        Save trained model to file

        Args:
            filepath: Path to save model
        """
        if not self.is_trained:
            raise ValueError("Model must be trained before saving")

        model_data = {
            'model': self.model,
            'label_encoders': self.label_encoders,
            'feature_columns': self.feature_columns,
            'model_type': self.model_type
        }

        joblib.dump(model_data, filepath)
        print(f"Model saved to {filepath}")

    def load_model(self, filepath: str):
        """
        Load trained model from file

        Args:
            filepath: Path to load model from
        """
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"Model file not found: {filepath}")

        model_data = joblib.load(filepath)

        self.model = model_data['model']
        self.label_encoders = model_data['label_encoders']
        self.feature_columns = model_data['feature_columns']
        self.model_type = model_data.get('model_type', 'random_forest')
        self.is_trained = True

        print(f"Model loaded from {filepath}")

    def get_feature_importance(self, top_n: int = 10) -> List[Dict]:
        """
        Get top N most important features

        Args:
            top_n: Number of top features to return

        Returns:
            List of dictionaries with feature names and importance scores
        """
        if not self.is_trained:
            raise ValueError("Model must be trained first")

        feature_importance = pd.DataFrame({
            'feature': self.feature_columns,
            'importance': self.model.feature_importances_
        }).sort_values('importance', ascending=False).head(top_n)

        return feature_importance.to_dict('records')

    def explain_prediction(self, prescription_dict: Dict) -> Dict:
        """
        Explain prediction with feature contributions

        Args:
            prescription_dict: Prescription dictionary

        Returns:
            Dictionary with explanation
        """
        # Get prediction
        prediction_result = self.predict_single(prescription_dict)

        # Get feature importance
        importance = self.get_feature_importance(top_n=5)

        # Extract key features from prescription
        key_features = {
            'age': prescription_dict.get('patient_age'),
            'duration': prescription_dict.get('duration_days'),
            'is_viral': prescription_dict.get('is_viral_diagnosis', 0) == 1,
            'is_broad_spectrum': prescription_dict.get('is_broad_spectrum', 0) == 1,
            'dosage_per_kg': prescription_dict.get('dosage_per_kg', 0)
        }

        explanation = {
            'prediction': prediction_result,
            'key_features': key_features,
            'top_influential_features': importance,
            'model_type': self.model_type
        }

        return explanation
