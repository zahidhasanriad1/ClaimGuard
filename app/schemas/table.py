from pydantic import BaseModel, Field

from app.schemas.document import ExtractedTableRow


class TableExtractionResponse(BaseModel):
    document_id: str
    total_rows: int
    rows: list[ExtractedTableRow] = Field(default_factory=list)