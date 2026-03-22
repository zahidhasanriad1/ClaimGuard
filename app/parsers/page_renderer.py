from pathlib import Path

import pymupdf

from app.schemas.document import RenderedPageInfo


def render_pdf_pages(
    pdf_path: Path,
    output_dir: Path,
    document_id: str,
    zoom: float = 1.5,
    scan_text_threshold: int = 40,
) -> list[RenderedPageInfo]:
    rendered_pages: list[RenderedPageInfo] = []

    with pymupdf.open(str(pdf_path)) as doc:
        for page_index in range(len(doc)):
            page = doc.load_page(page_index)

            text = page.get_text("text") or ""
            normalized_text = " ".join(text.split())
            extracted_text_chars = len(normalized_text)

            matrix = pymupdf.Matrix(zoom, zoom)
            pix = page.get_pixmap(matrix=matrix, alpha=False)

            image_filename = f"{document_id}_page_{page_index + 1}.png"
            image_path = output_dir / image_filename
            pix.save(str(image_path))

            rendered_pages.append(
                RenderedPageInfo(
                    page_number=page_index + 1,
                    image_path=str(image_path),
                    width=pix.width,
                    height=pix.height,
                    extracted_text_chars=extracted_text_chars,
                    is_scan_like=extracted_text_chars < scan_text_threshold,
                )
            )

    return rendered_pages