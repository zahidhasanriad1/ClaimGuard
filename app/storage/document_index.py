from pathlib import Path

from app.core.config import settings
from app.schemas.document import UploadResponse
from app.schemas.export import DocumentListItem


def list_parsed_documents() -> list[DocumentListItem]:
    items: list[DocumentListItem] = []

    for path in sorted(settings.parsed_docs_dir.glob("*.json")):
        name = path.name

        if ".claims." in name or ".verify." in name:
            continue

        try:
            payload = UploadResponse.model_validate_json(path.read_text(encoding="utf-8"))
        except Exception:
            continue

        items.append(
            DocumentListItem(
                document_id=payload.document_id,
                original_filename=payload.original_filename,
                saved_path=payload.saved_path,
                page_count=payload.metadata.page_count,
                title=payload.metadata.title,
                author=payload.metadata.author,
            )
        )

    items.sort(key=lambda x: x.document_id, reverse=True)
    return items