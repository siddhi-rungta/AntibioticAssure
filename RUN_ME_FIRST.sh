#!/bin/bash

# ========================================
# AUTOMATED SETUP AND RUN SCRIPT
# ========================================
# This script will:
# 1. Setup virtual environment
# 2. Install dependencies
# 3. Train the model
# 4. Run the demo
# 5. Start the web server
# ========================================

# Use AUTO_MODE=true environment variable for non-interactive run
AUTO_MODE=${AUTO_MODE:-true}
START_SERVER=${START_SERVER:-true}

echo ""
echo "╔════════════════════════════════════════════════════════════╗"
echo "║   AI-Driven Antibiotic Prescription Monitoring System     ║"
echo "║              Automated Setup & Run Script                  ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""

# Check if Python is installed
if command -v python3 &> /dev/null; then
    PYTHON=python3
elif command -v python &> /dev/null; then
    PYTHON=python
else
    echo "❌ Python 3 not found!"
    echo "Please install Python 3.9 or higher first."
    exit 1
fi

PYTHON_VERSION=$($PYTHON -c 'import sys; print("{}.{}.{}".format(sys.version_info[0], sys.version_info[1], sys.version_info[2]))')
echo "✓ Python found: $PYTHON $PYTHON_VERSION"
echo ""
# Step 1: Virtual Environment
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Step 1/5: Setting up virtual environment..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    $PYTHON -m venv venv
    echo "✓ Virtual environment created"
else
    echo "✓ Virtual environment already exists"
fi

# Activate virtual environment
echo "Activating virtual environment..."
if [ -f "venv/bin/activate" ]; then
    source venv/bin/activate
elif [ -f "venv/Scripts/activate" ]; then
    source venv/Scripts/activate
else
    echo "❌ Could not find venv activation script"
    exit 1
fi

echo "✓ Virtual environment activated"
echo ""

# Step 2: Install Dependencies
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Step 2/5: Installing dependencies..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

echo "Upgrading pip..."
pip install --upgrade pip --quiet

echo "Installing required packages (this may take a minute)..."
pip install -r requirements.txt --quiet

# Add optional but recommended utilities
pip install pytesseract easyocr opencv-python --quiet

echo "✓ All dependencies installed"
echo ""

# Ensure Tesseract engine is available
if ! command -v tesseract &> /dev/null; then
    echo "⚠️  Tesseract OCR binary not found. Please install it for image OCR:"
    echo "    - Linux: sudo apt install tesseract-ocr (or yum/dnf)"
    echo "    - macOS: brew install tesseract"
    echo "    - Windows: install from https://github.com/tesseract-ocr/tesseract/releases"
    echo "  Continuing without Tesseract (EasyOCR may still work if installed)."
    echo ""
else
    echo "✓ Tesseract binary found: $(tesseract --version | head -n 1)"
    echo ""
fi

# Step 3: Train Model
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Step 3/5: Training machine learning model..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

if [ ! -f "models/trained_model.pkl" ]; then
    echo "Training model with sample data..."
    $PYTHON scripts/train_model.py
    echo "✓ Model trained and saved"
else
    echo "✓ Trained model already exists"
    if [ "$AUTO_MODE" != "true" ]; then
        read -p "Do you want to retrain? (y/N) " -n 1 -r
        echo
    fi
    if [ "$AUTO_MODE" != "true" ] && [[ $REPLY =~ ^[Yy]$ ]]; then
        $PYTHON scripts/train_model.py
    elif [ "$AUTO_MODE" = "true" ]; then
        echo "AUTO_MODE=true -> skipping retrain"
    fi
fi
echo ""

# Step 4: Run Demo
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Step 4/5: Running demonstration..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

echo "This will show 4 prescription evaluation scenarios."
echo ""
if [ "$AUTO_MODE" != "true" ]; then
    read -p "Press Enter to continue..."
    echo ""
fi

$PYTHON scripts/demo.py

echo ""
echo "✓ Demo completed"
echo ""

# Step 5: Ask about web server
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Step 5/5: Web Server"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

echo ""
echo "Would you like to start the web interface?"
echo "This will open a beautiful dashboard at http://localhost:5000"
echo ""
if [ "$AUTO_MODE" != "true" ]; then
    read -p "Start web server? (Y/n) " -n 1 -r
    echo ""
    START_SERVER_RESPONSE=$REPLY
else
    START_SERVER_RESPONSE=Y
fi

if [ "$START_SERVER" = "true" ] && [[ ! "$START_SERVER_RESPONSE" =~ ^[Nn]$ ]]; then
    echo ""
    echo "╔════════════════════════════════════════════════════════════╗"
    echo "║                  Starting Web Server...                    ║"
    echo "╚════════════════════════════════════════════════════════════╝"
    echo ""
    echo "🌐 Server will start on: http://localhost:5000"
    echo ""
    echo "To stop the server: Press Ctrl+C"
    echo ""
    echo "Opening in 3 seconds..."
    sleep 3

    # Try to open browser
    if command -v open &> /dev/null; then
        # macOS
        (sleep 5 && open http://localhost:5000) &
    elif command -v xdg-open &> /dev/null; then
        # Linux
        (sleep 5 && xdg-open http://localhost:5000) &
    fi

    # Start server
    FLASK_APP=backend.app $PYTHON -m flask run --host=0.0.0.0 --port=5000
else
    echo ""
    echo "╔════════════════════════════════════════════════════════════╗"
    echo "║                     Setup Complete!                        ║"
    echo "╚════════════════════════════════════════════════════════════╝"
    echo ""
    echo "Your system is ready to use!"
    echo ""
    echo "To start the web server later, run:"
    echo "  source venv/bin/activate"
    echo "  FLASK_APP=backend.app $PYTHON -m flask run --host=0.0.0.0 --port=5000"
    echo ""
    echo "Then open http://localhost:5000 in your browser"
    echo ""
    echo "Or run the demo again:"
    echo "  source venv/bin/activate"
    echo "  $PYTHON scripts/demo.py"
    echo ""
fi
