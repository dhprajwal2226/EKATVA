def detect_intent(query: str) -> str:
    query_lower = query.lower()
    
    if "cpse" in query_lower or "which cpses" in query_lower:
        return "CPSE_LOOKUP"
    elif "passport" in query_lower:
        return "PASSPORT_LOOKUP"
    elif "where" in query_lower or "stored" in query_lower or "location" in query_lower:
        return "INVENTORY_LOOKUP"
    elif "vendor" in query_lower or "supplier" in query_lower:
        return "VENDOR_LOOKUP"
    elif "shortage" in query_lower or "enough inventory" in query_lower or "gap" in query_lower:
        return "SHORTAGE_LOOKUP"
    elif "surplus" in query_lower:
        return "SURPLUS_LOOKUP"
    elif "conflict" in query_lower:
        return "CONFLICT_LOOKUP"
    elif "map" in query_lower or "why" in query_lower:
        return "MATCH_LOOKUP"
    
    if "cnmc" in query_lower:
        return "MATERIAL_LOOKUP"
        
    return "UNKNOWN"
