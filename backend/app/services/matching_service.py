"""
Hybrid Matching Service.
Coordinates Vector Semantic Search, Fuzzy Matching, Attribute Matrix,
Technical Conflict Engine, and Explanation Generation.
SIH 2026 - National Material Master Platform.
"""

from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session
from app.core.config import settings
from app.models.material import Material
from app.models.material_attribute import MaterialAttribute
from app.models.material_embedding import MaterialEmbedding
from app.models.material_match import MaterialMatch
from app.models.material_conflict import MaterialConflict
from app.ai.embeddings import generate_embedding, cosine_similarity
from app.ai.fuzzy_matching import compute_fuzzy_similarity
from app.ai.candidate_generation import generate_candidate_pairs
from app.services.conflict_service import ConflictService
from app.services.classification_service import ClassificationService
from app.services.material_dna_service import MaterialDNAService


class MatchingService:
    @staticmethod
    def calculate_attribute_similarity(
        attr_a: Dict[str, Any],
        attr_b: Dict[str, Any],
    ) -> float:
        """
        Compute structured attribute overlap score.
        Calculates ratio of agreeing technical attributes over evaluated attributes.
        """
        eval_keys = [
            "material_type",
            "material",
            "grade",
            "diameter",
            "length",
            "pressure",
            "schedule",
            "standard",
        ]
        agreed = 0.0
        total = 0.0

        for k in eval_keys:
            v1 = attr_a.get(k)
            v2 = attr_b.get(k)
            if v1 is not None and v2 is not None:
                total += 1.0
                if k in ("diameter", "length"):
                    # Numeric tolerance check
                    try:
                        f1, f2 = float(v1), float(v2)
                        if max(f1, f2) > 0 and (abs(f1 - f2) / max(f1, f2)) <= 0.02:
                            agreed += 1.0
                    except (ValueError, TypeError):
                        pass
                else:
                    if str(v1).strip().upper() == str(v2).strip().upper():
                        agreed += 1.0

        if total == 0:
            return 0.50
        return round(agreed / total, 4)

    @classmethod
    def compare_pair(
        cls,
        source_desc: str,
        target_desc: str,
        source_attr: Optional[Dict[str, Any]] = None,
        target_attr: Optional[Dict[str, Any]] = None,
        source_vec: Optional[List[float]] = None,
        target_vec: Optional[List[float]] = None,
    ) -> Dict[str, Any]:
        """
        Pure hybrid evaluation of two material items.
        Can run standalone (without DB dependencies) for direct unit testing and API calls.
        """
        s_attr = source_attr or MaterialDNAService.extract_dna(source_desc)
        t_attr = target_attr or MaterialDNAService.extract_dna(target_desc)

        s_vec = source_vec or generate_embedding(source_desc, s_attr)
        t_vec = target_vec or generate_embedding(target_desc, t_attr)

        # 1. Semantic Similarity
        semantic_score = cosine_similarity(s_vec, t_vec)

        # 2. Fuzzy Similarity
        fuzzy_result = compute_fuzzy_similarity(source_desc, target_desc)
        fuzzy_score = fuzzy_result["composite_fuzzy"]

        # 3. Attribute Similarity
        attribute_score = cls.calculate_attribute_similarity(s_attr, t_attr)

        # 4. Technical Rule Validation & Conflicts
        conflicts, matrix, tech_score, has_critical = ConflictService.analyze_conflicts(s_attr, t_attr)

        # 5. Configurable Hybrid Score Formula
        final_score = round(
            (settings.SEMANTIC_WEIGHT * semantic_score)
            + (settings.FUZZY_WEIGHT * fuzzy_score)
            + (settings.ATTRIBUTE_WEIGHT * attribute_score)
            + (settings.TECHNICAL_WEIGHT * tech_score),
            4,
        )

        # 6. Classification & Explainable Matching
        classification_result = ClassificationService.classify_and_explain(
            final_score=final_score,
            semantic_score=semantic_score,
            fuzzy_score=fuzzy_score,
            attribute_score=attribute_score,
            technical_score=tech_score,
            conflicts=conflicts,
            attribute_matrix=matrix,
            source_attr=s_attr,
            target_attr=t_attr,
        )

        return {
            "scores": {
                "semantic": semantic_score,
                "fuzzy": fuzzy_score,
                "attribute": attribute_score,
                "technical": tech_score,
                "final": final_score,
            },
            "classification": classification_result["classification"],
            "review_required": classification_result["review_required"],
            "recommendation": classification_result["recommendation"],
            "confidence": classification_result["confidence"],
            "attribute_matrix": matrix,
            "technical_conflicts": conflicts,
            "explanation": classification_result["explanation"],
            "source_attributes": s_attr,
            "target_attributes": t_attr,
        }

    @classmethod
    def run_pipeline(
        cls,
        db: Session,
        limit_materials: Optional[int] = None,
    ) -> Dict[str, Any]:
        """
        Execute candidate generation and hybrid matching across all ingested materials in DB.
        Saves matches and conflicts with initial status PENDING_REVIEW.
        """
        query = db.query(Material)
        if limit_materials:
            query = query.limit(limit_materials)
        all_materials = query.all()

        # Ensure attributes and embeddings are populated for all records
        for mat in all_materials:
            if not mat.attributes:
                MaterialDNAService.persist_dna(db, mat)
            if not mat.embedding:
                vec = generate_embedding(mat.normalized_description or mat.original_description)
                emb = MaterialEmbedding(
                    material_id=mat.id,
                    embedding=vec,
                    model_name=settings.EMBEDDING_MODEL,
                )
                db.add(emb)
        db.commit()

        # Re-fetch materials with relationships loaded
        materials = db.query(Material).all()

        total_pairs_evaluated = 0
        matches_created = 0
        conflicts_created = 0
        classifications_tally: Dict[str, int] = {}

        # Run candidate blocking & matching
        for src in materials:
            candidates = generate_candidate_pairs(src, materials, top_k=settings.CANDIDATE_TOP_K)
            for tgt, prelim_score in candidates:
                # To prevent duplicate bidirectional matches (A-B and B-A), only compare when src.id < tgt.id
                if src.id >= tgt.id:
                    continue

                total_pairs_evaluated += 1

                # Check if match already exists
                existing_match = db.query(MaterialMatch).filter(
                    MaterialMatch.source_material_id == src.id,
                    MaterialMatch.target_material_id == tgt.id,
                ).first()

                src_attr_dict = {
                    "material_type": src.attributes.material_type if src.attributes else None,
                    "material": src.attributes.material if src.attributes else None,
                    "grade": src.attributes.grade if src.attributes else None,
                    "diameter": src.attributes.diameter if src.attributes else None,
                    "length": src.attributes.length if src.attributes else None,
                    "pressure": src.attributes.pressure if src.attributes else None,
                    "schedule": src.attributes.schedule if src.attributes else None,
                    "standard": src.attributes.standard if src.attributes else None,
                }
                tgt_attr_dict = {
                    "material_type": tgt.attributes.material_type if tgt.attributes else None,
                    "material": tgt.attributes.material if tgt.attributes else None,
                    "grade": tgt.attributes.grade if tgt.attributes else None,
                    "diameter": tgt.attributes.diameter if tgt.attributes else None,
                    "length": tgt.attributes.length if tgt.attributes else None,
                    "pressure": tgt.attributes.pressure if tgt.attributes else None,
                    "schedule": tgt.attributes.schedule if tgt.attributes else None,
                    "standard": tgt.attributes.standard if tgt.attributes else None,
                }

                for _d, _m in ((src_attr_dict, src), (tgt_attr_dict, tgt)):
                    _x = (_m.attributes.other_attributes or {}) if _m.attributes else {}
                    _d.update({k: v for k, v in _x.items() if k not in ("confidence_scores", "overall_confidence", "fingerprint_hash")})

                src_vec = src.embedding.embedding if src.embedding else None
                tgt_vec = tgt.embedding.embedding if tgt.embedding else None

                res = cls.compare_pair(
                    source_desc=src.original_description,
                    target_desc=tgt.original_description,
                    source_attr=src_attr_dict,
                    target_attr=tgt_attr_dict,
                    source_vec=src_vec,
                    target_vec=tgt_vec,
                )

                if existing_match:
                    match_record = existing_match
                else:
                    match_record = MaterialMatch(
                        source_material_id=src.id,
                        target_material_id=tgt.id,
                    )
                    db.add(match_record)

                match_record.semantic_score = res["scores"]["semantic"]
                match_record.fuzzy_score = res["scores"]["fuzzy"]
                match_record.attribute_score = res["scores"]["attribute"]
                match_record.technical_score = res["scores"]["technical"]
                match_record.final_score = res["scores"]["final"]
                match_record.classification = res["classification"]
                match_record.review_required = res["review_required"]
                match_record.explanation = res["explanation"]
                match_record.status = "PENDING_REVIEW"

                db.flush()

                # Clear old conflicts for this match if any
                db.query(MaterialConflict).filter(MaterialConflict.match_id == match_record.id).delete()

                # Add new conflicts
                for c in res["technical_conflicts"]:
                    conflict_record = MaterialConflict(
                        match_id=match_record.id,
                        attribute=c["attribute"],
                        source_value=c.get("source_value"),
                        target_value=c.get("target_value"),
                        severity=c["severity"],
                        reason=c["reason"],
                    )
                    db.add(conflict_record)
                    conflicts_created += 1

                matches_created += 1
                classifications_tally[res["classification"]] = classifications_tally.get(res["classification"], 0) + 1

        db.commit()

        return {
            "total_pairs_evaluated": total_pairs_evaluated,
            "matches_recorded": matches_created,
            "conflicts_detected": conflicts_created,
            "classifications_tally": classifications_tally,
        }
