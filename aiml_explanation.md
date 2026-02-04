AI/ML Explanation: AntibioticAssure System
This project implements a hybrid AI approach combining rule-based logic with machine learning to detect inappropriate antibiotic prescriptions. Here's how it works:

🏗️ System Architecture
INPUT: Prescription Data
    ↓
    ├─→ [Rule Engine] → Deterministic Rule Checks
    │   ├─ Viral infection detection
    │   ├─ Contraindication checks (allergies, age)
    │   ├─ Diagnosis-antibiotic matching
    │   ├─ Dosage validation
    │   ├─ Duration compliance
    │   └─ Broad-spectrum overuse detection
    │
    └─→ [ML Model] → Pattern Detection
        ├─ Random Forest Classifier (100 estimators)
        ├─ Trained on 818 real prescriptions
        └─ Accuracy: 96.95%
    
OUTPUT: Explanation + Risk Assessment
1️⃣ Rule-Based Engine (100% Deterministic)
Location: rule_engine.py

This enforces explicit clinical guidelines from WHO, IDSA, and CDC:

Viral Infection Check: Blocks antibiotics for known viral conditions (flu, cold, etc.)
Contraindications:
Detects patient allergies → prevents prescribed antibiotics the patient is allergic to
Age-specific restrictions → prevents adult drugs for pediatric patients
Drug interactions with comorbidities
Indication Matching: Ensures the antibiotic covers the diagnosed bacterial infection
Dosage Validation: Checks if dose is appropriate for patient age/weight
Duration Compliance: Ensures treatment length matches clinical guidelines (e.g., UTIs: 3-7 days, bacterial pneumonia: 7-14 days)
Spectrum Control: Flags unnecessary use of broad-spectrum antibiotics when narrow-spectrum would work
Reserved Antibiotics: Protects last-resort drugs (Colistin) for critical cases only
Output: List of violations with severity levels (Critical, High, Medium, Low)

2️⃣ Machine Learning Model (Pattern Detection)
Location: ml_model.py

This ML model is a Random Forest classifier that learns complex patterns:
RandomForestClassifier(
    n_estimators=100,        # 100 decision trees
    max_depth=10,            # Limits tree depth for generalization
    min_samples_split=5,     # Prevents overfitting
    min_samples_leaf=2,      
    class_weight='balanced'  # Handles imbalanced data
)

Model Configuration:

Features Extracted: (via feature engineering)

Age Features: Pediatric flag, elderly flag, age group
Dosage Features: mg per kg, total daily dose, total course dose
Duration Features: Short course (<5 days), long course (>14 days), excessive (>21 days)
Antibiotic Type: Broad-spectrum flag, antibiotic class
Patient Factors: Allergies present, comorbidities present
Diagnosis: Viral vs bacterial
Performance:

Accuracy: 96.95%
Cross-validation: 95.87% ± 1.72%
Training data: 818 prescriptions from MITRE Synthea dataset
Why Machine Learning? Rules alone can't catch subtle prescription patterns. ML finds combinations of factors that indicate inappropriate prescribing (e.g., young age + specific antibiotic + viral diagnosis might be flagged even if no single rule triggers).

3️⃣ Feature Engineering (Data Preparation)
Location: feature_engineering.py

Before training the ML model, raw prescription data is transformed into meaningful features:

Feature	Purpose	Example
patient_age	Raw age	35
is_pediatric	Binary: Age < 18	0
dosage_per_kg	Normalized dose	20 mg/kg
total_daily_dose	Cumulative daily	2000 mg
is_broad_spectrum	Binary antibiotic type	1 = broad
is_viral_diagnosis	Binary diagnosis type	0 = bacterial
This transforms raw inputs into signals the ML model can learn from.

4️⃣ Explainability (Making AI Trustworthy)
Location: explainer.py

Since doctors won't trust a "black box," the system explains its decisions:
For each prescription, you get:
├─ Prescription Summary (age, diagnosis, antibiotic, dosage)
├─ Overall Assessment (APPROPRIATE / NEEDS REVIEW / INAPPROPRIATE)
├─ Specific Violations (list with severity + explanation)
├─ Recommendations (actionable steps)
├─ Confidence Score
└─ ML Insights (if available)

Severity Levels:

🔴 CRITICAL: Immediate danger (allergic reaction risk, viral diagnosis with antibiotic)
🟠 HIGH: Serious issue (suboptimal dosage, contraindication)
🟡 MEDIUM: Review recommended (broad-spectrum when narrow would work)
🟢 LOW: Minor optimization (slightly long duration)
5️⃣ Training Pipeline
Location: train_model.py
1. Load Data → 818 labeled prescriptions from Synthea
2. Clean Data → Standardize values, handle missing data
3. Feature Engineering → Create 16+ features
4. Train/Test Split → 80/20 with stratification
5. Train Model → Random Forest learns from 654 training samples
6. Evaluate → Test on 164 unseen prescriptions
7. Save Model → Serialize for deployment

The process for training the ML model:

Cross-validation: Uses 5-fold cross-validation to ensure model generalizes to new data.

🔄 How It All Works Together
When you submit a prescription:
1. Prescription Validation → Check format/required fields
2. Preprocessing → Clean and standardize data
3. Feature Engineering → Extract 16+ features
4. Rule Engine Evaluation → Apply 7+ clinical rules
5. ML Model Prediction → Get probability score
6. Explainability Engine → Generate human-readable report
7. Return → Risk assessment + actionable recommendations

Example:
Input: 35-year-old with common cold prescribed Cephalexin 500mg 4x/day for 10 days

Rule Engine Says:
  🔴 CRITICAL: Common cold is viral; antibiotics ineffective
  🟠 HIGH: Duration too long for URI (10 days vs 3-5 days typical)

ML Model Says:
  Prediction: 88% confidence this is INAPPROPRIATE
  Similar prescriptions in training data were marked as overuse

Explanation Generated:
  "This prescription treats a viral infection with an antibiotic, 
   which is ineffective and contributes to antibiotic resistance. 
   Recommend supportive care only."

💡 Key Advantages of This Approach
Rule-Based	+ Machine Learning	= Best of Both
Fast	Detects subtle patterns	Real-time & smart
Transparent	Learns from data	Explainable decisions
Consistent	Handles edge cases	Reliable recommendations
This system combines the best of clinical expertise (rules) with data-driven intelligence (ML) to catch inappropriate prescriptions that might slip through either approach alone.

