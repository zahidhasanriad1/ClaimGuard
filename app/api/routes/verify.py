from fastapi import APIRouter, HTTPException, Query, status

from app.graph.verification_graph import run_verification_graph
from app.schemas.verification import VerificationResponse

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
        return run_verification_graph(
            document_id=document_id,
            mode=mode,
            max_claims=max_claims,
            use_tables=use_tables,
            include_results=include_results,
            use_cache=use_cache,
            refresh=refresh,
        )
    except FileNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Verification failed: {str(exc)}",
        ) from exc