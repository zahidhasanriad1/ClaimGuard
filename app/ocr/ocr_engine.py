from functools import lru_cache
from pathlib import Path
from typing import Any

from app.schemas.document import OCRTextBlock, PageOCRResult


def _to_plain_object(value: Any) -> Any:
    if hasattr(value, "tolist"):
        return value.tolist()
    return value


def _extract_result_dict(item: Any) -> dict:
    if isinstance(item, dict):
        data = item
    elif hasattr(item, "res"):
        data = {"res": getattr(item, "res")}
    elif hasattr(item, "__dict__"):
        data = item.__dict__
    else:
        data = {}

    if "res" in data and isinstance(data["res"], dict):
        return data["res"]

    return data


@lru_cache(maxsize=1)
def get_ocr_engine():
    from paddleocr import PaddleOCR

    engine = PaddleOCR(
        use_doc_orientation_classify=False,
        use_doc_unwarping=False,
        use_textline_orientation=False,
    )
    return engine


def run_ocr_on_image(image_path: Path) -> PageOCRResult:
    engine = get_ocr_engine()

    try:
        output = engine.predict(str(image_path))
        if not output:
            return PageOCRResult(
                page_number=0,
                image_path=str(image_path),
                full_text="",
                blocks=[],
                ran_ocr=True,
                error=None,
            )

        first_item = output[0]
        result = _extract_result_dict(first_item)

        texts = _to_plain_object(result.get("rec_texts", [])) or []
        scores = _to_plain_object(result.get("rec_scores", [])) or []
        polys = _to_plain_object(result.get("rec_polys", [])) or []

        blocks: list[OCRTextBlock] = []
        for idx, text in enumerate(texts):
            text_str = str(text).strip()
            if not text_str:
                continue

            score_val = None
            if idx < len(scores):
                try:
                    score_val = float(scores[idx])
                except Exception:
                    score_val = None

            bbox_val: list[list[int]] = []
            if idx < len(polys):
                raw_poly = polys[idx]
                try:
                    bbox_val = [[int(p[0]), int(p[1])] for p in raw_poly]
                except Exception:
                    bbox_val = []

            blocks.append(
                OCRTextBlock(
                    text=text_str,
                    score=score_val,
                    bbox=bbox_val,
                )
            )

        full_text = " ".join(block.text for block in blocks).strip()

        return PageOCRResult(
            page_number=0,
            image_path=str(image_path),
            full_text=full_text,
            blocks=blocks,
            ran_ocr=True,
            error=None,
        )

    except Exception as exc:
        return PageOCRResult(
            page_number=0,
            image_path=str(image_path),
            full_text="",
            blocks=[],
            ran_ocr=False,
            error=str(exc),
        )