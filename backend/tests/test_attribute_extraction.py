"""
Tests for Material DNA & Structured Technical Attribute Extraction.
SIH 2026 - National Material Master Platform.
"""

import pytest
from app.ai.attribute_extraction import extract_attributes
from app.services.material_dna_service import MaterialDNAService


def test_extract_pipe_attributes():
    """Verify DNA extraction from complex pipe description."""
    desc = "CS SEAMLESS PIPE 10 IN SCH 40 ASTM A106"
    dna = extract_attributes(desc)

    assert dna["material_type"] == "Pipe"
    assert dna["material"] == "Carbon Steel"
    assert dna["grade"] == "A106"
    assert dna["diameter"] == 254.0
    assert dna["schedule"] == "40"
    assert dna["form"] == "Seamless"
    assert dna["standard"] == "ASTM A106"
    assert dna["confidence_scores"]["diameter"] >= 0.90
    assert dna["confidence_scores"]["grade"] >= 0.90


def test_extract_bolt_attributes():
    """Verify DNA extraction from fastener with metric dimensions."""
    desc = "SS HEX BOLT M16 X 50 SS304 ASTM A193"
    dna = extract_attributes(desc)

    assert dna["material_type"] == "Fastener"
    assert dna["material"] == "Stainless Steel"
    assert dna["grade"] == "SS304"
    assert dna["diameter"] == 16.0
    assert dna["length"] == 50.0
    assert dna["form"] == "Hexagonal"
    assert dna["standard"] == "ASTM A193"


def test_extract_valve_attributes():
    """Verify DNA extraction from valve with pressure class."""
    desc = "CS GATE VALVE 6 INCH 300# WCB"
    dna = extract_attributes(desc)

    assert dna["material_type"] == "Valve"
    assert dna["material"] == "Carbon Steel"
    assert dna["grade"] == "WCB"
    assert dna["diameter"] == 152.4  # 6 * 25.4
    assert dna["pressure"] == "300#"


def test_dna_fingerprint_stability():
    """Verify deterministic SHA-256 fingerprint produces identical hash for equivalent specs."""
    desc1 = "CS SEAMLESS PIPE 10 IN SCH 40 ASTM A106"
    desc2 = "CARBON STEEL PIPE 10 INCH SCHEDULE 40 ASTM A106 SEAMLESS"

    dna1 = extract_attributes(desc1)
    dna2 = extract_attributes(desc2)

    hash1 = MaterialDNAService.compute_dna_fingerprint(dna1)
    hash2 = MaterialDNAService.compute_dna_fingerprint(dna2)

    assert hash1 == hash2, "Equivalent technical attributes must produce identical SHA-256 fingerprint!"
