from fastapi import APIRouter, HTTPException, Query, status

from app.schemas.export import ExportFileResponse
from app.schemas.verification import VerificationResponse
from app.services.claim_extractor import extract_claims_from_resolved_pages
from app.services.claim_postprocessor import deduplicate_claims, prioritize_claims
from app.services.claim_verifier import verify_claims_against_resolved_pages
from app.services.gemini_claim_extractor import extract_claims_with_gemini
from app.storage.claim_store import claim_cache_exists, load_claims, save_claims
from app.storage.document_store import load_upload_response
from app.storage.verification_store import (
    export_summary_json,
    export_verification_csv,
    export_verification_json,
    save_verification,
)

router = APIRouter(prefix="/exports", tags=["exports"])


def build_verification_payload(
    document_id: str,
    mode: str,
    max_claims: int,
    use_tables: bool,
) -> VerificationResponse:
    payload = load_upload_response(document_id)

    if claim_cache_exists(document_id, mode):
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

    supported = sum(1 for item in results if item.verdict == "supported")
    contradicted = sum(1 for item in results if item.verdict == "contradicted")
    insufficient = sum(1 for item in results if item.verdict == "insufficient")

    verification_payload = VerificationResponse(
        document_id=document_id,
        total_claims=len(results),
        supported=supported,
        contradicted=contradicted,
        insufficient=insufficient,
        results=results,
    )

    save_verification(document_id, mode, verification_payload)
    return verification_payload


@router.post("/{document_id}/summary", response_model=ExportFileResponse)
def export_summary(
    document_id: str,
    mode: str = Query(default="rule", pattern="^(rule|gemini)$"),
    max_claims: int = Query(default=100, ge=1, le=1000),
    use_tables: bool = Query(default=False),
) -> ExportFileResponse:
    try:
        verification_payload = build_verification_payload(
            document_id=document_id,
            mode=mode,
            max_claims=max_claims,
            use_tables=use_tables,
        )
        output_path = export_summary_json(document_id, mode, verification_payload)
    except FileNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Summary export failed: {str(exc)}",
        ) from exc

    return ExportFileResponse(
        document_id=document_id,
        export_type="summary_json",
        file_path=str(output_path),
        total_items=verification_payload.total_claims,
    )


@router.post("/{document_id}/verification-json", response_model=ExportFileResponse)
def export_verification_as_json(
    document_id: str,
    mode: str = Query(default="rule", pattern="^(rule|gemini)$"),
    max_claims: int = Query(default=100, ge=1, le=1000),
    use_tables: bool = Query(default=False),
) -> ExportFileResponse:
    try:
        verification_payload = build_verification_payload(
            document_id=document_id,
            mode=mode,
            max_claims=max_claims,
            use_tables=use_tables,
        )
        output_path = export_verification_json(document_id, mode, verification_payload)
    except FileNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Verification JSON export failed: {str(exc)}",
        ) from exc

    return ExportFileResponse(
        document_id=document_id,
        export_type="verification_json",
        file_path=str(output_path),
        total_items=verification_payload.total_claims,
    )


@router.post("/{document_id}/verification-csv", response_model=ExportFileResponse)
def export_verification_as_csv(
    document_id: str,
    mode: str = Query(default="rule", pattern="^(rule|gemini)$"),
    max_claims: int = Query(default=100, ge=1, le=1000),
    use_tables: bool = Query(default=False),
) -> ExportFileResponse:
    try:
        verification_payload = build_verification_payload(
            document_id=document_id,
            mode=mode,
            max_claims=max_claims,
            use_tables=use_tables,
        )
        output_path = export_verification_csv(document_id, mode, verification_payload)
    except FileNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Verification CSV export failed: {str(exc)}",
        ) from exc

    return ExportFileResponse(
        document_id=document_id,
        export_type="verification_csv",
        file_path=str(output_path),
        total_items=verification_payload.total_claims,
    )