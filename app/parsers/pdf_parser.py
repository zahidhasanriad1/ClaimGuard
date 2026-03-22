from pathlib import Path

import pymupdf

from app.schemas.document import DocumentMetadata, PagePreview


def clean_text(text: str, limit: int = 500) -> str:
    text = " ".join((text or "").split())
    return text[:limit]


def normalize_text(text: str) -> str:
    return " ".join((text or "").split())


def extract_pdf_page_texts(file_path: Path) -> list[str]:
    page_texts: list[str] = []

    with pymupdf.open(str(file_path)) as doc:
        for page_index in range(len(doc)):
            page = doc.load_page(page_index)
            text = page.get_text("text") or ""
            page_texts.append(normalize_text(text))

    return page_texts


def extract_pdf_metadata(file_path: Path, preview_pages: int = 3) -> DocumentMetadata:
    with pymupdf.open(str(file_path)) as doc:
        metadata = doc.metadata or {}
        page_count = len(doc)

        previews: list[PagePreview] = []
        for page_index in range(min(preview_pages, page_count)):
            page = doc.load_page(page_index)
            text = page.get_text("text")
            previews.append(
                PagePreview(
                    page_number=page_index + 1,
                    text_preview=clean_text(text),
                )
            )

        return DocumentMetadata(
            title=metadata.get("title") or None,
            author=metadata.get("author") or None,
            page_count=page_count,
            file_size_bytes=file_path.stat().st_size,
            previews=previews,
            rendered_pages=[],
            ocr_pages=[],
            resolved_pages=[],
            extracted_tables=[],
        )