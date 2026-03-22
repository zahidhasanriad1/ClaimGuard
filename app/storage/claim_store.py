from pathlib import Path

from app.core.config import settings
from app.schemas.claim import ClaimCandidate


def get_claim_cache_path(document_id: str, mode: str) -> Path:
    safe_mode = mode.lower().strip()
    return settings.parsed_docs_dir / f"{document_id}.claims.{safe_mode}.json"


def save_claims(document_id: str, mode: str, claims: list[ClaimCandidate]) -> Path:
    output_path = get_claim_cache_path(document_id, mode)
    payload = [claim.model_dump() for claim in claims]
    output_path.write_text(
        __import__("json").dumps(payload, ensure_ascii=False, indent=2),
        encoding="utf 8",
    )
    return output_path


def load_claims(document_id: str, mode: str) -> list[ClaimCandidate]:
    input_path = get_claim_cache_path(document_id, mode)
    if not input_path.exists():
        raise FileNotFoundError(f"Claim cache not found for document_id={document_id}, mode={mode}")

    raw = input_path.read_text(encoding="utf 8")
    data = __import__("json").loads(raw)
    return [ClaimCandidate.model_validate(item) for item in data]


def claim_cache_exists(document_id: str, mode: str) -> bool:
    return get_claim_cache_path(document_id, mode).exists()