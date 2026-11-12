from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import Optional, List
from app.db.session import get_db
from app.schemas import ConvergenceCheckRequest, ConvergenceCheckResponse, ConvergenceGraphResponse
from app.services.convergence_engine import check_multi_scheme_convergence, get_convergence_graph

router = APIRouter(prefix="/convergence", tags=["Multi-Scheme Convergence"])

@router.post("/check", response_model=ConvergenceCheckResponse)
def check_convergence(req: ConvergenceCheckRequest, db: Session = Depends(get_db)):
    pairs = check_multi_scheme_convergence(req.scheme_codes, db=db)
    return ConvergenceCheckResponse(pairs=pairs)

@router.get("/graph", response_model=ConvergenceGraphResponse)
def fetch_convergence_graph(scheme_codes: Optional[str] = None, db: Session = Depends(get_db)):
    codes = [c.strip() for c in scheme_codes.split(",")] if scheme_codes else None
    return get_convergence_graph(codes, db=db)

