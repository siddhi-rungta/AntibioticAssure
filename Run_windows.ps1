Clear-Host

Write-Host ""
Write-Host "AI-Driven Antibiotic Prescription Monitoring System"
Write-Host "Automated Setup And Run Script"
Write-Host ""

# Check Python
$python = Get-Command python -ErrorAction SilentlyContinue
if ($null -eq $python) {
    Write-Host "ERROR: Python not found. Install Python 3.9 or higher."
    exit 1
}

python --version
Write-Host ""

# Step 1: Virtual Environment
Write-Host "Step 1: Virtual Environment"

$VENV_PYTHON = ".\venv\Scripts\python.exe"

$venvValid = (Test-Path "venv\pyvenv.cfg") -and `
             (Test-Path $VENV_PYTHON) -and `
             (Test-Path "venv\Lib\site-packages")

if ($venvValid) {
    Write-Host "Using existing virtual environment"
}
else {
    Write-Host "Virtual environment missing or broken"
    Write-Host "Creating fresh virtual environment. Please wait."

    if (Test-Path "venv") {
        Remove-Item -Recurse -Force venv
    }

    python -m venv venv
    Start-Sleep -Seconds 3

    if (-not (Test-Path $VENV_PYTHON)) {
        Write-Host "ERROR: Virtual environment creation failed"
        exit 1
    }

    Write-Host "Virtual environment created"
}

Write-Host ""

# Step 2: Dependencies
Write-Host "Step 2: Dependencies"

if (Test-Path "venv\.deps_installed") {
    Write-Host "Dependencies already installed. Skipping."
}
else {
    Write-Host "Installing dependencies."

    & $VENV_PYTHON -m pip install --upgrade pip
    & $VENV_PYTHON -m pip install -r requirements.txt

    if ($LASTEXITCODE -ne 0) {
        Write-Host "ERROR: Dependency installation failed"
        exit 1
    }

    New-Item "venv\.deps_installed" -ItemType File | Out-Null
    Write-Host "Dependencies installed"
}

Write-Host ""

# Step 3: Train Model
Write-Host "Step 3: Training model"

if (-not (Test-Path "models\trained_model.pkl")) {
    & $VENV_PYTHON scripts\train_model.py
}
else {
    $ans = Read-Host "Model exists. Retrain? (y or N)"
    if ($ans -eq "y" -or $ans -eq "Y") {
        & $VENV_PYTHON scripts\train_model.py
    }
}

Write-Host ""

# Step 4: Demo
Write-Host "Step 4: Running demo"
Read-Host "Press Enter to continue"

& $VENV_PYTHON scripts\demo.py

Write-Host ""
Write-Host "Demo completed"
Write-Host ""

# Step 5: Web Server
Write-Host "Step 5: Web Server"
$start = Read-Host "Start web server? (Y or n)"

if ($start -ne "n" -and $start -ne "N") {
    Write-Host "Starting web server at http://localhost:5000"
    Start-Sleep -Seconds 2
    Start-Process "http://localhost:5000"

    $env:FLASK_APP = "backend.app"
    & $VENV_PYTHON -m flask run --host=0.0.0.0 --port=5000
}
else {
    Write-Host ""
    Write-Host "Setup complete"
    Write-Host ""
    Write-Host "To start server later:"
    Write-Host ".\venv\Scripts\python.exe -m flask run --host=0.0.0.0 --port=5000"
    Write-Host ""
    Write-Host "To run demo again:"
    Write-Host ".\venv\Scripts\python.exe scripts\demo.py"
}
