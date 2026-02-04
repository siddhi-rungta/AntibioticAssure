# Utility Scripts

This directory contains utility scripts for training, testing, and labeling data.

---

## 📜 Available Scripts

### 1. `train_model.py` - Train ML Model

**Purpose:** Trains the Random Forest classifier on prescription data

**Usage:**
```bash
# Train with default data
python scripts/train_model.py
```

**What it does:**
- Loads prescription data from `data/sample_prescriptions.csv`
- Cleans and preprocesses the data
- Engineers features for ML model
- Trains Random Forest classifier
- Evaluates model performance
- Saves trained model to `models/trained_model.pkl`

**Output:**
```
Training Antibiotic Prescription ML Model
============================================================

📂 Loading sample data...
✓ Loaded 40,118 prescriptions

🔧 Initializing components...
✓ Cleaner, Feature Engineer, ML Model initialized

🧹 Cleaning data...
✓ Data cleaned: 40,118 → 40,118 records

🏗️ Engineering features...
✓ Created 15 features

📊 Splitting data...
✓ Train: 28,082 | Test: 12,036

🤖 Training model...
✓ Model trained

📈 Evaluating model...
✓ Accuracy: 85.2%
✓ Precision: 83.7%
✓ Recall: 87.1%
✓ F1-Score: 85.4%

💾 Saving model...
✓ Model saved to models/trained_model.pkl

✅ Training Complete!
```

---

### 2. `demo.py` - Command Line Demo

**Purpose:** Demonstrates the prescription evaluation system with 4 scenarios

**Usage:**
```bash
python scripts/demo.py
```

**What it shows:**
1. **❌ Inappropriate** - Antibiotic for viral infection (Common Cold)
2. **✅ Appropriate** - Correct antibiotic for bacterial infection (Pneumonia)
3. **🚨 Contraindicated** - Patient allergic to prescribed antibiotic
4. **⚠️ Excessive** - Dosage too high for patient weight

**Output:**
- Detailed prescription evaluation
- Rule violations
- ML predictions (if model trained)
- Recommendations
- Confidence scores

---

### 3. `label_data.py` - Auto-Label Prescriptions

**Purpose:** Automatically labels prescriptions using the rule engine

**Usage:**
```bash
python scripts/label_data.py
```

**What it does:**
- Loads prescriptions from `data/sample_prescriptions.csv`
- Evaluates each prescription using rule engine
- Adds `is_appropriate` label (1 = appropriate, 0 = inappropriate)
- Saves labeled data back to `data/sample_prescriptions.csv`

**When to use:**
- After importing new prescription data
- When you need labeled training data
- To validate rule engine consistency

**Output:**
```
Auto-Labeling Prescriptions
============================================================

🔧 Initializing rule engine...
✓ Rule engine initialized

📂 Loading prescription data...
✓ Loaded 40,118 prescriptions

🏷️  Labeling prescriptions...
  Processed 10/40118 prescriptions...
  Processed 20/40118 prescriptions...
  ...

✅ Labeled data saved to: data/sample_prescriptions.csv

📊 Summary:
   Total: 40,118
   Appropriate: 26,077 (65.0%)
   Inappropriate: 14,041 (35.0%)

✅ Labeling Complete!
```

---

## 🔄 Typical Workflow

### For Normal Use (System Already Set Up):

1. **Run the application:**
   ```bash
   ./RUN_ME_FIRST.sh
   ```

### For Adding New Data:

1. **Add new prescriptions to `data/sample_prescriptions.csv`**

2. **Label the data:**
   ```bash
   python scripts/label_data.py
   ```

3. **Retrain the model:**
   ```bash
   python scripts/train_model.py
   ```

4. **Test with demo:**
   ```bash
   python scripts/demo.py
   ```

5. **Start the web server:**
   ```bash
   FLASK_APP=backend.app python3 -m flask run --host=0.0.0.0 --port=5000
   ```

---

## 📊 Data Format

The system expects prescriptions in this format:

| Column | Type | Description |
|--------|------|-------------|
| `prescription_id` | string | Unique identifier (optional, auto-generated) |
| `patient_age` | int | Patient age in years |
| `patient_weight_kg` | float | Patient weight in kg |
| `diagnosis` | string | Primary diagnosis |
| `antibiotic_prescribed` | string | Antibiotic name (lowercase) |
| `dosage_mg` | int | Dosage in milligrams |
| `frequency_per_day` | int | Times per day |
| `duration_days` | int | Treatment duration in days |
| `patient_allergies` | string | Patient allergies (comma-separated) |
| `comorbidities` | string | Comorbid conditions (comma-separated) |
| `is_appropriate` | int | 1 = appropriate, 0 = inappropriate (for training) |

---

## 🔧 Troubleshooting

### Error: "FileNotFoundError: data/sample_prescriptions.csv"
**Solution:** Make sure you're running from the project root directory:
```bash
cd /path/to/finalyear
python scripts/train_model.py
```

### Error: "No module named 'backend'"
**Solution:** Activate the virtual environment first:
```bash
source venv/bin/activate
python scripts/train_model.py
```

### Error: "ModuleNotFoundError: No module named 'sklearn'"
**Solution:** Install dependencies:
```bash
pip install -r requirements.txt
```

### Model training takes too long
**Solution:** This is normal for 40,000+ records. Training takes ~2-3 minutes on modern hardware.

### Low model accuracy
**Possible causes:**
- Insufficient training data
- Imbalanced classes
- Need feature engineering improvements

**Solutions:**
- Add more labeled data
- Use `label_data.py` to ensure consistent labeling
- Check data quality in `data/sample_prescriptions.csv`

---

## 💡 Tips

1. **Always activate venv before running scripts:**
   ```bash
   source venv/bin/activate
   ```

2. **Run from project root:**
   ```bash
   cd /path/to/finalyear
   python scripts/script_name.py
   ```

3. **Check model performance regularly:**
   - After adding new data
   - When guidelines change
   - Before production deployment

4. **Use demo.py for quick testing:**
   - Fast way to verify system works
   - Shows all components in action
   - Good for presentations

---

*Last Updated: February 4, 2026*
