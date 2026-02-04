#!/bin/bash
################################################################################
# Official Synthea Data Downloader
# Downloads authentic synthetic patient data from MITRE Corporation
# Source: https://synthetichealth.github.io/synthea/
################################################################################

set -e  # Exit on error

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}================================================${NC}"
echo -e "${BLUE}  Official Synthea Data Downloader (MITRE)    ${NC}"
echo -e "${BLUE}================================================${NC}"
echo ""

# Configuration
PROJECT_DIR="/Users/srungta/Downloads/finalyear"
DATA_DIR="$PROJECT_DIR/data"
DOWNLOAD_DIR="$DATA_DIR/synthea_downloads"
EXTRACT_DIR="$DATA_DIR/synthea_large"
OUTPUT_DIR="$DATA_DIR/synthea_processed_large"

# Official Synthea datasets
echo -e "${YELLOW}Select Official Synthea Dataset:${NC}"
echo ""
echo "1) COVID-19 Dataset (10K patients, MITRE, ~150-250 prescriptions)"
echo "   URL: https://synthetichealth.github.io/synthea/"
echo ""
echo "2) SyntheticMass (1M patients, Mass. DPH, ~8,000-15,000 prescriptions)"
echo "   URL: https://synthea.mitre.org/downloads"
echo ""
echo "3) Custom Generation (1K patients, ~50-100 prescriptions)"
echo "   Requires Java + Synthea JAR"
echo ""
read -p "Enter choice (1-3) [Recommended: 1]: " CHOICE
CHOICE=${CHOICE:-1}

case $CHOICE in
    1)
        DATASET_URL="https://storage.googleapis.com/synthea-public/synthea_sample_data_csv_apr2020.zip"
        DATASET_NAME="COVID-19 Sample (10K patients)"
        CITATION="MITRE Corporation. Synthea™ COVID-19 Sample Data (2020)"
        ;;
    2)
        DATASET_URL="https://synthea.mitre.org/downloads"
        echo ""
        echo -e "${YELLOW}Note: SyntheticMass requires manual download${NC}"
        echo "1. Visit: https://synthea.mitre.org/downloads"
        echo "2. Download: 'SyntheticMass' ZIP file (~1.2GB)"
        echo "3. Extract to: $EXTRACT_DIR"
        echo "4. Run: python scripts/import_synthea.py --input $EXTRACT_DIR/csv --output $OUTPUT_DIR"
        echo ""
        exit 0
        ;;
    3)
        echo ""
        echo "To generate custom data, you need:"
        echo "1. Java 11+ installed"
        echo "2. Download Synthea JAR:"
        echo "   wget https://github.com/synthetichealth/synthea/releases/download/master-branch-latest/synthea-with-dependencies.jar"
        echo "3. Generate data:"
        echo "   java -jar synthea-with-dependencies.jar -p 1000"
        echo ""
        exit 0
        ;;
    *)
        echo "Invalid choice"
        exit 1
        ;;
esac

# Create directories
mkdir -p "$DOWNLOAD_DIR"
mkdir -p "$EXTRACT_DIR"
mkdir -p "$OUTPUT_DIR"

# Download
echo ""
echo -e "${GREEN}Step 1: Downloading $DATASET_NAME${NC}"
echo "Source: $DATASET_URL"
echo "Citation: $CITATION"
echo ""

DOWNLOAD_FILE="$DOWNLOAD_DIR/synthea_official.zip"

if [ -f "$DOWNLOAD_FILE" ]; then
    echo "File exists. Skipping download."
else
    echo "Downloading... (may take a few minutes)"
    curl -L --progress-bar -o "$DOWNLOAD_FILE" "$DATASET_URL"
    echo -e "${GREEN}✓ Downloaded successfully${NC}"
fi

# Extract
echo ""
echo -e "${GREEN}Step 2: Extracting Dataset${NC}"

# Clear existing extraction
rm -rf "$EXTRACT_DIR"
mkdir -p "$EXTRACT_DIR"

echo "Extracting ZIP file..."
unzip -q "$DOWNLOAD_FILE" -d "$EXTRACT_DIR"
echo -e "${GREEN}✓ Extracted${NC}"

# Find CSV directory
CSV_DIR=$(find "$EXTRACT_DIR" -name "patients.csv" -type f -exec dirname {} \; | head -1)

if [ -z "$CSV_DIR" ]; then
    echo "Error: Could not find CSV files"
    exit 1
fi

echo ""
echo -e "${GREEN}Step 3: Verifying Files${NC}"
echo "CSV Directory: $CSV_DIR"
echo "  Patients: $(tail -n +2 "$CSV_DIR/patients.csv" | wc -l | xargs) records"
echo "  Medications: $(tail -n +2 "$CSV_DIR/medications.csv" | wc -l | xargs) records"
echo "  Conditions: $(tail -n +2 "$CSV_DIR/conditions.csv" | wc -l | xargs) records"

# Import
echo ""
echo -e "${GREEN}Step 4: Processing Prescriptions${NC}"
echo ""

cd "$PROJECT_DIR"

# Activate venv if exists
if [ -d "venv/bin/activate" ]; then
    source venv/bin/activate
fi

# Run import script
python3 scripts/import_synthea.py --input "$CSV_DIR" --output "$OUTPUT_DIR"

# Save citation info
cat > "$OUTPUT_DIR/CITATION.txt" << EOF
Dataset Information
===================

Source: $DATASET_NAME
Provider: MITRE Corporation / Synthea™
URL: https://synthetichealth.github.io/synthea/
Downloaded: $(date)

Citation:
$CITATION

About Synthea:
Synthea™ is an open-source synthetic patient generator developed by
MITRE Corporation. It creates realistic (but not real) patient data
and associated health records covering every aspect of healthcare.

Funding: U.S. Department of Health and Human Services (HHS)

For academic use:
Please cite: Walone, Jason, et al. "Synthea: An approach, method,
and software mechanism for generating synthetic patients and the
synthetic electronic health care record." Journal of the American
Medical Informatics Association 25.3 (2018): 230-238.

DOI: 10.1093/jamia/ocx079
EOF

echo ""
echo -e "${GREEN}================================================${NC}"
echo -e "${GREEN}          Download Complete!                   ${NC}"
echo -e "${GREEN}================================================${NC}"
echo ""
echo "✅ Processed prescriptions: $OUTPUT_DIR/synthea_prescriptions.csv"
echo "📄 Citation info: $OUTPUT_DIR/CITATION.txt"
echo ""
echo "Next steps:"
echo "  1. Label data: python scripts/label_data.py"
echo "  2. Train model: python scripts/train_model.py"
echo ""
echo "For your report, cite:"
echo "  $CITATION"
echo ""
