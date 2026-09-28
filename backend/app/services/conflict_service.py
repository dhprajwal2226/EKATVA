"""
Conflict Service.
Evaluates, isolates, and manages technical conflicts between material candidates.
SIH 2026 - National Material Master Platform.
"""

from typing import Dict, Any, List, Tuple
from app.ai.technical_rules import evaluate_technical_conflicts, SEVERITY_CRITICAL, SEVERITY_MAJOR


class ConflictService:
    @staticmethod
    def analyze_conflicts(
        source_attributes: Dict[str, Any],
        target_attributes: Dict[str, Any],
    ) -> Tuple[List[Dict[str, Any]], Dict[str, str], float, bool]:
        """
        Evaluate full conflict matrix between source and target attributes.
        Returns:
            - conflicts: List of conflict records
            - attribute_matrix: Detailed comparison status per attribute
            - technical_score: Technical rule compliance score (0.0 - 1.0)
            - has_critical_conflict: Boolean indicating presence of any CRITICAL conflict
        """
        conflicts, matrix, tech_score = evaluate_technical_conflicts(source_attributes, target_attributes)
        has_critical = any(c.get("severity") == SEVERITY_CRITICAL for c in conflicts)
        return conflicts, matrix, tech_score, has_critical
