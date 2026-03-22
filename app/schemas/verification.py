from pydantic import BaseModel, Field


class EvidenceMatch(BaseModel):
    source_type: str = "text"
    page_number: int
    sentence_text: str = ""
    raw_numbers: list[str] = Field(default_factory=list)
    keyword_overlap: list[str] = Field(default_factory=list)
    score: float = 0.0
    table_index: int | None = None
    row_index: int | None = None
    row_text: str | None = None


class ClaimVerificationResult(BaseModel):
    claim_id: str
    claim_page_number: int
    claim_text: str
    claim_type: str
    raw_value: str
    numeric_value: float | None = None
    verdict: str
    confidence: float = 0.0
    matched_evidence: EvidenceMatch | None = None
    notes: list[str] = Field(default_factory=list)


class VerificationResponse(BaseModel):
    document_id: str
    total_claims: int
    supported: int = 0
    contradicted: int = 0
    insufficient: int = 0
    results: list[ClaimVerificationResult] = Field(default_factory=list)