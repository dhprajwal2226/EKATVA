from fastapi import FastAPI
from app.api import vendors, locations, inventory, demand, procurement, intelligence, graph

app = FastAPI(title="National Material Intelligence Engine")

app.include_router(vendors.router, prefix="/api/vendors", tags=["vendors"])
app.include_router(locations.router, prefix="/api/locations", tags=["locations"])
app.include_router(inventory.router, prefix="/api/inventory", tags=["inventory"])
app.include_router(demand.router, prefix="/api/demand", tags=["demand"])
app.include_router(procurement.router, prefix="/api/procurement", tags=["procurement"])
app.include_router(intelligence.router, prefix="/api/intelligence", tags=["intelligence"])
app.include_router(graph.router, prefix="/api/graph", tags=["graph"])




@app.get("/")
def read_root():
    return {"status": "ok"}
