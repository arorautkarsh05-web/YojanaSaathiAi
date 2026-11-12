from fastapi import APIRouter, HTTPException, status
from typing import List, Dict, Any
from app.services.scheme_catalogue import SCHEME_CATALOGUE

router = APIRouter(prefix="/schemes", tags=["Scheme Catalogue"])

@router.get("", response_model=List[Dict[str, Any]])
def list_schemes():
    """Returns curated, verified schemes for Uttar Pradesh farmers."""
    return list(SCHEME_CATALOGUE.values())

@router.get("/{scheme_code}", response_model=Dict[str, Any])
def get_scheme(scheme_code: str):
    code = scheme_code.upper()
    if code not in SCHEME_CATALOGUE:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Scheme '{scheme_code}' is not in the verified UP catalogue."
        )
    return SCHEME_CATALOGUE[code]

