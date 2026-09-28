"""
Tests for CNMC Generation, Canonical Selection, and CPSE Mapping.
SIH 2026 - National Material Master Platform.
"""

import pytest
from app.services.cnmc_service import CNMCService
from app.models.material import Material
from app.models.cpse import CPSE
from app.services.material_dna_service import MaterialDNAService


def test_cnmc_idempotent_generation(db_session):
    """Verify CNMC generation is deterministic and returns existing code for identical identity hash."""
    canonical_attrs = {
        "material_type": "Pipe",
        "material": "Carbon Steel",
        "grade": "A106",
        "diameter": 254.0,
        "schedule": "40",
    }

    # First creation
    mat1 = CNMCService.generate_or_get_cnmc(
        db=db_session,
        canonical_attributes=canonical_attrs,
        standard_description="CS SEAMLESS PIPE 10 IN SCH 40 ASTM A106",
    )
    assert mat1.cnmc.startswith("CNMC-")
    first_code = mat1.cnmc

    # Second call with same attributes
    mat2 = CNMCService.generate_or_get_cnmc(
        db=db_session,
        canonical_attributes=canonical_attrs,
        standard_description="CARBON STEEL PIPE 10 INCH SCHEDULE 40",
    )

    # Must return identical CNMC record
    assert mat2.id == mat1.id
    assert mat2.cnmc == first_code


def test_canonical_description_selection(db_session):
    """Verify algorithm selects most complete description containing standard and grade."""
    cpse = db_session.query(CPSE).first()

    m1 = Material(
        cpse_id=cpse.id,
        material_code="MAT-SHORT",
        original_description="CS PIPE 10 INCH",
        status="ANALYZED",
    )
    m2 = Material(
        cpse_id=cpse.id,
        material_code="MAT-COMPLETE",
        original_description="CS SEAMLESS PIPE 10 IN SCH 40 ASTM A106",
        status="ANALYZED",
    )
    db_session.add_all([m1, m2])
    db_session.commit()

    MaterialDNAService.persist_dna(db_session, m1)
    MaterialDNAService.persist_dna(db_session, m2)

    selection = CNMCService.select_canonical_description([m1, m2])
    assert selection["selected_material_id"] == m2.id
    assert "MAT-COMPLETE" == selection["selected_material_code"]
    assert len(selection["reason"]) > 0


def test_cpse_material_mapping(db_session):
    """Verify linking a CPSE material to a National Material."""
    cpse = db_session.query(CPSE).first()
    mat = Material(
        cpse_id=cpse.id,
        material_code="IOCL-TEST-99",
        original_description="TEST MATERIAL",
    )
    db_session.add(mat)
    db_session.commit()

    nat_mat = CNMCService.generate_or_get_cnmc(
        db=db_session,
        canonical_attributes={"type": "Test"},
        standard_description="TEST STANDARD",
    )

    mapping = CNMCService.map_cpse_material(
        db=db_session,
        national_material_id=nat_mat.id,
        cpse_id=cpse.id,
        material_id=mat.id,
        mapping_type="IDENTICAL",
    )

    assert mapping.id is not None
    assert mapping.national_material_id == nat_mat.id
    assert mapping.material_id == mat.id
