from fastapi import APIRouter, HTTPException, Query, status

from app.graph.verification_graph import run_verification_graph
from app.schemas.export import ExportFileResponse
from app.storage.verification_store import (
    export_summary_json,
    export_verification_csv,
    export_verification_json,
)

router = APIRouter(prefix="/exports", tags=["exports"])


@router.post("/{document_id}/summary", response_model=ExportFileResponse)
def export_summary(
    document_id: str,
    mode: str = Query(default="rule", pattern="^(rule|gemini)$"),
    max_claims: int = Query(default=100, ge=1, le=1000),
    use_tables: bool = Query(default=False),
) -> ExportFileResponse:
    try:
        verification_payload = run_verification_graph(
            document_id=document_id,
            mode=mode,
            max_claims=max_claims,
            use_tables=use_tables,
            include_results=True,
            use_cache=True,
            refresh=False,
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
        verification_payload = run_verification_graph(
            document_id=document_id,
            mode=mode,
            max_claims=max_claims,
            use_tables=use_tables,
            include_results=True,
            use_cache=True,
            refresh=False,
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
        verification_payload = run_verification_graph(
            document_id=document_id,
            mode=mode,
            max_claims=max_claims,
            use_tables=use_tables,
            include_results=True,
            use_cache=True,
            refresh=False,
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