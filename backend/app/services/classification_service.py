"""
Classification & Explainability Service.
Translates hybrid scores and technical conflicts into human-readable,
actionable engineering recommendations.
SIH 2026 - National Material Master Platform.
"""

from typing import Dict, Any, List
from app.core.config import settings
from app.ai.technical_rules import SEVERITY_CRITICAL, SEVERITY_MAJOR, STATUS_MATCH


class ClassificationService:
    @staticmethod
    def classify_and_explain(
        final_score: float,
        semantic_score: float,
        fuzzy_score: float,
        attribute_score: float,
        technical_score: float,
        conflicts: List[Dict[str, Any]],
        attribute_matrix: Dict[str, str],
        source_attr: Dict[str, Any],
        target_attr: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Produce deterministic classification and explainable matching dossier.
        Strictly enforces: CRITICAL CONFLICT > SIMILARITY SCORE.
        """
        has_critical = any(c.get("severity") == SEVERITY_CRITICAL for c in conflicts)
        has_major = any(c.get("severity") == SEVERITY_MAJOR for c in conflicts)

        # Build Explainability Lists
        why_matched: List[str] = []
        what_matched: List[str] = []
        what_differed: List[str] = []

        for attr, status in attribute_matrix.items():
            s_val = source_attr.get(attr)
            t_val = target_attr.get(attr)
            if status == STATUS_MATCH and s_val is not None:
                what_matched.append(f"{attr.replace('_', ' ').title()}: {s_val}")
                why_matched.append(f"Identical {attr.replace('_', ' ')} ({s_val})")
            elif status in ("MAJOR_DIFFERENCE", "CRITICAL_CONFLICT") and (s_val or t_val):
                what_differed.append(f"{attr.replace('_', ' ').title()}: {s_val} vs {t_val}")

        if semantic_score >= 0.85:
            why_matched.append(f"High semantic vector similarity ({semantic_score:.2f})")
        if fuzzy_score >= 0.85:
            why_matched.append(f"High lexical token match ({fuzzy_score:.2f})")

        # Check for unknown / missing critical attributes when comparing candidate matches
        unknown_critical_attrs = [
            attr for attr in ("material_type", "material", "grade", "pressure")
            if attribute_matrix.get(attr) == "UNKNOWN" and (source_attr.get(attr) or target_attr.get(attr))
        ]
        has_ambiguous_critical = len(unknown_critical_attrs) > 0

        # Core Decision Logic
        if final_score < settings.REVIEW_THRESHOLD:
            # Insufficient similarity or completely unrelated equipment
            classification = "DIFFERENT"
            review_required = False
            recommendation = "NO_ACTION"
            confidence = round(final_score, 3)
        elif has_critical:
            # MANDATORY RULE: Never auto-merge or classify as IDENTICAL if critical conflict exists!
            classification = "REVIEW_REQUIRED"
            review_required = True
            recommendation = "DO_NOT_AUTO_MERGE"
            confidence = round(final_score, 3)
        elif has_ambiguous_critical:
            # Missing critical specification on one side requires human review
            classification = "REVIEW_REQUIRED"
            review_required = True
            recommendation = "MANUAL_REVIEW_REQUIRED"
            confidence = round(final_score, 3)
        elif has_major:
            classification = "FUNCTIONALLY_EQUIVALENT" if final_score >= settings.FUNCTIONAL_EQUIVALENT_THRESHOLD else "REVIEW_REQUIRED"
            review_required = True
            recommendation = "REVIEW_FOR_SUBSTITUTION"
            confidence = round(final_score, 3)
        elif final_score >= settings.IDENTICAL_THRESHOLD and technical_score >= 0.95:
            classification = "IDENTICAL"
            review_required = False
            recommendation = "AUTO_MERGE_CANDIDATE"
            confidence = round(final_score, 3)
        elif final_score >= settings.NEAR_DUPLICATE_THRESHOLD:
            classification = "NEAR_DUPLICATE"
            review_required = True
            recommendation = "REVIEW_FOR_MERGE"
            confidence = round(final_score, 3)
        elif final_score >= settings.FUNCTIONAL_EQUIVALENT_THRESHOLD:
            classification = "FUNCTIONALLY_EQUIVALENT"
            review_required = True
            recommendation = "REVIEW_FOR_EQUIVALENCE"
            confidence = round(final_score, 3)
        else:
            classification = "REVIEW_REQUIRED"
            review_required = True
            recommendation = "MANUAL_REVIEW_REQUIRED"
            confidence = round(final_score, 3)

        explanation = {
            "why_matched": why_matched,
            "what_matched": what_matched,
            "what_differed": what_differed,
            "technical_conflicts": conflicts,
            "confidence": confidence,
            "recommendation": recommendation,
            "review_required": review_required,
        }

        return {
            "classification": classification,
            "review_required": review_required,
            "recommendation": recommendation,
            "confidence": confidence,
            "explanation": explanation,
        }
