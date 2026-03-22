from app.schemas.document import PageOCRResult, ResolvedPageText


def resolve_page_texts(
    native_page_texts: list[str],
    ocr_pages: list[PageOCRResult],
    min_ocr_chars: int = 20,
) -> list[ResolvedPageText]:
    ocr_map = {page.page_number: page for page in ocr_pages}
    resolved_pages: list[ResolvedPageText] = []

    for idx, native_text in enumerate(native_page_texts, start=1):
        native_text = " ".join((native_text or "").split())
        native_chars = len(native_text)

        ocr_result = ocr_map.get(idx)
        ocr_text = ""
        ocr_chars = 0

        if ocr_result and ocr_result.ran_ocr and not ocr_result.error:
            ocr_text = " ".join((ocr_result.full_text or "").split())
            ocr_chars = len(ocr_text)

        use_ocr = ocr_chars >= max(native_chars, min_ocr_chars)

        if use_ocr:
            resolved_pages.append(
                ResolvedPageText(
                    page_number=idx,
                    source="ocr",
                    text=ocr_text,
                    text_chars=ocr_chars,
                    used_ocr=True,
                )
            )
        else:
            resolved_pages.append(
                ResolvedPageText(
                    page_number=idx,
                    source="native",
                    text=native_text,
                    text_chars=native_chars,
                    used_ocr=False,
                )
            )

    return resolved_pages