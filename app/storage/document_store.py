from pathlib import Path

from app.core.config import settings
from app.schemas.document import UploadResponse


def get_parsed_document_path(document_id: str) -> Path:
    return settings.parsed_docs_dir / f"{document_id}.json"


def save_upload_response(payload: UploadResponse) -> Path:
    output_path = get_parsed_document_path(payload.document_id)
    output_path.write_text(
        payload.model_dump_json(indent=2),
        encoding="utf-8",
    )
    return output_path


def load_upload_response(document_id: str) -> UploadResponse:
    input_path = get_parsed_document_path(document_id)
    if not input_path.exists():
        raise FileNotFoundError(f"Parsed document not found for document_id={document_id}")

    raw = input_path.read_text(encoding="utf-8")
    return UploadResponse.model_validate_json(raw)