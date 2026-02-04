"""
Rule-Based Engine Module
Enforces clinical guideline rules for antibiotic prescribing
"""

from typing import Dict, List, Tuple
from backend.utils.guidelines import ClinicalGuidelines
from backend.utils.validators import PrescriptionValidator


class RuleEngine:
    """Rule-based engine for detecting guideline violations"""

    def __init__(self, guidelines: ClinicalGuidelines = None):
        """
        Initialize rule engine

        Args:
            guidelines: ClinicalGuidelines instance
        """
        self.guidelines = guidelines or ClinicalGuidelines()
        self.validator = PrescriptionValidator()

    def evaluate_prescription(self, prescription: Dict) -> Tuple[bool, List[Dict]]:
        """
        Evaluate a prescription against all rules

        Args:
            prescription: Prescription dictionary

        Returns:
            Tuple of (is_appropriate, violations_list)
            violations_list contains dicts with 'severity', 'rule', 'message'
        """
        violations = []

        # Extract prescription details
        diagnosis = prescription.get('diagnosis', '').lower().replace(' ', '_')
        antibiotic = prescription.get('antibiotic_prescribed', '').lower()
        dosage = prescription.get('dosage_mg', 0)
        frequency = prescription.get('frequency_per_day', 0)
        duration = prescription.get('duration_days', 0)
        patient_age = prescription.get('patient_age', 0)
        patient_weight = prescription.get('patient_weight_kg', 70)
        allergies = self.validator.parse_allergies(prescription.get('patient_allergies', 'none'))
        comorbidities = self.validator.parse_comorbidities(prescription.get('comorbidities', 'none'))

        # Rule 1: No antibiotics for viral infections
        viral_violations = self._check_viral_infection(diagnosis, antibiotic)
        violations.extend(viral_violations)

        # Rule 2: Check contraindications
        contraindication_violations = self._check_contraindications(
            antibiotic, allergies, patient_age, comorbidities
        )
        violations.extend(contraindication_violations)

        # Rule 3: Check if antibiotic is appropriate for diagnosis
        indication_violations = self._check_indication(diagnosis, antibiotic)
        violations.extend(indication_violations)

        # Rule 4: Check dosage appropriateness
        dosage_violations = self._check_dosage(
            antibiotic, dosage, frequency, patient_age, patient_weight
        )
        violations.extend(dosage_violations)

        # Rule 5: Check duration appropriateness
        duration_violations = self._check_duration(antibiotic, diagnosis, duration)
        violations.extend(duration_violations)

        # Rule 6: Check for unnecessary broad-spectrum use
        spectrum_violations = self._check_spectrum_appropriateness(diagnosis, antibiotic)
        violations.extend(spectrum_violations)

        # Rule 7: Check for reserved antibiotics
        reserved_violations = self._check_reserved_antibiotics(antibiotic, diagnosis)
        violations.extend(reserved_violations)

        # Determine if prescription is appropriate
        critical_violations = [v for v in violations if v['severity'] in ['critical', 'high']]
        is_appropriate = len(critical_violations) == 0

        return is_appropriate, violations

    def _check_viral_infection(self, diagnosis: str, antibiotic: str) -> List[Dict]:
        """Check if antibiotic prescribed for viral infection"""
        violations = []

        if self.guidelines.is_viral_infection(diagnosis):
            violations.append({
                'severity': 'critical',
                'rule': 'no_antibiotics_for_viral',
                'message': f'Antibiotics not indicated for viral infection: {diagnosis}. '
                          f'Prescribing {antibiotic} is inappropriate.',
                'recommendation': 'Consider symptomatic treatment only',
                'why_explanation': '🦠 Antibiotics only work against bacterial infections, not viruses. '
                                  'Using them for viral infections provides no benefit to the patient but '
                                  'kills beneficial bacteria in the body, allowing drug-resistant bacteria to multiply. '
                                  'This contributes directly to antimicrobial resistance (AMR), making future infections '
                                  'harder to treat for everyone.'
            })

        return violations

    def _check_contraindications(self, antibiotic: str, allergies: List[str],
                                 patient_age: int, comorbidities: List[str]) -> List[Dict]:
        """Check for contraindications"""
        violations = []

        warnings = self.guidelines.check_contraindications(
            antibiotic, allergies, patient_age, comorbidities
        )

        for warning in warnings:
            severity = 'critical' if 'CONTRAINDICATION' in warning else 'high'

            # Determine why explanation based on warning type
            if 'allerg' in warning.lower():
                why_text = '⚠️ Allergic reactions to antibiotics can range from mild rashes to life-threatening ' \
                          'anaphylaxis (severe allergic shock). Prescribing an antibiotic the patient is allergic to ' \
                          'could cause serious harm or even death. Patient safety must always come first.'
            elif 'age' in warning.lower():
                why_text = '👶 Certain antibiotics can harm developing bones, teeth, or organs in children. ' \
                          'Age restrictions exist because these medications have been proven unsafe for specific age groups. ' \
                          'Using them anyway risks permanent damage to the patient\'s development.'
            else:
                why_text = '⚕️ This antibiotic may interact dangerously with the patient\'s existing conditions or ' \
                          'medications, potentially worsening their health, causing organ damage, or reducing ' \
                          'the effectiveness of treatment.'

            violations.append({
                'severity': severity,
                'rule': 'contraindication_check',
                'message': warning,
                'recommendation': 'Choose alternative antibiotic',
                'why_explanation': why_text
            })

        return violations

    def _check_indication(self, diagnosis: str, antibiotic: str) -> List[Dict]:
        """Check if antibiotic is appropriate for the diagnosis"""
        violations = []

        # Get recommended antibiotics for diagnosis
        recommended = self.guidelines.get_recommended_antibiotics(diagnosis)

        if not recommended:
            # Diagnosis not in guidelines - cannot verify
            return violations

        # Check if antibiotics are needed at all
        if not recommended.get('requires_antibiotic', True):
            violations.append({
                'severity': 'critical',
                'rule': 'antibiotic_not_required',
                'message': f'Antibiotic not required for {diagnosis}. Reason: {recommended.get("reason", "Unknown")}',
                'recommendation': 'Avoid antibiotic prescription',
                'why_explanation': '❌ This condition does not require antibiotics at all. Prescribing them provides zero ' \
                                  'benefit to the patient while causing unnecessary side effects, killing beneficial bacteria, ' \
                                  'and contributing to the global crisis of antibiotic resistance. Every unnecessary prescription ' \
                                  'brings us closer to a post-antibiotic world where common infections become deadly.'
            })
            return violations

        # Check if prescribed antibiotic is in recommended list
        first_line = recommended.get('first_line', [])
        alternative = recommended.get('alternative', [])
        severe_cases = recommended.get('severe_cases', [])

        all_recommended = first_line + alternative + severe_cases

        if antibiotic not in [ab.lower() for ab in all_recommended]:
            violations.append({
                'severity': 'high',
                'rule': 'non_guideline_antibiotic',
                'message': f'{antibiotic} not in recommended antibiotics for {diagnosis}',
                'recommendation': f'Consider first-line options: {", ".join(first_line)}',
                'why_explanation': f'🎯 Clinical guidelines specify which antibiotics work best for each condition based on ' \
                                  f'extensive research and proven outcomes. Using {antibiotic} for {diagnosis.replace("_", " ")} ' \
                                  f'may not effectively treat the infection, leading to treatment failure, prolonged illness, ' \
                                  f'and potential complications. The recommended alternatives have been proven to work better ' \
                                  f'and reduce the risk of developing antibiotic resistance.'
            })
        elif antibiotic not in [ab.lower() for ab in first_line] and first_line:
            violations.append({
                'severity': 'medium',
                'rule': 'non_first_line_antibiotic',
                'message': f'{antibiotic} is not first-line therapy for {diagnosis}',
                'recommendation': f'Consider first-line options: {", ".join(first_line)}',
                'why_explanation': f'💊 First-line antibiotics are chosen because they are the most effective, safest, and ' \
                                  f'least likely to cause resistance for this specific condition. Using second-line or alternative ' \
                                  f'antibiotics unnecessarily can lead to more side effects, higher costs, and increased risk of ' \
                                  f'developing drug resistance. Reserve these alternatives for when first-line options fail or ' \
                                  f'cannot be used.'
            })

        return violations

    def _check_dosage(self, antibiotic: str, dosage: float, frequency: int,
                     patient_age: int, patient_weight: float) -> List[Dict]:
        """Check if dosage is within appropriate range"""
        violations = []

        dosage_info = self.guidelines.get_dosage_range(antibiotic, patient_age, patient_weight)

        if not dosage_info:
            return violations

        # Check single dose
        min_dose = dosage_info.get('min_mg', 0)
        max_dose = dosage_info.get('max_mg', float('inf'))
        recommended_freq = dosage_info.get('frequency_per_day', frequency)

        if dosage < min_dose:
            violations.append({
                'severity': 'high',
                'rule': 'underdosing',
                'message': f'Dosage ({dosage}mg) below recommended minimum ({min_dose}mg) for {antibiotic}',
                'recommendation': f'Increase dosage to {min_dose}-{max_dose}mg per dose',
                'why_explanation': '⚖️ Under-dosing antibiotics is extremely dangerous - it kills only the weakest bacteria, ' \
                                  'allowing the strongest, most resistant ones to survive and multiply. This is exactly how ' \
                                  'antibiotic-resistant "superbugs" develop. The patient\'s infection may not be cured, and ' \
                                  'it could become resistant to treatment. Always use the full recommended dose.'
            })

        if dosage > max_dose:
            violations.append({
                'severity': 'high',
                'rule': 'overdosing',
                'message': f'Dosage ({dosage}mg) exceeds recommended maximum ({max_dose}mg) for {antibiotic}',
                'recommendation': f'Reduce dosage to {min_dose}-{max_dose}mg per dose',
                'why_explanation': '☠️ Overdosing antibiotics can cause serious side effects including organ damage (kidney, ' \
                                  'liver), severe allergic reactions, and toxicity. The maximum dose exists to protect patients ' \
                                  'from harm. Higher doses don\'t make the antibiotic work better - they just increase the risk ' \
                                  'of dangerous complications.'
            })

        # Check frequency
        if frequency != recommended_freq:
            violations.append({
                'severity': 'medium',
                'rule': 'incorrect_frequency',
                'message': f'Frequency ({frequency}x/day) differs from recommended ({recommended_freq}x/day)',
                'recommendation': f'Adjust frequency to {recommended_freq} times per day',
                'why_explanation': '⏰ Taking antibiotics at the correct frequency maintains steady drug levels in the body ' \
                                  'needed to kill bacteria. Wrong frequency means drug levels drop too low between doses ' \
                                  '(allowing bacteria to survive) or spike too high (causing side effects). This can lead to ' \
                                  'treatment failure and resistance development.'
            })

        # Check pediatric weight-based dosing
        if patient_age < 18 and 'mg_per_kg_per_day' in dosage_info:
            recommended_daily_dose = dosage_info['mg_per_kg_per_day'] * patient_weight
            actual_daily_dose = dosage * frequency

            # Allow 20% variance
            if actual_daily_dose < recommended_daily_dose * 0.8:
                violations.append({
                    'severity': 'high',
                    'rule': 'pediatric_underdosing',
                    'message': f'Total daily dose ({actual_daily_dose:.0f}mg) below recommended '
                              f'({recommended_daily_dose:.0f}mg = {dosage_info["mg_per_kg_per_day"]}mg/kg/day)',
                    'recommendation': f'Increase to approximately {recommended_daily_dose:.0f}mg total daily dose',
                    'why_explanation': '👶 Children need precise weight-based dosing because their bodies process drugs ' \
                                      'differently than adults. Under-dosing won\'t cure the infection and creates resistant ' \
                                      'bacteria. Children are especially vulnerable - getting the dose right is critical for ' \
                                      'their safety and recovery.'
                })
            elif actual_daily_dose > recommended_daily_dose * 1.2:
                violations.append({
                    'severity': 'high',
                    'rule': 'pediatric_overdosing',
                    'message': f'Total daily dose ({actual_daily_dose:.0f}mg) exceeds recommended '
                              f'({recommended_daily_dose:.0f}mg = {dosage_info["mg_per_kg_per_day"]}mg/kg/day)',
                    'recommendation': f'Reduce to approximately {recommended_daily_dose:.0f}mg total daily dose',
                    'why_explanation': '👶 Overdosing children is extremely dangerous - their smaller bodies and developing ' \
                                      'organs (kidneys, liver) can\'t handle excess medication. This can cause organ damage, ' \
                                      'severe side effects, or toxicity. Children need precise dosing to stay safe.'
                })

        return violations

    def _check_duration(self, antibiotic: str, diagnosis: str, duration: int) -> List[Dict]:
        """Check if duration is appropriate"""
        violations = []

        dosage_info = self.guidelines.get_dosage_range(antibiotic, 30)  # Use adult default

        if not dosage_info:
            # Check general duration limits
            if duration > 21:
                violations.append({
                    'severity': 'high',
                    'rule': 'excessive_duration',
                    'message': f'Treatment duration ({duration} days) is excessive',
                    'recommendation': 'Review need for prolonged antibiotic therapy',
                    'why_explanation': '⏱️ Prolonged antibiotic use (over 3 weeks) significantly increases the risk of resistance, ' \
                                      'side effects, and secondary infections. Extended treatment should only be used for specific ' \
                                      'serious conditions that clinically require it. Always re-evaluate the need for continued therapy.'
                })
            return violations

        min_duration = dosage_info.get('min_duration_days', 0)
        max_duration = dosage_info.get('max_duration_days', 14)

        if duration < min_duration:
            violations.append({
                'severity': 'high',
                'rule': 'insufficient_duration',
                'message': f'Duration ({duration} days) below recommended minimum ({min_duration} days)',
                'recommendation': f'Extend treatment to {min_duration}-{max_duration} days',
                'why_explanation': '📅 Stopping antibiotics too early is a major cause of antibiotic resistance. It\'s like ' \
                                  'only partially cleaning a wound - you kill most bacteria but the strongest survive and come ' \
                                  'back stronger. The infection may relapse, become resistant, and be much harder to treat. ' \
                                  'Always complete the full course.'
            })

        if duration > max_duration:
            violations.append({
                'severity': 'high',
                'rule': 'excessive_duration',
                'message': f'Duration ({duration} days) exceeds recommended maximum ({max_duration} days)',
                'recommendation': f'Reduce duration to {min_duration}-{max_duration} days',
                'why_explanation': '⏱️ Taking antibiotics longer than needed unnecessarily exposes bacteria to the drug, ' \
                                  'giving them more opportunity to develop resistance. It also increases side effects, kills ' \
                                  'beneficial bacteria, and may cause secondary infections like C. difficile. Use antibiotics ' \
                                  'only as long as clinically necessary.'
            })

        return violations

    def _check_spectrum_appropriateness(self, diagnosis: str, antibiotic: str) -> List[Dict]:
        """Check for unnecessary broad-spectrum antibiotic use"""
        violations = []

        if not self.guidelines.is_broad_spectrum(antibiotic):
            return violations

        # Simple infections that don't require broad-spectrum
        simple_infections = [
            'streptococcal_pharyngitis', 'acute_otitis_media',
            'simple_uti', 'uncomplicated_skin_infection'
        ]

        if any(simple in diagnosis for simple in simple_infections):
            violations.append({
                'severity': 'medium',
                'rule': 'unnecessary_broad_spectrum',
                'message': f'Broad-spectrum antibiotic ({antibiotic}) used for simple infection ({diagnosis})',
                'recommendation': 'Consider narrow-spectrum alternative to preserve antibiotic effectiveness',
                'why_explanation': '🎯 Broad-spectrum antibiotics are like using a sledgehammer when you need a scalpel - they ' \
                                  'kill many types of bacteria, not just the ones causing the infection. This unnecessarily ' \
                                  'wipes out beneficial bacteria and creates more opportunities for resistance to develop. ' \
                                  'Save these powerful drugs for complex infections; use narrow-spectrum antibiotics for simple cases.'
            })

        return violations

    def _check_reserved_antibiotics(self, antibiotic: str, diagnosis: str) -> List[Dict]:
        """Check if reserved antibiotics used appropriately"""
        violations = []

        reserved_antibiotics = ['vancomycin', 'linezolid', 'daptomycin', 'tigecycline']

        if antibiotic.lower() in reserved_antibiotics:
            ab_info = self.guidelines.get_antibiotic_info(antibiotic)
            if ab_info:
                indications = ab_info.get('indications', [])
                if diagnosis not in indications:
                    violations.append({
                        'severity': 'high',
                        'rule': 'reserved_antibiotic_misuse',
                        'message': f'{antibiotic} is a reserved antibiotic and should only be used for specific indications',
                        'recommendation': f'Reserve for: {", ".join(indications)}',
                        'why_explanation': '🚨 Reserved antibiotics are our "last line of defense" against the most dangerous, ' \
                                          'drug-resistant infections. Using them unnecessarily for common infections accelerates ' \
                                          'resistance, meaning when we truly need them (for life-threatening multi-drug resistant ' \
                                          'infections), they might not work. We\'re running out of backup options - protect these ' \
                                          'precious resources.'
                    })

        return violations

    def get_violation_summary(self, violations: List[Dict]) -> Dict:
        """
        Get summary of violations by severity

        Args:
            violations: List of violation dictionaries

        Returns:
            Summary dictionary with counts by severity
        """
        summary = {
            'total': len(violations),
            'critical': 0,
            'high': 0,
            'medium': 0,
            'low': 0
        }

        for violation in violations:
            severity = violation.get('severity', 'medium')
            if severity in summary:
                summary[severity] += 1

        return summary
