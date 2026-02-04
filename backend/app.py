"""
Main Flask Application
AI-Driven Antibiotic Prescription Monitoring System
"""

from flask import Flask, request, jsonify, render_template, send_from_directory, make_response
from flask_cors import CORS
import pandas as pd
import os
from datetime import datetime
from typing import Dict, List
from functools import wraps

# Import backend modules
from backend.preprocessing.data_cleaner import DataCleaner
from backend.preprocessing.feature_engineering import FeatureEngineer
from backend.models.rule_engine import RuleEngine
from backend.models.ml_model import AntibioticMLModel
from backend.explainability.explainer import ExplainabilityEngine
from backend.utils.guidelines import ClinicalGuidelines
from backend.utils.validators import PrescriptionValidator

# Initialize Flask app
app = Flask(__name__,
            template_folder='../frontend',
            static_folder='../frontend',
            static_url_path='/static')
CORS(app)

# Disable caching in development
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0

def add_no_cache_headers(response):
    """Add no-cache headers to response"""
    response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, post-check=0, pre-check=0, max-age=0'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '-1'
    return response

@app.after_request
def after_request(response):
    """Add no-cache headers to all responses"""
    return add_no_cache_headers(response)

# Initialize system components
guidelines = ClinicalGuidelines()
data_cleaner = DataCleaner()
feature_engineer = FeatureEngineer(guidelines)
rule_engine = RuleEngine(guidelines)
ml_model = AntibioticMLModel(model_type='random_forest')
explainer = ExplainabilityEngine()
validator = PrescriptionValidator()

# Global variables
MODEL_TRAINED = False
BASE_DIR = os.path.dirname(os.path.dirname(__file__))


@app.route('/')
def index():
    """Serve main page"""
    return render_template('index.html')


@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'model_trained': MODEL_TRAINED,
        'timestamp': datetime.now().isoformat()
    })


@app.route('/api/evaluate', methods=['POST'])
def evaluate_prescription():
    """
    Evaluate a prescription

    Request body:
    {
        "prescription_id": "P001",
        "patient_age": 45,
        "patient_weight_kg": 70,
        "diagnosis": "community_acquired_pneumonia",
        "antibiotic_prescribed": "amoxicillin",
        "dosage_mg": 500,
        "frequency_per_day": 3,
        "duration_days": 7,
        "patient_allergies": "none",
        "comorbidities": "none"
    }
    """
    try:
        prescription = request.json

        # Validate input
        is_valid, validation_errors = validator.validate_prescription(prescription)
        if not is_valid:
            return jsonify({
                'success': False,
                'errors': validation_errors
            }), 400

        # Clean data
        prescription_clean = data_cleaner.clean_prescription_dict(prescription)

        # Evaluate with rule engine
        is_appropriate, violations = rule_engine.evaluate_prescription(prescription_clean)

        # Get ML prediction if model is trained
        ml_prediction_dict = None

        if MODEL_TRAINED:
            # Create features for ML
            features_df = feature_engineer.create_features(pd.DataFrame([prescription_clean]))

            # Get prediction
            prediction = ml_model.predict(features_df)
            probabilities = ml_model.predict_proba(features_df)

            ml_prediction_dict = {
                'prediction': 'appropriate' if prediction[0] == 1 else 'inappropriate',
                'confidence': float(probabilities[0][prediction[0]]),
                'agrees_with_rules': (prediction[0] == 1 and is_appropriate) or (prediction[0] == 0 and not is_appropriate)
            }

        # Generate explanation
        explanation = explainer.generate_explanation(
            prescription=prescription_clean,
            rule_violations=violations,
            ml_prediction=ml_prediction_dict
        )

        return jsonify({
            'success': True,
            'prescription_id': prescription.get('prescription_id', 'N/A'),
            'is_appropriate': is_appropriate,
            'explanation': explanation
        })

    except Exception as e:
        import traceback
        print(f"ERROR in /api/evaluate: {str(e)}")
        print(traceback.format_exc())
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/statistics', methods=['GET'])
def get_statistics():
    """Get system statistics"""
    try:
        # Load sample data
        data_path = os.path.join(BASE_DIR, 'data', 'sample_prescriptions.csv')

        if not os.path.exists(data_path):
            return jsonify({
                'success': True,
                'statistics': {
                    'total_prescriptions': 0,
                    'appropriate': 0,
                    'inappropriate': 0,
                    'appropriateness_rate': 0,
                    'antibiotics_monitored': len(guidelines.get_all_antibiotics()),
                    'model_trained': MODEL_TRAINED
                }
            })

        df = pd.read_csv(data_path)

        # Calculate statistics
        total = len(df)

        if 'is_appropriate' in df.columns:
            appropriate = int(df['is_appropriate'].sum())
            inappropriate = total - appropriate
            appropriateness_rate = (appropriate / total * 100) if total > 0 else 0
        else:
            # Evaluate each prescription if not labeled
            appropriate = 0
            for _, row in df.iterrows():
                is_app, _ = rule_engine.evaluate_prescription(row.to_dict())
                if is_app:
                    appropriate += 1
            inappropriate = total - appropriate
            appropriateness_rate = (appropriate / total * 100) if total > 0 else 0

        return jsonify({
            'success': True,
            'statistics': {
                'total_prescriptions': total,
                'appropriate': appropriate,
                'inappropriate': inappropriate,
                'appropriateness_rate': appropriateness_rate,
                'antibiotics_monitored': len(guidelines.get_all_antibiotics()),
                'model_trained': MODEL_TRAINED
            }
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/guidelines', methods=['GET'])
def get_guidelines():
    """Get clinical guidelines"""
    try:
        antibiotics = guidelines.get_all_antibiotics()

        return jsonify({
            'success': True,
            'antibiotics': sorted(antibiotics),
            'total_antibiotics': len(antibiotics)
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/train-model', methods=['POST'])
def train_model():
    """Train ML model endpoint"""
    global MODEL_TRAINED

    try:
        # Check if file uploaded
        if 'file' in request.files:
            file = request.files['file']
            if file.filename:
                # Save uploaded file
                filepath = os.path.join(BASE_DIR, 'data', 'uploaded_training_data.csv')
                file.save(filepath)
                data_path = filepath
            else:
                data_path = os.path.join(BASE_DIR, 'data', 'sample_prescriptions.csv')
        else:
            data_path = os.path.join(BASE_DIR, 'data', 'sample_prescriptions.csv')

        # Load data
        df = pd.read_csv(data_path)

        # Clean data
        df_clean = df.apply(lambda row: pd.Series(data_cleaner.clean_prescription(row.to_dict())), axis=1)

        # Create features
        df_features = feature_engineer.create_features(df_clean)

        # Train model
        metrics = ml_model.train(df_features, target_column='is_appropriate')

        # Save model
        model_path = os.path.join(BASE_DIR, 'models', 'trained_model.pkl')
        ml_model.save_model(model_path)

        MODEL_TRAINED = True

        return jsonify({
            'success': True,
            'message': 'Model trained successfully',
            'metrics': metrics
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


if __name__ == '__main__':
    # Try to load existing model
    model_path = os.path.join(BASE_DIR, 'models', 'trained_model.pkl')
    if os.path.exists(model_path):
        try:
            ml_model.load_model(model_path)
            MODEL_TRAINED = True
            print(f"✓ Loaded trained model from {model_path}")
        except Exception as e:
            print(f"⚠ Could not load model: {e}")
            MODEL_TRAINED = False

    # Run app
    app.run(host='0.0.0.0', port=5000, debug=False)
