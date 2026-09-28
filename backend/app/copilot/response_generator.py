from app.schemas.copilot import CopilotResponse

def generate_response(intent: str, data: dict, error: str) -> CopilotResponse:
    if error:
        return CopilotResponse(
            answer=error,
            key_findings=[],
            sources=[],
            data_limitation="No verified data could be retrieved for this query.",
            intent=intent
        )
        
    answer = ""
    key_findings = []
    sources = data.get("sources", [])
    data_limitation = None
    
    if intent in ["CPSE_LOOKUP", "MATCH_LOOKUP"]:
        cpses = [m["cpse"] for m in data.get("cpse_mappings", [])]
        answer = f"{data['cnmc']} is currently mapped to {len(cpses)} CPSEs: {', '.join(cpses)}."
        key_findings = [f"{m['cpse']} uses code {m['code']}" for m in data.get("cpse_mappings", [])]
        
    elif intent == "INVENTORY_LOOKUP":
        locations = [l["location"] for l in data.get("locations", [])]
        answer = f"{data['cnmc']} is stored in {len(locations)} locations: {', '.join(locations)}."
        key_findings = [f"{l['location']}: {l['quantity']} units" for l in data.get("locations", [])]
        
    elif intent == "SHORTAGE_LOOKUP":
        gap = data.get("potential_gap", 0)
        inv = data.get("inventory", 0)
        dem = data.get("demand", 0)
        
        if gap > 0:
            answer = f"The available records indicate a potential supply gap of {gap:,.0f} units for this material."
            data_limitation = "This is an indicative calculation based on available records and does not represent a confirmed procurement shortage."
        else:
            answer = f"There is no potential supply gap indicated by current records."
            
        key_findings = [
            f"Available inventory = {inv:,.0f}",
            f"Demand = {dem:,.0f}",
            f"Potential gap = {gap:,.0f}" if gap > 0 else "Potential gap = 0"
        ]
        
    elif intent == "VENDOR_LOOKUP":
        vendors = [v["name"] for v in data.get("vendors", [])]
        answer = f"There are {len(vendors)} vendors supplying {data['cnmc']}."
        key_findings = vendors
        
    return CopilotResponse(
        answer=answer,
        key_findings=key_findings,
        sources=sources,
        data_limitation=data_limitation,
        intent=intent
    )
