from fastapi import APIRouter, HTTPException, status

from app.schemas.verification import VerificationResponse
from app.services.claim_extractor import extract_claims_from_resolved_pages
from app.services.claim_verifier import verify_claims_against_resolved_pages
from app.storage.document_store import load_upload_response

router = APIRouter(prefix="/verify", tags=["verify"])


@router.get("/{document_id}", response_model=VerificationResponse)
def verify_document_claims(document_id: str) -> VerificationResponse:
    try:
        payload = load_upload_response(document_id)
    except FileNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc

    claims = extract_claims_from_resolved_pages(payload.metadata.resolved_pages)
    results = verify_claims_against_resolved_pages(
        claims=claims,
        resolved_pages=payload.metadata.resolved_pages,
        extracted_tables=payload.metadata.extracted_tables,
    )

    supported = sum(1 for item in results if item.verdict == "supported")
    contradicted = sum(1 for item in results if item.verdict == "contradicted")
    insufficient = sum(1 for item in results if item.verdict == "insufficient")

    return VerificationResponse(
        document_id=document_id,
        total_claims=len(results),
        supported=supported,
        contradicted=contradicted,
        insufficient=insufficient,
        results=results,
    )