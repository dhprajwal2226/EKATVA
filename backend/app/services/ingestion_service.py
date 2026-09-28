"""
Ingestion Service.
Handles CSV/Excel file validation, asynchronous job progress tracking,
normalization, Material DNA extraction, and persistent database storage.
SIH 2026 - National Material Master Platform.
"""

import io
import csv
import os
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session
from app.models.cpse import CPSE
from app.models.material import Material
from app.models.ingestion_job import IngestionJob
from app.models.material_embedding import MaterialEmbedding
from app.services.normalization_service import NormalizationService
from app.services.material_dna_service import MaterialDNAService
from app.ai.embeddings import generate_embedding
from app.utils.validators import validate_file_metadata, validate_material_row
from app.core.config import settings


class IngestionService:
    @classmethod
    def parse_file_content(cls, filename: str, content: bytes) -> List[Dict[str, Any]]:
        """
        Parse raw bytes of CSV or XLSX into standard list of dict rows.
        """
        ext = os.path.splitext(filename)[1].lower()
        rows: List[Dict[str, Any]] = []

        if ext == ".csv":
            # Attempt UTF-8, fallback to Latin-1
            try:
                decoded = content.decode("utf-8")
            except UnicodeDecodeError:
                decoded = content.decode("latin-1")

            reader = csv.DictReader(io.StringIO(decoded))
            for r in reader:
                # Standardize dictionary keys to lowercase without whitespace
                clean_row = {k.strip().lower(): v.strip() for k, v in r.items() if k}
                rows.append(clean_row)

        elif ext in [".xlsx", ".xls"]:
            try:
                import pandas as pd
                df = pd.read_excel(io.BytesIO(content))
                # Fill NaN with empty string
                df = df.fillna("")
                # Clean column headers
                df.columns = [str(c).strip().lower() for c in df.columns]
                rows = df.to_dict(orient="records")
            except ImportError:
                raise ValueError("Excel file uploaded but 'pandas'/'openpyxl' is not installed in the environment.")

        return rows

    @classmethod
    def process_ingestion(
        cls,
        db: Session,
        job_id: str,
        filename: str,
        file_bytes: bytes,
        default_cpse_code: Optional[str] = None,
    ) -> IngestionJob:
        """
        Full ingestion pipeline:
        VALIDATE -> PARSE -> PRESERVE ORIGINAL -> NORMALIZE -> EXTRACT DNA -> STORE
        """
        job = db.query(IngestionJob).filter(IngestionJob.id == job_id).first()
        if not job:
            job = IngestionJob(id=job_id, filename=filename, status="PROCESSING")
            db.add(job)
            db.commit()

        job.status = "PROCESSING"
        db.commit()

        # Cache known CPSEs by code
        cpses = {c.code.upper(): c.id for c in db.query(CPSE).all()}

        try:
            raw_rows = cls.parse_file_content(filename, file_bytes)
        except Exception as e:
            job.status = "FAILED"
            job.errors = [{"row": 0, "field": "file", "message": f"Failed to parse file: {str(e)}"}]
            job.completed_at = datetime.now(timezone.utc)
            db.commit()
            return job

        job.total_rows = len(raw_rows)
        accepted = 0
        rejected = 0
        warnings = 0
        error_list: List[Dict[str, Any]] = []

        seen_codes_in_batch = set()

        for idx, row in enumerate(raw_rows, start=1):
            # Extract common field aliases
            mat_code = str(row.get("material_code") or row.get("code") or row.get("item_code") or "").strip()
            desc = str(row.get("description") or row.get("original_description") or row.get("item_desc") or "").strip()
            cpse_code = str(row.get("cpse") or row.get("cpse_code") or default_cpse_code or "").strip().upper()
            category = str(row.get("category") or "").strip()
            source_ref = str(row.get("source_reference") or filename).strip()

            # Row Validation
            row_data = {"material_code": mat_code, "description": desc, "cpse": cpse_code}
            is_valid, row_errs = validate_material_row(idx, row_data)

            if not is_valid:
                rejected += 1
                error_list.extend(row_errs)
                continue

            # Validate CPSE
            if not cpse_code or cpse_code not in cpses:
                rejected += 1
                error_list.append({
                    "row": idx,
                    "field": "cpse",
                    "message": f"Unknown or missing CPSE code '{cpse_code}'. Must be one of: {list(cpses.keys())}",
                })
                continue

            cpse_id = cpses[cpse_code]

            # Duplicate check within batch
            batch_key = (cpse_id, mat_code)
            if batch_key in seen_codes_in_batch:
                warnings += 1
                error_list.append({
                    "row": idx,
                    "field": "material_code",
                    "message": f"Duplicate material code '{mat_code}' within upload batch. Skipping subsequent duplicate.",
                })
                rejected += 1
                continue
            seen_codes_in_batch.add(batch_key)

            # Normalization
            norm_res = NormalizationService.process_description(desc)
            normalized_desc = norm_res["normalized_description"]

            # Save Material (preserve original_description)
            existing_material = db.query(Material).filter(
                Material.cpse_id == cpse_id,
                Material.material_code == mat_code,
            ).first()

            if existing_material:
                # Update existing record while keeping original description immutable
                existing_material.normalized_description = normalized_desc
                existing_material.category = category or existing_material.category
                existing_material.status = "ANALYZED"
                existing_material.updated_at = datetime.now(timezone.utc)
                material_rec = existing_material
            else:
                material_rec = Material(
                    cpse_id=cpse_id,
                    material_code=mat_code,
                    original_description=desc,
                    normalized_description=normalized_desc,
                    category=category or "General",
                    source_reference=source_ref,
                    status="ANALYZED",
                )
                db.add(material_rec)

            db.flush()

            # Extract and persist Material DNA
            MaterialDNAService.persist_dna(db, material_rec)

            # Generate and persist Embedding
            vec = generate_embedding(normalized_desc, material_rec.attributes.other_attributes if material_rec.attributes else None)
            if not material_rec.embedding:
                emb = MaterialEmbedding(
                    material_id=material_rec.id,
                    embedding=vec,
                    model_name=settings.EMBEDDING_MODEL,
                )
                db.add(emb)
            else:
                material_rec.embedding.embedding = vec

            accepted += 1

        db.commit()

        # Update Job Metrics
        job.processed_rows = len(raw_rows)
        job.accepted_rows = accepted
        job.rejected_rows = rejected
        job.warnings = warnings
        job.errors = error_list
        job.completed_at = datetime.now(timezone.utc)

        if rejected == 0:
            job.status = "COMPLETED"
        elif accepted > 0:
            job.status = "PARTIAL_SUCCESS"
        else:
            job.status = "FAILED"

        db.commit()
        db.refresh(job)
        return job
