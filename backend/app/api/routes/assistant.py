from fastapi import APIRouter
from app.schemas import AssistantQueryRequest, AssistantQueryResponse
from app.services.qa_service import answer_scheme_question

router = APIRouter(prefix="/assistant", tags=["Grounded Assistant"])

@router.post("/query", response_model=AssistantQueryResponse)
def query_assistant(req: AssistantQueryRequest):
    return answer_scheme_question(req.query, req.scheme_code, req.language)

