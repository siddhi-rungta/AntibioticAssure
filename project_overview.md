AntibioticAssure Project Overview
This is an AI-powered Clinical Decision Support System (CDSS) designed to detect and prevent inappropriate or excessive antibiotic prescriptions, combating Antimicrobial Resistance (AMR).

🎯 Project Purpose
The system addresses critical healthcare challenges:

Over-prescription of antibiotics for viral infections
Incorrect antibiotic selection for specific bacterial infections
Improper dosing based on patient factors
Lack of real-time validation during prescription
No immediate clinical guidelines checking
🏗️ Project Architecture
Backend (Python Flask)
The backend has a modular structure:

app.py - Main Flask REST API server

Handles HTTP requests/responses
Routes for prescription evaluation, statistics, and guidelines
CORS enabled for frontend integration
preprocessing - Data Processing

data_cleaner.py - Standardizes prescription input data
feature_engineering.py - Extracts features from raw data for ML
models - Core AI Logic

ml_model.py - Random Forest classifier trained on 818 real prescriptions from MITRE Synthea data
rule_engine.py - Deterministic rule-based validation enforcing clinical guidelines (WHO, IDSA, CDC)
explainability - Model Interpretability

Uses SHAP and LIME libraries for clinician-friendly explanations
utils - Utilities

guidelines.py - Clinical guideline data and reference information
validators.py - Input validation and prescription parsing
Frontend (HTML/CSS/JavaScript)
index.html - Responsive web interface using Bootstrap 5
style.css - Styling and animations
app.js - ES6 JavaScript for API interaction and UI logic
🔥 Key Features
Hybrid Validation System
Rule-Based Engine (100% deterministic)

Checks diagnosis-antibiotic matching
Detects contraindications (allergies, age restrictions, drug interactions)
Validates dosage ranges based on weight, age
Verifies treatment duration compliance
Prevents broad-spectrum overuse
Protects reserved antibiotics (e.g., Colistin)
Machine Learning Model

96.95% accuracy (95.87% ±1.72% cross-validation)
Detects complex patterns invisible to rules
Provides confidence scores for transparency
Random Forest with 100 estimators, balanced class weights
Explainable AI (XAI)

Clinician-friendly explanations for each decision
Violation severity levels (Critical, High, Moderate, Low)
Actionable recommendations
Real-Time Features
< 1 second evaluation
Batch processing for multiple prescriptions
RESTful API for EHR integration
Interactive dashboard with statistics
Mobile-responsive design
📊 Data & Training
Data Source: MITRE Synthea

12,352 synthetic patients
818 labeled antibiotic prescriptions
Covers diverse diagnoses and patient demographics
Training Pipeline (train_model.py):

Data cleaning and standardization
Feature engineering (age groups, dosage ratios, etc.)
Train/test split with cross-validation
Model serialization for deployment
🛠️ Technology Stack
Backend:

Flask 3.0 (REST API)
scikit-learn (Random Forest ML)
pandas/numpy (Data processing)
SHAP/LIME (Explainability)
Pydantic (Data validation)
Frontend:

Bootstrap 5.3 (Responsive UI)
Vanilla JavaScript (No framework)
Fetch API (REST communication)
Data & Configuration:

JSON clinical guidelines
CSV prescription data
Python virtual environment (venv)
📂 Directory Structure
data - Training data (Synthea CSV files, clinical guidelines JSON)
backend - Python API server with AI components
frontend - Web interface (HTML/CSS/JS)
scripts - Training and data import utilities
models - Trained ML model storage
Requirements.txt - Python dependencies
🚀 How It Works
Clinician Input → Prescription details (patient info, diagnosis, antibiotic, dosage, duration)
Data Cleaning → Standardizes input format
Dual Evaluation:
Rule Engine checks against clinical guidelines
ML Model detects suspicious patterns
Explainability → Generates human-readable explanations
Output → Verdict (appropriate/inappropriate) with severity levels and actionable recommendations
This is a comprehensive final-year project combining healthcare domain knowledge with modern AI/ML techniques! 🏥⚕️

