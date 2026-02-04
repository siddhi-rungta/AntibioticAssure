"""
Explainability Module
Provides human-readable explanations for AI decisions
"""

from typing import Dict, List
from backend.models.rule_engine import RuleEngine
from backend.models.ml_model import AntibioticMLModel


class ExplainabilityEngine:
    """Generates clinician-friendly explanations for alerts"""

    def __init__(self):
        """Initialize explainability engine"""
        self.severity_descriptions = {
            'critical': 'CRITICAL - Immediate attention required',
            'high': 'HIGH PRIORITY - Should be addressed',
            'medium': 'MODERATE - Review recommended',
            'low': 'MINOR - Consider for optimization'
        }

    def generate_explanation(self, prescription: Dict, rule_violations: List[Dict],
                            ml_prediction: Dict = None) -> Dict:
        """
        Generate comprehensive explanation for prescription evaluation

        Args:
            prescription: Prescription dictionary
            rule_violations: List of rule violations from rule engine
            ml_prediction: ML model prediction dictionary (optional)

        Returns:
            Dictionary with structured explanation
        """
        explanation = {
            'prescription_summary': self._create_prescription_summary(prescription),
            'overall_assessment': self._create_overall_assessment(rule_violations, ml_prediction),
            'violations': self._format_violations(rule_violations),
            'recommendations': self._generate_recommendations(rule_violations),
            'confidence_score': self._calculate_confidence(rule_violations, ml_prediction)
        }

        if ml_prediction:
            explanation['ml_insights'] = self._format_ml_insights(ml_prediction)

        return explanation

    def _create_prescription_summary(self, prescription: Dict) -> Dict:
        """Create a concise summary of the prescription"""
        return {
            'patient_age': f"{prescription.get('patient_age')} years",
            'diagnosis': prescription.get('diagnosis', 'Unknown').replace('_', ' ').title(),
            'antibiotic': prescription.get('antibiotic_prescribed', 'Unknown').title(),
            'dosage': f"{prescription.get('dosage_mg')}mg {prescription.get('frequency_per_day')}x/day",
            'duration': f"{prescription.get('duration_days')} days",
            'allergies': prescription.get('patient_allergies', 'None'),
            'comorbidities': prescription.get('comorbidities', 'None')
        }

    def _create_overall_assessment(self, violations: List[Dict], ml_prediction: Dict = None) -> Dict:
        """Create overall assessment of prescription appropriateness"""
        critical_count = sum(1 for v in violations if v['severity'] == 'critical')
        high_count = sum(1 for v in violations if v['severity'] == 'high')
        medium_count = sum(1 for v in violations if v['severity'] == 'medium')

        # Determine status
        if critical_count > 0:
            status = 'INAPPROPRIATE'
            risk_level = 'CRITICAL'
            message = f"Found {critical_count} critical issue(s) that make this prescription inappropriate."
        elif high_count > 0:
            status = 'NEEDS REVIEW'
            risk_level = 'HIGH'
            message = f"Found {high_count} high-priority issue(s) that require attention."
        elif medium_count > 0:
            status = 'SUBOPTIMAL'
            risk_level = 'MODERATE'
            message = f"Found {medium_count} moderate issue(s). Consider optimization."
        else:
            status = 'APPROPRIATE'
            risk_level = 'LOW'
            message = "No significant issues detected. Prescription aligns with guidelines."

        assessment = {
            'status': status,
            'risk_level': risk_level,
            'message': message,
            'total_violations': len(violations),
            'violations_by_severity': {
                'critical': critical_count,
                'high': high_count,
                'medium': medium_count
            }
        }

        # Add ML confidence if available
        if ml_prediction:
            assessment['ml_agreement'] = self._check_ml_agreement(violations, ml_prediction)

        return assessment

    def _format_violations(self, violations: List[Dict]) -> List[Dict]:
        """Format violations for display"""
        formatted = []

        for i, violation in enumerate(violations, 1):
            formatted.append({
                'id': i,
                'severity': violation['severity'],
                'severity_label': self.severity_descriptions.get(violation['severity'], 'UNKNOWN'),
                'rule': violation['rule'].replace('_', ' ').title(),
                'message': violation['message'],
                'recommendation': violation.get('recommendation', 'Consult clinical guidelines'),
                'why_explanation': violation.get('why_explanation', ''),  # Add why explanation
                'icon': self._get_severity_icon(violation['severity'])
            })

        # Sort by severity
        severity_order = {'critical': 0, 'high': 1, 'medium': 2, 'low': 3}
        formatted.sort(key=lambda x: severity_order.get(x['severity'], 4))

        return formatted

    def _generate_recommendations(self, violations: List[Dict]) -> List[str]:
        """Generate actionable recommendations"""
        recommendations = []

        # Extract unique recommendations from violations
        for violation in violations:
            rec = violation.get('recommendation')
            if rec and rec not in recommendations:
                recommendations.append(rec)

        # Add general recommendations based on violation types
        violation_rules = [v['rule'] for v in violations]

        if 'no_antibiotics_for_viral' in violation_rules:
            recommendations.insert(0, "⚠️ PRIORITY: Discontinue antibiotic - viral infection detected")

        if 'contraindication_check' in violation_rules:
            recommendations.insert(0, "⚠️ PRIORITY: Review contraindications and consider alternative antibiotic")

        if not recommendations:
            recommendations.append("✅ Prescription aligns with clinical guidelines")

        return recommendations[:5]  # Limit to top 5

    def _calculate_confidence(self, violations: List[Dict], ml_prediction: Dict = None) -> Dict:
        """Calculate confidence in the assessment"""
        # Rule-based confidence
        rule_confidence = 1.0
        if violations:
            # Higher confidence when clear violations exist
            critical_count = sum(1 for v in violations if v['severity'] == 'critical')
            if critical_count > 0:
                rule_confidence = 0.95
            else:
                rule_confidence = 0.85

        confidence = {
            'rule_based_confidence': rule_confidence,
            'explanation': 'High confidence based on clear guideline violations' if violations else 'High confidence - no violations detected'
        }

        # Add ML confidence if available
        if ml_prediction and 'confidence' in ml_prediction:
            confidence['ml_confidence'] = ml_prediction['confidence']
            confidence['combined_confidence'] = (rule_confidence + ml_prediction['confidence']) / 2

        return confidence

    def _format_ml_insights(self, ml_prediction: Dict) -> Dict:
        """Format ML model insights"""
        insights = {
            'prediction': 'Appropriate' if ml_prediction.get('is_appropriate') else 'Inappropriate',
            'confidence': f"{ml_prediction.get('confidence', 0) * 100:.1f}%",
            'probability_appropriate': f"{ml_prediction.get('probability_appropriate', 0) * 100:.1f}%",
            'interpretation': self._interpret_ml_prediction(ml_prediction)
        }

        # Add feature importance if available
        if 'top_influential_features' in ml_prediction:
            insights['key_factors'] = [
                f"{f['feature'].replace('_', ' ').title()}: {f['importance']:.3f}"
                for f in ml_prediction['top_influential_features'][:3]
            ]

        return insights

    def _interpret_ml_prediction(self, ml_prediction: Dict) -> str:
        """Interpret ML prediction in plain language"""
        confidence = ml_prediction.get('confidence', 0)
        is_appropriate = ml_prediction.get('is_appropriate', True)

        if is_appropriate:
            if confidence > 0.8:
                return "ML model strongly agrees this prescription is appropriate"
            elif confidence > 0.6:
                return "ML model suggests prescription is likely appropriate"
            else:
                return "ML model has low confidence; manual review recommended"
        else:
            if confidence > 0.8:
                return "ML model strongly flags this as potentially inappropriate"
            elif confidence > 0.6:
                return "ML model suggests this prescription may be inappropriate"
            else:
                return "ML model has low confidence; manual review recommended"

    def _check_ml_agreement(self, violations: List[Dict], ml_prediction: Dict) -> str:
        """Check if ML model agrees with rule-based assessment"""
        has_critical_violations = any(v['severity'] == 'critical' for v in violations)
        ml_inappropriate = not ml_prediction.get('is_appropriate', True)

        if has_critical_violations and ml_inappropriate:
            return "✅ ML model confirms rule-based assessment"
        elif has_critical_violations and not ml_inappropriate:
            return "⚠️ ML model disagrees - manual review recommended"
        elif not has_critical_violations and not ml_inappropriate:
            return "⚠️ ML model detects potential issues not caught by rules"
        else:
            return "✅ Both systems agree prescription is appropriate"

    def _get_severity_icon(self, severity: str) -> str:
        """Get icon for severity level"""
        icons = {
            'critical': '🔴',
            'high': '🟠',
            'medium': '🟡',
            'low': '🟢'
        }
        return icons.get(severity, '⚪')

    def generate_alert_text(self, explanation: Dict) -> str:
        """
        Generate concise alert text for quick review

        Args:
            explanation: Full explanation dictionary

        Returns:
            Concise alert text string
        """
        assessment = explanation['overall_assessment']
        status = assessment['status']
        risk_level = assessment['risk_level']

        if status == 'APPROPRIATE':
            return "✅ Prescription appropriate - no issues detected"

        violations = explanation['violations']
        top_issue = violations[0] if violations else None

        if top_issue:
            alert = f"{top_issue['icon']} {risk_level}: {top_issue['message']}"
        else:
            alert = f"⚠️ {status} - Review required"

        return alert[:200]  # Limit length

    def format_for_display(self, explanation: Dict, format_type: str = 'detailed') -> str:
        """
        Format explanation for different display contexts

        Args:
            explanation: Explanation dictionary
            format_type: 'brief', 'detailed', or 'clinical'

        Returns:
            Formatted string
        """
        if format_type == 'brief':
            return self._format_brief(explanation)
        elif format_type == 'clinical':
            return self._format_clinical(explanation)
        else:
            return self._format_detailed(explanation)

    def _format_brief(self, explanation: Dict) -> str:
        """Brief format for notifications"""
        assessment = explanation['overall_assessment']
        return f"{assessment['status']}: {assessment['message']}"

    def _format_detailed(self, explanation: Dict) -> str:
        """Detailed format for full reports"""
        output = []
        output.append("=" * 60)
        output.append("PRESCRIPTION EVALUATION REPORT")
        output.append("=" * 60)

        # Summary
        summary = explanation['prescription_summary']
        output.append(f"\nPatient: {summary['patient_age']}")
        output.append(f"Diagnosis: {summary['diagnosis']}")
        output.append(f"Antibiotic: {summary['antibiotic']}")
        output.append(f"Dosage: {summary['dosage']} for {summary['duration']}")

        # Assessment
        assessment = explanation['overall_assessment']
        output.append(f"\n{'=' * 60}")
        output.append(f"ASSESSMENT: {assessment['status']} (Risk: {assessment['risk_level']})")
        output.append(f"{'=' * 60}")
        output.append(f"\n{assessment['message']}")

        # Violations
        if explanation['violations']:
            output.append(f"\n{'=' * 60}")
            output.append("ISSUES DETECTED:")
            output.append(f"{'=' * 60}")
            for v in explanation['violations']:
                output.append(f"\n{v['icon']} {v['severity_label']}")
                output.append(f"   Issue: {v['message']}")
                if v.get('why_explanation'):
                    output.append(f"   Why This Matters: {v['why_explanation']}")
                output.append(f"   Recommendation: {v['recommendation']}")

        # Recommendations
        output.append(f"\n{'=' * 60}")
        output.append("RECOMMENDATIONS:")
        output.append(f"{'=' * 60}")
        for i, rec in enumerate(explanation['recommendations'], 1):
            output.append(f"{i}. {rec}")

        return "\n".join(output)

    def _format_clinical(self, explanation: Dict) -> str:
        """Clinical format for healthcare professionals"""
        output = []
        assessment = explanation['overall_assessment']

        output.append(f"Clinical Decision Support Alert - {assessment['risk_level']} Priority")
        output.append(f"\nStatus: {assessment['status']}")
        output.append(f"Assessment: {assessment['message']}")

        if explanation['violations']:
            output.append("\nClinical Concerns:")
            for v in explanation['violations'][:3]:  # Top 3 only
                output.append(f"  • {v['message']}")
                output.append(f"    → {v['recommendation']}")

        return "\n".join(output)
