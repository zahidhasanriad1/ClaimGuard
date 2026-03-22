from fastapi import APIRouter, HTTPException, status

from app.schemas.table import TableExtractionResponse
from app.storage.document_store import load_upload_response

router = APIRouter(prefix="/tables", tags=["tables"])


@router.get("/{document_id}", response_model=TableExtractionResponse)
def get_tables(document_id: str) -> TableExtractionResponse:
    try:
        payload = load_upload_response(document_id)
    except FileNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc

    rows = payload.metadata.extracted_tables

    return TableExtractionResponse(
        document_id=document_id,
        total_rows=len(rows),
        rows=rows,
    )