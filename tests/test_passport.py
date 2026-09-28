from app.models.mock_models import NationalMaterial, Inventory, Demand

def test_passport_shortage(client, db_session):
    # TEST 1: Shortage
    m = NationalMaterial(id="CNMC-SHORTAGE", canonical_description="Test", category="Test")
    db_session.add(m)
    db_session.add(Inventory(cnmc_id="CNMC-SHORTAGE", total_quantity=11500, reserved_quantity=0, location="Loc1"))
    db_session.add(Demand(cnmc_id="CNMC-SHORTAGE", demand_type="CURRENT", quantity=33000))
    db_session.commit()

    response = client.get("/api/v1/passport/CNMC-SHORTAGE")
    assert response.status_code == 200
    data = response.json()
    assert data["intelligence"]["signal"] == "SHORTAGE_SIGNAL"
    assert data["intelligence"]["potential_gap"] == 21500

def test_passport_surplus(client, db_session):
    # TEST 2: Surplus
    m = NationalMaterial(id="CNMC-SURPLUS", canonical_description="Test", category="Test")
    db_session.add(m)
    db_session.add(Inventory(cnmc_id="CNMC-SURPLUS", total_quantity=10000, reserved_quantity=0, location="Loc1"))
    db_session.add(Demand(cnmc_id="CNMC-SURPLUS", demand_type="CURRENT", quantity=2500))
    db_session.commit()

    response = client.get("/api/v1/passport/CNMC-SURPLUS")
    assert response.status_code == 200
    data = response.json()
    assert data["intelligence"]["signal"] == "SURPLUS_SIGNAL"
    assert data["intelligence"]["potential_surplus"] == 7500

def test_passport_insufficient_data(client, db_session):
    # TEST 3: Insufficient Data
    m = NationalMaterial(id="CNMC-INSUFFICIENT", canonical_description="Test", category="Test")
    db_session.add(m)
    # Missing inventory, only demand
    db_session.add(Demand(cnmc_id="CNMC-INSUFFICIENT", demand_type="CURRENT", quantity=10000))
    db_session.commit()

    response = client.get("/api/v1/passport/CNMC-INSUFFICIENT")
    assert response.status_code == 200
    data = response.json()
    assert data["intelligence"]["signal"] == "INSUFFICIENT_DATA"

def test_passport_balanced(client, db_session):
    # TEST 4: Balanced
    m = NationalMaterial(id="CNMC-BALANCED", canonical_description="Test", category="Test")
    db_session.add(m)
    db_session.add(Inventory(cnmc_id="CNMC-BALANCED", total_quantity=5000, reserved_quantity=0, location="Loc1"))
    db_session.add(Demand(cnmc_id="CNMC-BALANCED", demand_type="CURRENT", quantity=5000))
    db_session.commit()

    response = client.get("/api/v1/passport/CNMC-BALANCED")
    assert response.status_code == 200
    data = response.json()
    assert data["intelligence"]["signal"] == "BALANCED"
    assert data["intelligence"]["potential_gap"] == 0

def test_inactive_cnmc(client, db_session):
    # TEST 5: Inactive CNMC (should technically not be returned or handled gracefully)
    m = NationalMaterial(id="CNMC-INACTIVE", canonical_description="Test", category="Test", status="INACTIVE")
    db_session.add(m)
    db_session.commit()

    response = client.get("/api/v1/passport/CNMC-INACTIVE")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "INACTIVE" # For now we return it but flag it INACTIVE
