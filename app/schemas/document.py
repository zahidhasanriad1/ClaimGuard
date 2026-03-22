from pydantic import BaseModel, Field


class PagePreview(BaseModel):
    page_number: int
    text_preview: str = Field(default="")


class RenderedPageInfo(BaseModel):
    page_number: int
    image_path: str
    width: int
    height: int
    extracted_text_chars: int
    is_scan_like: bool


class OCRTextBlock(BaseModel):
    text: str
    score: float | None = None
    bbox: list[list[int]] = Field(default_factory=list)


class PageOCRResult(BaseModel):
    page_number: int
    image_path: str
    full_text: str = ""
    blocks: list[OCRTextBlock] = Field(default_factory=list)
    ran_ocr: bool = False
    error: str | None = None


class ResolvedPageText(BaseModel):
    page_number: int
    source: str
    text: str = ""
    text_chars: int = 0
    used_ocr: bool = False


class ExtractedTableRow(BaseModel):
    page_number: int
    table_index: int
    row_index: int
    headers: list[str] = Field(default_factory=list)
    values: list[str] = Field(default_factory=list)
    row_text: str = ""


class DocumentMetadata(BaseModel):
    title: str | None = None
    author: str | None = None
    page_count: int
    file_size_bytes: int
    previews: list[PagePreview]
    rendered_pages: list[RenderedPageInfo] = Field(default_factory=list)
    ocr_pages: list[PageOCRResult] = Field(default_factory=list)
    resolved_pages: list[ResolvedPageText] = Field(default_factory=list)
    extracted_tables: list[ExtractedTableRow] = Field(default_factory=list)


class UploadResponse(BaseModel):
    document_id: str
    original_filename: str
    saved_path: str
    metadata: DocumentMetadata