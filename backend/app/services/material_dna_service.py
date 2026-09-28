"""
Material DNA Service.
Extracts technical fingerprints, computes attribute confidences, and hashes canonical identities.
SIH 2026 - National Material Master Platform.
"""

import json
import hashlib
from typing import Dict, Any, Optional
from sqlalchemy.orm import Session
from app.ai.attribute_extraction import extract_attributes
from app.utils.text import normalize_description
from app.models.material import Material
from app.models.material_attribute import MaterialAttribute


class MaterialDNAService:
    @staticmethod
    def extract_dna(raw_description: str) -> Dict[str, Any]:
        """Extract structured Material DNA attributes from description text."""
        norm_desc = normalize_description(raw_description)
        dna = extract_attributes(raw_description)
        dna["normalized_description"] = norm_desc
        dna["fingerprint_hash"] = MaterialDNAService.compute_dna_fingerprint(dna)
        return dna

    @staticmethod
    def compute_dna_fingerprint(attributes: Dict[str, Any]) -> str:
        """
        Generate deterministic SHA-256 fingerprint for canonical technical attributes.
        Ignores non-technical cosmetic description differences.
        """
        canonical_dict = {
            "type": (attributes.get("material_type") or "").strip().upper(),
            "material": (attributes.get("material") or "").strip().upper(),
            "grade": (attributes.get("grade") or "").strip().upper(),
            "diameter": round(float(attributes["diameter"]), 1) if attributes.get("diameter") is not None else None,
            "length": round(float(attributes["length"]), 1) if attributes.get("length") is not None else None,
            "pressure": (attributes.get("pressure") or "").strip().upper(),
            "schedule": (attributes.get("schedule") or "").strip().upper(),
            "form": (attributes.get("form") or "").strip().upper(),
            "standard": (attributes.get("standard") or "").strip().upper(),
        }
        serialized = json.dumps(canonical_dict, sort_keys=True)
        return hashlib.sha256(serialized.encode("utf-8")).hexdigest()

    @staticmethod
    def persist_dna(db: Session, material: Material) -> MaterialAttribute:
        """Extract attributes and store or update MaterialAttribute in database."""
        dna = extract_attributes(material.original_description)

        attr = db.query(MaterialAttribute).filter(MaterialAttribute.material_id == material.id).first()
        if not attr:
            attr = MaterialAttribute(material_id=material.id)
            db.add(attr)

        attr.material_type = dna.get("material_type")
        attr.material = dna.get("material")
        attr.grade = dna.get("grade")
        attr.size = dna.get("size")
        attr.diameter = dna.get("diameter")
        attr.length = dna.get("length")
        attr.width = dna.get("width")
        attr.height = dna.get("height")
        attr.thickness = dna.get("thickness")
        attr.pressure = dna.get("pressure")
        attr.schedule = dna.get("schedule")
        attr.form = dna.get("form")
        attr.standard = dna.get("standard")
        attr.application = dna.get("application")
        attr.manufacturer = dna.get("manufacturer")
        attr.other_attributes = {
            "confidence_scores": dna.get("confidence_scores", {}),
            "overall_confidence": dna.get("overall_confidence", 0.5),
            "fingerprint_hash": MaterialDNAService.compute_dna_fingerprint(dna),
        }

        db.commit()
        db.refresh(attr)
        return attr
