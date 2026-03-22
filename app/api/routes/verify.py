from fastapi import APIRouter, HTTPException, Query, status

from app.schemas.verification import VerificationResponse
from app.services.claim_extractor import extract_claims_from_resolved_pages
from app.services.claim_postprocessor import deduplicate_claims, prioritize_claims
from app.services.claim_verifier import verify_claims_against_resolved_pages
from app.services.gemini_claim_extractor import extract_claims_with_gemini
from app.storage.claim_store import claim_cache_exists, load_claims, save_claims
from app.storage.document_store import load_upload_response

router = APIRouter(prefix="/verify", tags=["verify"])


@router.get("/{document_id}", response_model=VerificationResponse)
def verify_document_claims(
    document_id: str,
    include_results: bool = Query(default=False),
    max_claims: int = Query(default=100, ge=1, le=1000),
    use_tables: bool = Query(default=False),
    mode: str = Query(default="rule", pattern="^(rule|gemini)$"),
    use_cache: bool = Query(default=True),
    refresh: bool = Query(default=False),
) -> VerificationResponse:
    try:
        payload = load_upload_response(document_id)
    except FileNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc

    try:
        if use_cache and not refresh and claim_cache_exists(document_id, mode):
            claims = load_claims(document_id, mode)
        else:
            if mode == "gemini":
                claims = extract_claims_with_gemini(payload.metadata.resolved_pages)
            else:
                claims = extract_claims_from_resolved_pages(payload.metadata.resolved_pages)

            claims = deduplicate_claims(claims)
            save_claims(document_id, mode, claims)

        claims = deduplicate_claims(claims)
        claims = prioritize_claims(claims, max_claims=max_claims)

        results = verify_claims_against_resolved_pages(
            claims=claims,
            resolved_pages=payload.metadata.resolved_pages,
            extracted_tables=payload.metadata.extracted_tables,
            use_tables=use_tables,
        )

    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Verification failed: {str(exc)}",
        ) from exc

    supported = sum(1 for item in results if item.verdict == "supported")
    contradicted = sum(1 for item in results if item.verdict == "contradicted")
    insufficient = sum(1 for item in results if item.verdict == "insufficient")

    return VerificationResponse(
        document_id=document_id,
        total_claims=len(results),
        supported=supported,
        contradicted=contradicted,
        insufficient=insufficient,
        results=results if include_results else [],
    )