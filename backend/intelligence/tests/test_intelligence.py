import pytest
from app.services.procurement_service import analyze_procurement
from app.models.inventory import Inventory
from app.models.demand import Demand

class MockSession:
    def __init__(self, inventories, demands):
        self.inventories = inventories
        self.demands = demands
        
    def query(self, model):
        return self
        
    def filter(self, condition):
        return self
        
    def all(self):
        # Extremely simplified mock specifically for testing logic independently of real DB
        if self.current_model == Inventory:
            return self.inventories
        elif self.current_model == Demand:
            return self.demands
        return []

# Monkeypatching for tests
import app.services.procurement_service as ps

def test_shortage_signal():
    # Inventory = 11500, Demand = 33000
    inv = Inventory(available_quantity=11500, cpse_id="IOCL")
    dem = Demand(forecast_quantity=33000, cpse_id="IOCL")
    
    ps.get_inventory_by_cnmc = lambda db, cnmc: [inv]
    ps.get_demand_by_cnmc = lambda db, cnmc: [dem]
    
    result = analyze_procurement(None, "CNMC-000001")
    assert result.potential_gap == 21500
    assert result.status == "SHORTAGE_SIGNAL"

def test_surplus_signal():
    # Inventory = 10000, Demand = 2500
    inv = Inventory(available_quantity=10000, cpse_id="IOCL")
    dem = Demand(forecast_quantity=2500, cpse_id="IOCL")
    
    ps.get_inventory_by_cnmc = lambda db, cnmc: [inv]
    ps.get_demand_by_cnmc = lambda db, cnmc: [dem]
    
    result = analyze_procurement(None, "CNMC-000002")
    assert result.potential_gap == -7500
    assert result.status == "SURPLUS_SIGNAL"

def test_insufficient_data():
    # Missing inventory data
    dem = Demand(forecast_quantity=10000, cpse_id="IOCL")
    
    ps.get_inventory_by_cnmc = lambda db, cnmc: []
    ps.get_demand_by_cnmc = lambda db, cnmc: [dem]
    
    result = analyze_procurement(None, "CNMC-000004")
    assert result.status == "INSUFFICIENT_DATA"

def test_balanced_signal():
    # Inventory = 5000, Demand = 5000
    inv = Inventory(available_quantity=5000, cpse_id="IOCL")
    dem = Demand(forecast_quantity=5000, cpse_id="IOCL")
    
    ps.get_inventory_by_cnmc = lambda db, cnmc: [inv]
    ps.get_demand_by_cnmc = lambda db, cnmc: [dem]
    
    result = analyze_procurement(None, "CNMC-000003")
    assert result.status == "BALANCED"
