from fastapi import APIRouter, HTTPException, Query, status

from app.schemas.claim import ClaimExtractionResponse
from app.services.claim_extractor import extract_claims_from_resolved_pages
from app.services.claim_postprocessor import deduplicate_claims, prioritize_claims
from app.storage.document_store import load_upload_response

router = APIRouter(prefix="/claims", tags=["claims"])


@router.get("/{document_id}", response_model=ClaimExtractionResponse)
def extract_claims(
    document_id: str,
    max_claims: int = Query(default=200, ge=1, le=1000),
) -> ClaimExtractionResponse:
    try:
        payload = load_upload_response(document_id)
    except FileNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc

    claims = extract_claims_from_resolved_pages(payload.metadata.resolved_pages)
    claims = deduplicate_claims(claims)
    claims = prioritize_claims(claims, max_claims=max_claims)

    return ClaimExtractionResponse(
        document_id=document_id,
        total_claims=len(claims),
        claims=claims,
    )