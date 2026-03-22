from pydantic import BaseModel, Field


class ExportFileResponse(BaseModel):
    document_id: str
    export_type: str
    file_path: str
    total_items: int = 0


class DocumentListItem(BaseModel):
    document_id: str
    original_filename: str
    saved_path: str
    page_count: int
    title: str | None = None
    author: str | None = None


class DocumentListResponse(BaseModel):
    total_documents: int
    documents: list[DocumentListItem] = Field(default_factory=list)