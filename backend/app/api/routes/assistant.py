from fastapi import APIRouter
from app.schemas import (
    AssistantQueryRequest,
    AssistantQueryResponse,
    ConversationalIntakeRequest,
    ConversationalIntakeResponse
)
from app.services.qa_service import answer_scheme_question
from app.services.farmer_intake_service import parse_conversational_intake

router = APIRouter(prefix="/assistant", tags=["Grounded Assistant"])

@router.post("/query", response_model=AssistantQueryResponse)
def query_assistant(req: AssistantQueryRequest):
    return answer_scheme_question(req.query, req.scheme_code, req.language)

@router.post("/intake", response_model=ConversationalIntakeResponse)
def natural_language_farmer_intake(req: ConversationalIntakeRequest):
    """
    Translates free-form farmer speech/text (Hindi, English, Hinglish, Punjabi)
    into structured profile parameters, detects unit ambiguities (e.g. bigha variations),
    and identifies missing attributes for deterministic eligibility evaluation.
    """
    return parse_conversational_intake(req)

