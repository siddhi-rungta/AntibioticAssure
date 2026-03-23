// API Base URL - dynamically determine the host
const API_BASE_URL = `${window.location.protocol}//${window.location.host}/api`;

// Sample prescription data
const SAMPLE_DATA = {
    prescription_id: 'P001',
    patient_age: 45,
    patient_gender: 'male',
    patient_weight_kg: 70,
    diagnosis: 'community_acquired_pneumonia',
    antibiotic_prescribed: 'amoxicillin',
    dosage_mg: 500,
    frequency_per_day: 3,
    duration_days: 7,
    patient_allergies: 'none',
    comorbidities: 'diabetes'
};

// Initialize app
document.addEventListener('DOMContentLoaded', function() {
    // Load sample data button
    document.getElementById('loadSampleBtn').addEventListener('click', loadSampleData);

    // Prescription form submission
    document.getElementById('prescriptionForm').addEventListener('submit', handlePrescriptionSubmit);

    // Load statistics button
    document.getElementById('loadStatsBtn').addEventListener('click', loadStatistics);

    // Check server health on load
    checkServerHealth();

    // Auto-load guidelines on page load so users see supported antibiotics first
    loadGuidelines();
});

// Check server health
async function checkServerHealth() {
    try {
        const response = await fetch(`${API_BASE_URL}/health`);
        const data = await response.json();

        if (data.status === 'healthy') {
            console.log('✅ Server is healthy and ready');
        }
    } catch (error) {
        console.error('Server health check failed:', error);
        showNotification('Unable to connect to server. Please ensure Flask app is running.', 'danger');
    }
}

// Load sample data into form
function loadSampleData() {
    document.getElementById('prescription_id').value = SAMPLE_DATA.prescription_id;
    document.getElementById('patient_age').value = SAMPLE_DATA.patient_age;
    document.getElementById('patient_gender').value = SAMPLE_DATA.patient_gender;
    document.getElementById('patient_weight_kg').value = SAMPLE_DATA.patient_weight_kg;
    document.getElementById('diagnosis').value = SAMPLE_DATA.diagnosis;
    document.getElementById('antibiotic_prescribed').value = SAMPLE_DATA.antibiotic_prescribed;
    document.getElementById('dosage_mg').value = SAMPLE_DATA.dosage_mg;
    document.getElementById('frequency_per_day').value = SAMPLE_DATA.frequency_per_day;
    document.getElementById('duration_days').value = SAMPLE_DATA.duration_days;
    document.getElementById('patient_allergies').value = SAMPLE_DATA.patient_allergies;
    document.getElementById('comorbidities').value = SAMPLE_DATA.comorbidities;

    showNotification('Sample data loaded successfully', 'info');
}

// Handle prescription form submission
async function handlePrescriptionSubmit(event) {
    event.preventDefault();

    // Auto-generate prescription ID if empty
    let prescriptionId = document.getElementById('prescription_id').value;
    if (!prescriptionId || prescriptionId.trim() === '') {
        prescriptionId = 'RX' + Date.now(); // e.g., RX1738645123456
        document.getElementById('prescription_id').value = prescriptionId;
    }

    // Collect form data
    const prescription = {
        prescription_id: prescriptionId,
        patient_age: parseInt(document.getElementById('patient_age').value),
        patient_gender: document.getElementById('patient_gender').value || 'unknown',
        patient_weight_kg: parseFloat(document.getElementById('patient_weight_kg').value) || 70,
        diagnosis: document.getElementById('diagnosis').value,
        antibiotic_prescribed: document.getElementById('antibiotic_prescribed').value,
        dosage_mg: parseInt(document.getElementById('dosage_mg').value),
        frequency_per_day: parseInt(document.getElementById('frequency_per_day').value),
        duration_days: parseInt(document.getElementById('duration_days').value),
        patient_allergies: document.getElementById('patient_allergies').value || 'none',
        comorbidities: document.getElementById('comorbidities').value || 'none'
    };

    // Show loading
    showLoading('resultsContainer');
    document.getElementById('results').style.display = 'block';

    try {
        const response = await fetch(`${API_BASE_URL}/evaluate`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(prescription)
        });

        const data = await response.json();

        if (data.success) {
            displayResults(data);
            showNotification('Prescription evaluated successfully', 'success');
        } else {
            showNotification(`Error: ${data.error || data.errors.join(', ')}`, 'danger');
        }
    } catch (error) {
        console.error('Evaluation failed:', error);
        showNotification('Failed to evaluate prescription. Please check server connection.', 'danger');
    }
}

// Display evaluation results
function displayResults(data) {
    const container = document.getElementById('resultsContainer');
    const explanation = data.explanation;
    const assessment = explanation.overall_assessment;

    // Get alert class
    let alertClass = 'alert-low';
    if (assessment.risk_level === 'CRITICAL') alertClass = 'alert-critical';
    else if (assessment.risk_level === 'HIGH') alertClass = 'alert-high';
    else if (assessment.risk_level === 'MODERATE') alertClass = 'alert-moderate';

    let html = `
        <div class="fade-in">
            <!-- Alert Summary -->
            <div class="alert alert-result ${alertClass}">
                <h4 class="alert-heading">
                    ${getSeverityIcon(assessment.risk_level)} ${assessment.status}
                </h4>
                <p class="mb-0">${assessment.message}</p>
            </div>

            <!-- Prescription Summary -->
            <div class="prescription-summary">
                <h4><i class="bi bi-file-medical"></i> Prescription Summary</h4>
                <div class="row">
                    <div class="col-md-6">
                        <div class="prescription-detail">
                            <strong>Patient Age:</strong> ${explanation.prescription_summary.patient_age}
                        </div>
                        <div class="prescription-detail">
                            <strong>Patient Gender:</strong> ${explanation.prescription_summary.patient_gender || 'Not specified'}
                        </div>
                        <div class="prescription-detail">
                            <strong>Diagnosis:</strong> ${explanation.prescription_summary.diagnosis}
                        </div>
                        <div class="prescription-detail">
                            <strong>Antibiotic:</strong> ${explanation.prescription_summary.antibiotic}
                        </div>
                    </div>
                    <div class="col-md-6">
                        <div class="prescription-detail">
                            <strong>Dosage:</strong> ${explanation.prescription_summary.dosage}
                        </div>
                        <div class="prescription-detail">
                            <strong>Duration:</strong> ${explanation.prescription_summary.duration}
                        </div>
                        <div class="prescription-detail">
                            <strong>Allergies:</strong> ${explanation.prescription_summary.allergies}
                        </div>
                    </div>
                </div>
            </div>

            <!-- Violations -->
            ${explanation.violations.length > 0 ? `
                <div class="card mb-3">
                    <div class="card-header bg-danger text-white">
                        <h5 class="mb-0"><i class="bi bi-exclamation-triangle"></i> Issues Detected (${explanation.violations.length})</h5>
                    </div>
                    <div class="card-body">
                        ${explanation.violations.map(v => `
                            <div class="card violation-card violation-${v.severity} mb-2">
                                <div class="card-body">
                                    <h6 class="card-title">
                                        <span class="severity-icon">${v.icon}</span>
                                        ${v.severity_label}
                                    </h6>
                                    <p class="card-text mb-2">${v.message}</p>
                                    ${v.why_explanation ? `
                                        <div class="alert alert-warning mb-2" style="background-color: #fff3cd; border-left: 4px solid #ffc107;">
                                            <strong>📚 Why This Matters:</strong>
                                            <p class="mb-0 mt-1" style="font-size: 0.95rem;">${v.why_explanation}</p>
                                        </div>
                                    ` : ''}
                                    <div class="alert alert-info mb-0">
                                        <strong>Recommendation:</strong> ${v.recommendation}
                                    </div>
                                </div>
                            </div>
                        `).join('')}
                    </div>
                </div>
            ` : `
                <div class="alert alert-success">
                    <h5><i class="bi bi-check-circle"></i> No Issues Detected</h5>
                    <p class="mb-0">This prescription aligns with clinical guidelines.</p>
                </div>
            `}

            <!-- Recommendations -->
            <div class="card mb-3">
                <div class="card-header bg-info text-white">
                    <h5 class="mb-0"><i class="bi bi-lightbulb"></i> Recommendations</h5>
                </div>
                <div class="card-body">
                    <ul class="recommendations-list">
                        ${explanation.recommendations.map(rec => `
                            <li>${rec}</li>
                        `).join('')}
                    </ul>
                </div>
            </div>

            <!-- ML Insights -->
            ${explanation.ml_insights ? `
                <div class="card mb-3">
                    <div class="card-header bg-primary text-white">
                        <h5 class="mb-0"><i class="bi bi-cpu"></i> Machine Learning Insights</h5>
                    </div>
                    <div class="card-body">
                        <div class="row">
                            <div class="col-md-6">
                                <p><strong>Prediction:</strong> ${explanation.ml_insights.prediction}</p>
                                <p><strong>Confidence:</strong> ${explanation.ml_insights.confidence}</p>
                            </div>
                            <div class="col-md-6">
                                <p><strong>Interpretation:</strong> ${explanation.ml_insights.interpretation}</p>
                                ${assessment.ml_agreement ? `<p><strong>Agreement:</strong> ${assessment.ml_agreement}</p>` : ''}
                            </div>
                        </div>
                    </div>
                </div>
            ` : ''}

            <!-- Confidence Score -->
            <div class="card">
                <div class="card-header bg-secondary text-white">
                    <h5 class="mb-0"><i class="bi bi-speedometer"></i> Confidence Score</h5>
                </div>
                <div class="card-body">
                    <p>${explanation.confidence_score.explanation}</p>
                    <div class="confidence-bar">
                        <div class="confidence-fill ${getConfidenceClass(explanation.confidence_score.rule_based_confidence)}"
                             style="width: ${explanation.confidence_score.rule_based_confidence * 100}%">
                        </div>
                    </div>
                    <p class="mt-2 text-muted">Rule-based confidence: ${(explanation.confidence_score.rule_based_confidence * 100).toFixed(1)}%</p>
                </div>
            </div>
        </div>
    `;

    container.innerHTML = html;

    // Scroll to results
    document.getElementById('results').scrollIntoView({ behavior: 'smooth' });
}

// Load statistics
async function loadStatistics() {
    const container = document.getElementById('statisticsContainer');
    showLoading('statisticsContainer');

    try {
        const response = await fetch(`${API_BASE_URL}/statistics`);
        const data = await response.json();

        if (data.success) {
            const stats = data.statistics;
            container.innerHTML = `
                <div class="row fade-in">
                    <div class="col-md-3">
                        <div class="stat-card">
                            <h3>${stats.total_prescriptions}</h3>
                            <p>Total Prescriptions</p>
                        </div>
                    </div>
                    <div class="col-md-3">
                        <div class="stat-card" style="background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);">
                            <h3>${stats.appropriate}</h3>
                            <p>Appropriate</p>
                        </div>
                    </div>
                    <div class="col-md-3">
                        <div class="stat-card" style="background: linear-gradient(135deg, #eb3349 0%, #f45c43 100%);">
                            <h3>${stats.inappropriate}</h3>
                            <p>Inappropriate</p>
                        </div>
                    </div>
                    <div class="col-md-3">
                        <div class="stat-card" style="background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);">
                            <h3>${stats.appropriateness_rate.toFixed(1)}%</h3>
                            <p>Compliance Rate</p>
                        </div>
                    </div>
                </div>
                <div class="row mt-4">
                    <div class="col-md-12">
                        <div class="card">
                            <div class="card-body text-center">
                                <h5><i class="bi bi-capsule"></i> Antibiotics Monitored</h5>
                                <h2 class="text-primary">${stats.antibiotics_monitored}</h2>
                                <p class="text-muted mt-2">Clinical guidelines active and enforced</p>
                            </div>
                        </div>
                    </div>
                </div>
            `;
        } else {
            container.innerHTML = '<div class="alert alert-danger">Failed to load statistics</div>';
        }
    } catch (error) {
        console.error('Failed to load statistics:', error);
        container.innerHTML = '<div class="alert alert-danger">Failed to load statistics. Please check server connection.</div>';
    }
}

// Load guidelines
async function loadGuidelines() {
    const container = document.getElementById('guidelinesContainer');
    const countElement = document.getElementById('antibioticCount');

    try {
        const response = await fetch(`${API_BASE_URL}/guidelines`);
        const data = await response.json();

        if (data.success) {
            const antibiotics = data.antibiotics;

            // Update count
            if (countElement) {
                countElement.textContent = antibiotics.length;
            }

            // Show compact badge list
            container.innerHTML = `
                <div class="d-flex flex-wrap gap-2 align-items-center">
                    ${antibiotics.map(ab => `
                        <span class="badge bg-primary px-3 py-2" style="font-size: 0.85rem; text-transform: capitalize;">
                            ${ab}
                        </span>
                    `).join('')}
                    <small class="text-muted ms-2">
                        <i class="bi bi-info-circle"></i> Only these antibiotics can be evaluated
                    </small>
                </div>
            `;
        } else {
            container.innerHTML = '<small class="text-danger">Failed to load</small>';
        }
    } catch (error) {
        console.error('Failed to load guidelines:', error);
        container.innerHTML = '<small class="text-warning">Server not connected</small>';
    }
}

// Helper: Show loading spinner
function showLoading(containerId) {
    const container = document.getElementById(containerId);
    container.innerHTML = `
        <div class="spinner-container">
            <div class="spinner-border text-primary spinner-border-custom" role="status">
                <span class="visually-hidden">Loading...</span>
            </div>
        </div>
    `;
}

// Helper: Show notification
function showNotification(message, type = 'info') {
    // Create toast or alert (simplified version)
    console.log(`[${type.toUpperCase()}] ${message}`);
}

// Helper: Get severity icon
function getSeverityIcon(level) {
    const icons = {
        'CRITICAL': '🔴',
        'HIGH': '🟠',
        'MODERATE': '🟡',
        'LOW': '🟢'
    };
    return icons[level] || '⚪';
}

// Helper: Get confidence class
function getConfidenceClass(confidence) {
    if (confidence >= 0.8) return 'confidence-high';
    if (confidence >= 0.6) return 'confidence-medium';
    return 'confidence-low';
}
