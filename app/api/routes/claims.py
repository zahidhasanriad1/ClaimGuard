from fastapi import APIRouter, HTTPException, status

from app.schemas.claim import ClaimExtractionResponse
from app.services.claim_extractor import extract_claims_from_resolved_pages
from app.storage.document_store import load_upload_response

router = APIRouter(prefix="/claims", tags=["claims"])


@router.get("/{document_id}", response_model=ClaimExtractionResponse)
def extract_claims(document_id: str) -> ClaimExtractionResponse:
    try:
        payload = load_upload_response(document_id)
    except FileNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc

    claims = extract_claims_from_resolved_pages(payload.metadata.resolved_pages)

    return ClaimExtractionResponse(
        document_id=document_id,
        total_claims=len(claims),
        claims=claims,
    )