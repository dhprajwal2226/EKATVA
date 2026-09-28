"""
CNMC (Common National Material Code) & Canonical Description Service.
Deterministic identity hashing, collision prevention, and CPSE mapping foundation.
SIH 2026 - National Material Master Platform.
"""

import json
import hashlib
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.models.national_material import NationalMaterial
from app.models.cpse_material_mapping import CPSEMaterialMapping
from app.models.material import Material
from app.services.material_dna_service import MaterialDNAService


class CNMCService:
    @staticmethod
    def compute_identity_hash(attributes: Dict[str, Any]) -> str:
        """Compute deterministic SHA-256 fingerprint from canonical attributes."""
        return MaterialDNAService.compute_dna_fingerprint(attributes)

    @classmethod
    def generate_or_get_cnmc(
        cls,
        db: Session,
        canonical_attributes: Dict[str, Any],
        standard_description: str,
        category: Optional[str] = None,
        status: str = "DRAFT",
    ) -> NationalMaterial:
        """
        Idempotent CNMC generator.
        If an identity hash already exists in national_materials, returns that existing record.
        Otherwise, assigns the next incremental sequential code (e.g. CNMC-000001).
        """
        identity_hash = cls.compute_identity_hash(canonical_attributes)

        existing = db.query(NationalMaterial).filter(NationalMaterial.identity_hash == identity_hash).first()
        if existing:
            return existing

        # Determine next sequence number
        max_id = db.query(func.max(NationalMaterial.id)).scalar() or 0
        next_seq = max_id + 1
        cnmc_code = f"CNMC-{next_seq:06d}"

        national_mat = NationalMaterial(
            cnmc=cnmc_code,
            standard_description=standard_description.strip(),
            category=category or canonical_attributes.get("material_type"),
            canonical_attributes=canonical_attributes,
            identity_hash=identity_hash,
            status=status,
        )
        db.add(national_mat)
        db.commit()
        db.refresh(national_mat)
        return national_mat

    @staticmethod
    def select_canonical_description(materials: List[Material]) -> Dict[str, Any]:
        """
        Evaluate candidate material records in an equivalence cluster
        and pick the strongest canonical description based on technical completeness.
        """
        if not materials:
            return {"selected_material": None, "standard_description": "", "reason": ["No materials provided"]}

        scored_candidates = []

        for mat in materials:
            score = 0.0
            reasons = []

            desc = mat.original_description or ""
            attr = mat.attributes

            # Attribute completeness
            if attr:
                filled_attrs = sum(
                    1 for k in ["material_type", "material", "grade", "diameter", "pressure", "schedule", "standard"]
                    if getattr(attr, k, None) is not None
                )
                completeness_ratio = filled_attrs / 7.0
                score += completeness_ratio * 40.0
                if completeness_ratio >= 0.70:
                    reasons.append("High technical attribute completeness")

                if attr.standard:
                    score += 25.0
                    reasons.append(f"Contains standard specification ({attr.standard})")

                if attr.grade:
                    score += 20.0
                    reasons.append(f"Explicit metallurgical grade ({attr.grade})")

                if attr.schedule or attr.pressure:
                    score += 15.0
                    reasons.append("Detailed pressure/schedule rating")

            # Length and readability bonus
            if 20 <= len(desc) <= 120:
                score += 10.0
                reasons.append("Concise and informative technical description")

            scored_candidates.append({
                "material": mat,
                "score": score,
                "reasons": reasons if reasons else ["Baseline description"],
            })

        # Select highest scored candidate
        scored_candidates.sort(key=lambda x: x["score"], reverse=True)
        winner = scored_candidates[0]

        return {
            "selected_material_id": winner["material"].id,
            "selected_material_code": winner["material"].material_code,
            "cpse_code": winner["material"].cpse.code if winner["material"].cpse else "UNKNOWN",
            "standard_description": winner["material"].normalized_description or winner["material"].original_description,
            "score": round(winner["score"], 1),
            "reason": winner["reasons"],
        }

    @staticmethod
    def map_cpse_material(
        db: Session,
        national_material_id: int,
        cpse_id: int,
        material_id: int,
        mapping_type: str = "IDENTICAL",
    ) -> CPSEMaterialMapping:
        """Link a CPSE material record to a National Material master (CNMC)."""
        existing = db.query(CPSEMaterialMapping).filter(
            CPSEMaterialMapping.national_material_id == national_material_id,
            CPSEMaterialMapping.material_id == material_id,
        ).first()

        if existing:
            existing.mapping_type = mapping_type
            db.commit()
            db.refresh(existing)
            return existing

        mapping = CPSEMaterialMapping(
            national_material_id=national_material_id,
            cpse_id=cpse_id,
            material_id=material_id,
            mapping_type=mapping_type,
        )
        db.add(mapping)
        db.commit()
        db.refresh(mapping)
        return mapping
