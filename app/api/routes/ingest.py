from pathlib import Path
from uuid import uuid4

from fastapi import APIRouter, File, HTTPException, UploadFile, status

from app.core.config import settings
from app.ocr.ocr_engine import run_ocr_on_image
from app.parsers.page_renderer import render_pdf_pages
from app.parsers.page_text_resolver import resolve_page_texts
from app.parsers.pdf_parser import extract_pdf_metadata, extract_pdf_page_texts
from app.schemas.document import PageOCRResult, UploadResponse
from app.storage.document_store import save_upload_response

router = APIRouter(prefix="/ingest", tags=["ingest"])


@router.post("/upload", response_model=UploadResponse)
async def upload_pdf(file: UploadFile = File(...)) -> UploadResponse:
    original_name = file.filename or "uploaded.pdf"
    extension = Path(original_name).suffix.lower()

    if extension != ".pdf":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only PDF files are allowed in Step 5.",
        )

    contents = await file.read()
    if not contents:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Uploaded file is empty.",
        )

    document_id = uuid4().hex
    saved_filename = f"{document_id}.pdf"
    saved_path = settings.raw_docs_dir / saved_filename
    saved_path.write_bytes(contents)

    try:
        metadata = extract_pdf_metadata(saved_path)
        native_page_texts = extract_pdf_page_texts(saved_path)

        rendered_pages = render_pdf_pages(
            pdf_path=saved_path,
            output_dir=settings.pages_dir,
            document_id=document_id,
        )
        metadata.rendered_pages = rendered_pages

        ocr_pages: list[PageOCRResult] = []
        if settings.ocr_enabled:
            for rendered_page in rendered_pages:
                if rendered_page.is_scan_like:
                    ocr_result = run_ocr_on_image(Path(rendered_page.image_path))
                    ocr_result.page_number = rendered_page.page_number
                    ocr_pages.append(ocr_result)

        metadata.ocr_pages = ocr_pages
        metadata.resolved_pages = resolve_page_texts(
            native_page_texts=native_page_texts,
            ocr_pages=ocr_pages,
        )

        response_payload = UploadResponse(
            document_id=document_id,
            original_filename=original_name,
            saved_path=str(saved_path),
            metadata=metadata,
        )

        save_upload_response(response_payload)
        return response_payload

    except Exception as exc:
        if saved_path.exists():
            saved_path.unlink(missing_ok=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to parse PDF: {str(exc)}",
        ) from exc