import json
import re
from uuid import uuid4

from app.core.config import settings
from app.schemas.claim import ClaimCandidate

try:
    from google import genai
except Exception:
    genai = None


def _extract_json_array(text: str) -> list[dict]:
    text = (text or "").strip()
    if not text:
        return []

    try:
        data = json.loads(text)
        if isinstance(data, list):
            return data
    except Exception:
        pass

    match = re.search(r"\[\s*{.*}\s*\]", text, re.DOTALL)
    if match:
        try:
            data = json.loads(match.group(0))
            if isinstance(data, list):
                return data
        except Exception:
            return []

    return []


def _safe_float(value) -> float | None:
    if value is None or value == "":
        return None

    try:
        return float(value)
    except Exception:
        return None


def _safe_str(value) -> str | None:
    if value is None:
        return None
    text = str(value).strip()
    return text if text else None


def _build_page_prompt(page_number: int, page_text: str) -> str:
    return f"""
You are extracting meaningful numerical claims from a report page.

Rules:
1. Extract only meaningful report claims with numbers.
2. Ignore citation numbers, reference numbers, author affiliations, emails, page numbers, section numbers, figure numbers, table numbers, DOI, URLs, model version names such as YOLOv5, VHR 10, GPT 4, and isolated numbers without claim meaning.
3. Prefer claims about metrics, percentages, money, counts, growth, decline, ranking, comparison, speed, latency, images, epochs, and dimensions when they are part of a meaningful statement.
4. Return only a JSON array.
5. Each item must have these keys:
   page_number
   sentence_text
   claim_type
   raw_value
   numeric_value
   unit
   trend_direction
   comparator
   confidence
6. claim_type must be one of:
   absolute, percentage, currency, trend, comparison, ranking
7. confidence must be between 0 and 1.

Page number: {page_number}

Page text:
\"\"\"
{page_text}
\"\"\"

Return JSON array only.
""".strip()


def extract_claims_with_gemini(resolved_pages: list) -> list[ClaimCandidate]:
    if not settings.gemini_api_key:
        raise ValueError("GEMINI_API_KEY is missing in .env")

    if genai is None:
        raise ImportError("google genai package is not available")

    client = genai.Client(api_key=settings.gemini_api_key)
    all_claims: list[ClaimCandidate] = []

    for page in resolved_pages:
        page_text = (page.text or "").strip()
        if not page_text:
            continue

        prompt = _build_page_prompt(page.page_number, page_text)

        try:
            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=prompt,
            )
            raw_text = getattr(response, "text", "") or ""
            items = _extract_json_array(raw_text)
        except Exception:
            items = []

        for item in items:
            sentence_text = _safe_str(item.get("sentence_text"))
            raw_value = _safe_str(item.get("raw_value"))

            if not sentence_text or not raw_value:
                continue

            claim_type = _safe_str(item.get("claim_type")) or "absolute"
            if claim_type not in {"absolute", "percentage", "currency", "trend", "comparison", "ranking"}:
                claim_type = "absolute"

            confidence = _safe_float(item.get("confidence"))
            if confidence is None:
                confidence = 0.75
            confidence = max(0.0, min(1.0, confidence))

            all_claims.append(
                ClaimCandidate(
                    claim_id=uuid4().hex,
                    page_number=int(item.get("page_number") or page.page_number),
                    sentence_text=sentence_text,
                    claim_type=claim_type,
                    raw_value=raw_value,
                    numeric_value=_safe_float(item.get("numeric_value")),
                    unit=_safe_str(item.get("unit")),
                    trend_direction=_safe_str(item.get("trend_direction")),
                    comparator=_safe_str(item.get("comparator")),
                    confidence=confidence,
                )
            )

    return all_claims