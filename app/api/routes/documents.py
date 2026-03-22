from fastapi import APIRouter

from app.schemas.export import DocumentListResponse
from app.storage.document_index import list_parsed_documents

router = APIRouter(prefix="/documents", tags=["documents"])


@router.get("", response_model=DocumentListResponse)
def get_documents() -> DocumentListResponse:
    items = list_parsed_documents()
    return DocumentListResponse(
        total_documents=len(items),
        documents=items,
    )