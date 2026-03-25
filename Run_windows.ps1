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

# Step 2.1: Optional PaddleOCR Backend
Write-Host "Step 2.1: Optional PaddleOCR backend"

if (Test-Path "venv\.paddle_installed") {
    Write-Host "PaddleOCR already installed. Skipping."
}
else {
    $installPaddle = Read-Host "Install PaddleOCR + PaddlePaddle now? (Y or n)"
    if ($installPaddle -ne "n" -and $installPaddle -ne "N") {
        # PaddlePaddle wheels are not available for latest Python versions (e.g. 3.14).
        $pyVersionRaw = & $VENV_PYTHON -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')"
        $pyVersion = $pyVersionRaw.Trim()
        $supportedForPaddle = @("3.10", "3.11", "3.12", "3.13")

        if ($supportedForPaddle -contains $pyVersion) {
            Write-Host "Installing PaddleOCR backend. Please wait."
            & $VENV_PYTHON -m pip install paddleocr==2.7.3 paddlepaddle==2.6.2

            if ($LASTEXITCODE -eq 0) {
                New-Item "venv\.paddle_installed" -ItemType File | Out-Null
                Write-Host "PaddleOCR backend installed successfully."
            }
            else {
                Write-Host "WARNING: PaddleOCR backend installation failed."
                Write-Host "The app will still run with EasyOCR fallback."
                Write-Host "Tip: Paddle packages may require Python 3.10/3.11."
            }
        }
        else {
            Write-Host "Python $pyVersion cannot install PaddlePaddle in this venv."
            Write-Host "Creating/using Python 3.11 virtual environment (venv311) for PaddleOCR."

            $py311 = Get-Command py -ErrorAction SilentlyContinue
            if ($null -eq $py311) {
                Write-Host "ERROR: 'py' launcher not found. Install Python 3.11 and rerun."
                Write-Host "The app will continue with EasyOCR fallback in current venv."
            }
            else {
                $VENV311_PYTHON = ".\venv311\Scripts\python.exe"
                $venv311Valid = (Test-Path "venv311\pyvenv.cfg") -and `
                                (Test-Path $VENV311_PYTHON) -and `
                                (Test-Path "venv311\Lib\site-packages")

                if (-not $venv311Valid) {
                    if (Test-Path "venv311") {
                        Remove-Item -Recurse -Force venv311
                    }
                    py -3.11 -m venv venv311
                    Start-Sleep -Seconds 2
                }

                if (-not (Test-Path $VENV311_PYTHON)) {
                    Write-Host "ERROR: Failed to create venv311 with Python 3.11."
                    Write-Host "The app will continue with EasyOCR fallback in current venv."
                }
                else {
                    Write-Host "Installing project deps in venv311 (Paddle-strict compatible set)."
                    & $VENV311_PYTHON -m pip install --upgrade pip

                    # Build a filtered requirements file for venv311 to avoid numpy/OpenCV conflicts:
                    # - Exclude EasyOCR/OpenCV-headless track
                    # - Exclude shap (newer versions require numpy>=2)
                    # - Exclude paddleocr from base file; install pinned version separately below.
                    $filteredReq = "requirements.paddle311.txt"
                    Get-Content "requirements.txt" | Where-Object {
                        ($_ -notmatch '^\s*easyocr') -and
                        ($_ -notmatch '^\s*opencv-python') -and
                        ($_ -notmatch '^\s*shap') -and
                        ($_ -notmatch '^\s*paddleocr')
                    } | Set-Content $filteredReq

                    & $VENV311_PYTHON -m pip install -r $filteredReq
                    if ($LASTEXITCODE -ne 0) {
                        Write-Host "ERROR: requirements install failed in venv311."
                        Write-Host "Continuing with current venv and EasyOCR fallback."
                    }
                    else {
                        # Keep ABI-compatible stack for PaddleOCR on Windows.
                        # numpy 2.x can break older OpenCV/Paddle wheels.
                        Write-Host "Pinning numpy/opencv compatibility for PaddleOCR."
                        & $VENV311_PYTHON -m pip install --force-reinstall "numpy<2.0.0" "opencv-python==4.6.0.66" "opencv-contrib-python==4.6.0.66"
                        if ($LASTEXITCODE -ne 0) {
                            Write-Host "WARNING: Could not pin numpy/opencv compatibility."
                            Write-Host "Continuing, but Paddle may fail to import."
                        }

                        Write-Host "Installing PaddleOCR backend in venv311."
                        & $VENV311_PYTHON -m pip install paddleocr==2.7.3 paddlepaddle==2.6.2
                        if ($LASTEXITCODE -eq 0) {
                            # Re-apply compatibility pins because dependency resolver may upgrade them.
                            & $VENV311_PYTHON -m pip install --force-reinstall "numpy<2.0.0" "opencv-python==4.6.0.66" "opencv-contrib-python==4.6.0.66"
                            New-Item "venv311\.deps_installed" -ItemType File -Force | Out-Null
                            New-Item "venv311\.paddle_installed" -ItemType File -Force | Out-Null
                            $VENV_PYTHON = $VENV311_PYTHON
                            Write-Host "PaddleOCR installed in venv311. Using venv311 for remaining steps."
                        }
                        else {
                            Write-Host "WARNING: Paddle install still failed in venv311."
                            Write-Host "Continuing with current venv and EasyOCR fallback."
                        }
                    }
                }
            }
        }
    }
    else {
        Write-Host "Skipped PaddleOCR installation."
    }
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

    # Skip Paddle model-host connectivity check on startup (avoids delays/noise)
    $env:PADDLE_PDX_DISABLE_MODEL_SOURCE_CHECK = "True"
    # Work around Paddle oneDNN/PIR runtime issues seen on some Windows setups.
    $env:FLAGS_use_mkldnn = "0"
    $env:FLAGS_enable_pir_api = "0"
    $env:FLAGS_enable_pir_in_executor = "0"
    # Enforce strict Paddle-only OCR mode for highest consistency.
    $env:OCR_ENGINE_MODE = "paddle_only"
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
