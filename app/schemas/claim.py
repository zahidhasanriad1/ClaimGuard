from pydantic import BaseModel, Field


class ClaimCandidate(BaseModel):
    claim_id: str
    page_number: int
    sentence_text: str
    claim_type: str
    raw_value: str
    numeric_value: float | None = None
    unit: str | None = None
    trend_direction: str | None = None
    comparator: str | None = None
    confidence: float = 0.0


class ClaimExtractionResponse(BaseModel):
    document_id: str
    total_claims: int
    claims: list[ClaimCandidate] = Field(default_factory=list)