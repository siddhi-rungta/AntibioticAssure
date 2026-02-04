#!/bin/bash

# ========================================
# AUTOMATED SETUP AND RUN SCRIPT
# ========================================
# This script will:
# 1. Setup virtual environment
# 2. Install dependencies
# 3. Train the model
# 4. Run the demo
# 5. Ask if you want to start the web server
# ========================================

echo ""
echo "╔════════════════════════════════════════════════════════════╗"
echo "║   AI-Driven Antibiotic Prescription Monitoring System     ║"
echo "║              Automated Setup & Run Script                  ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 not found!"
    echo "Please install Python 3.9 or higher first."
    exit 1
fi

echo "✓ Python found: $(python3 --version)"
echo ""

# Step 1: Virtual Environment
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Step 1/5: Setting up virtual environment..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
    echo "✓ Virtual environment created"
else
    echo "✓ Virtual environment already exists"
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate
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

echo "✓ All dependencies installed"
echo ""

# Step 3: Train Model
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Step 3/5: Training machine learning model..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

if [ ! -f "models/trained_model.pkl" ]; then
    echo "Training model with sample data..."
    python scripts/train_model.py
    echo "✓ Model trained and saved"
else
    echo "✓ Trained model already exists"
    read -p "Do you want to retrain? (y/N) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        python scripts/train_model.py
    fi
fi
echo ""

# Step 4: Run Demo
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Step 4/5: Running demonstration..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

echo "This will show 4 prescription evaluation scenarios."
echo ""
read -p "Press Enter to continue..."
echo ""

python scripts/demo.py

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
read -p "Start web server? (Y/n) " -n 1 -r
echo ""

if [[ ! $REPLY =~ ^[Nn]$ ]]; then
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
    FLASK_APP=backend.app python3 -m flask run --host=0.0.0.0 --port=5000
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
    echo "  FLASK_APP=backend.app python3 -m flask run --host=0.0.0.0 --port=5000"
    echo ""
    echo "Then open http://localhost:5000 in your browser"
    echo ""
    echo "Or run the demo again:"
    echo "  source venv/bin/activate"
    echo "  python scripts/demo.py"
    echo ""
fi
