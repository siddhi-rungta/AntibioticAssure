Write-Host ""
Write-Host "=============================================" -ForegroundColor Cyan
Write-Host " AI Antibiotic System - Windows Setup" -ForegroundColor Cyan
Write-Host "=============================================" -ForegroundColor Cyan
Write-Host ""

# Step 1: Check Python
Write-Host "Checking Python..." -ForegroundColor Yellow
python --version

# Step 2: Create venv
if (!(Test-Path "venv")) {
    Write-Host "Creating virtual environment..." -ForegroundColor Yellow
    python -m venv venv
} else {
    Write-Host "Virtual environment already exists" -ForegroundColor Green
}

# Step 3: Activate venv
Write-Host "Activating virtual environment..." -ForegroundColor Yellow
. .\venv\Scripts\Activate.ps1

# Step 4: Upgrade pip
Write-Host "Upgrading pip..." -ForegroundColor Yellow
python -m pip install --upgrade pip

# Step 5: Install dependencies
Write-Host "Installing dependencies..." -ForegroundColor Yellow

if (Test-Path "requirements.txt") {
    pip install -r requirements.txt
} else {
    Write-Host "requirements.txt not found, installing manually..."
    pip install flask pandas numpy scikit-learn pillow pytesseract easyocr opencv-python
}

# Step 6: Force fix numpy issue (VERY IMPORTANT)
Write-Host "Fixing numpy compatibility..." -ForegroundColor Yellow
pip install --upgrade --force-reinstall numpy

# Step 7: Install OCR extras (ensures no failure)
Write-Host "Ensuring OCR libraries..." -ForegroundColor Yellow
pip install easyocr pytesseract opencv-python

# Step 8: Check Tesseract (optional)
$tesseractPath = "C:\Program Files\Tesseract-OCR\tesseract.exe"
if (Test-Path $tesseractPath) {
    Write-Host "Tesseract found ✓" -ForegroundColor Green
} else {
    Write-Host "Tesseract not installed (OCR may be limited)" -ForegroundColor Red
    Write-Host "Download: https://github.com/tesseract-ocr/tesseract"
}

# Step 9: Train model (optional)
if (!(Test-Path "models\trained_model.pkl")) {
    Write-Host "Training ML model..." -ForegroundColor Yellow
    python scripts\train_model.py
} else {
    Write-Host "Model already exists ✓" -ForegroundColor Green
}

# Step 10: Run Flask
Write-Host ""
Write-Host "Starting server at http://localhost:5000" -ForegroundColor Green
$env:FLASK_APP="backend.app"
.\venv\Scripts\python -m flask run --host=0.0.0.0 --port=5000