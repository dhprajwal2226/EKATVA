from sqlalchemy.orm import Session
from app.schemas.copilot import CopilotRequest, CopilotResponse
from app.copilot.intent import detect_intent
from app.copilot.retrieval import retrieve_verified_data
from app.copilot.response_generator import generate_response

def process_copilot_query(db: Session, request: CopilotRequest) -> CopilotResponse:
    intent = detect_intent(request.query)
    
    if intent == "UNKNOWN":
        return generate_response(intent, {}, "I couldn't map the request to a supported verified-data query.")
        
    data, error = retrieve_verified_data(db, intent, request.query, request.cnmc_id)
    
    response = generate_response(intent, data or {}, error)
    
    return response
