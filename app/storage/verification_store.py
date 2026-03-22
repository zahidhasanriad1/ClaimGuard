import json
from pathlib import Path

from app.core.config import settings
from app.schemas.verification import VerificationResponse


def get_verification_cache_path(document_id: str, mode: str) -> Path:
    safe_mode = mode.lower().strip()
    return settings.parsed_docs_dir / f"{document_id}.verify.{safe_mode}.json"


def save_verification(document_id: str, mode: str, payload: VerificationResponse) -> Path:
    output_path = get_verification_cache_path(document_id, mode)
    output_path.write_text(
        payload.model_dump_json(indent=2),
        encoding="utf-8",
    )
    return output_path


def load_verification(document_id: str, mode: str) -> VerificationResponse:
    input_path = get_verification_cache_path(document_id, mode)
    if not input_path.exists():
        raise FileNotFoundError(f"Verification cache not found for document_id={document_id}, mode={mode}")

    raw = input_path.read_text(encoding="utf-8")
    return VerificationResponse.model_validate_json(raw)


def verification_cache_exists(document_id: str, mode: str) -> bool:
    return get_verification_cache_path(document_id, mode).exists()


def export_verification_json(document_id: str, mode: str, payload: VerificationResponse) -> Path:
    export_dir = settings.exports_dir / document_id
    export_dir.mkdir(parents=True, exist_ok=True)

    output_path = export_dir / f"verification_{mode}.json"
    output_path.write_text(
        payload.model_dump_json(indent=2),
        encoding="utf-8",
    )
    return output_path


def export_verification_csv(document_id: str, mode: str, payload: VerificationResponse) -> Path:
    import csv

    export_dir = settings.exports_dir / document_id
    export_dir.mkdir(parents=True, exist_ok=True)

    output_path = export_dir / f"verification_{mode}.csv"

    with output_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(
            [
                "claim_id",
                "claim_page_number",
                "claim_text",
                "claim_type",
                "raw_value",
                "numeric_value",
                "verdict",
                "confidence",
                "evidence_source_type",
                "evidence_page_number",
                "evidence_text",
                "evidence_row_text",
                "notes",
            ]
        )

        for item in payload.results:
            writer.writerow(
                [
                    item.claim_id,
                    item.claim_page_number,
                    item.claim_text,
                    item.claim_type,
                    item.raw_value,
                    item.numeric_value,
                    item.verdict,
                    item.confidence,
                    item.matched_evidence.source_type if item.matched_evidence else "",
                    item.matched_evidence.page_number if item.matched_evidence else "",
                    item.matched_evidence.sentence_text if item.matched_evidence else "",
                    item.matched_evidence.row_text if item.matched_evidence else "",
                    " | ".join(item.notes),
                ]
            )

    return output_path


def export_summary_json(document_id: str, mode: str, payload: VerificationResponse) -> Path:
    export_dir = settings.exports_dir / document_id
    export_dir.mkdir(parents=True, exist_ok=True)

    output_path = export_dir / f"summary_{mode}.json"
    summary = {
        "document_id": payload.document_id,
        "total_claims": payload.total_claims,
        "supported": payload.supported,
        "contradicted": payload.contradicted,
        "insufficient": payload.insufficient,
    }
    output_path.write_text(
        json.dumps(summary, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    return output_path