import re
from uuid import uuid4

from app.schemas.claim import ClaimCandidate

SENTENCE_SPLIT_PATTERN = re.compile(r"(?<=[.!?])\s+")
NUMBER_PATTERN = re.compile(
    r"(?P<token>(?:[$€£৳]|USD|BDT|Tk\.?\s*)?\d[\d,]*(?:\.\d+)?(?:\s*(?:%|percent|percentage|million|billion|thousand|ms|s|GB|MB|KB|epochs|pixels|px|images))?)",
    re.IGNORECASE,
)

PERCENT_PATTERN = re.compile(r"(%|percent|percentage)", re.IGNORECASE)
CURRENCY_PATTERN = re.compile(r"(\$|€|£|৳|USD|BDT|Tk\.?)", re.IGNORECASE)
COMPARISON_PATTERN = re.compile(
    r"\b(higher|lower|greater|less|than|compared to|versus|vs\.?)\b",
    re.IGNORECASE,
)
RANKING_PATTERN = re.compile(
    r"\b(highest|lowest|top|bottom|ranked|leading|largest|smallest|best|worst)\b",
    re.IGNORECASE,
)
TREND_UP_PATTERN = re.compile(
    r"\b(increased|increase|grew|growth|rose|improved|improves|improve|higher|up)\b",
    re.IGNORECASE,
)
TREND_DOWN_PATTERN = re.compile(
    r"\b(decreased|decrease|fell|drop|dropped|down|declined|lower)\b",
    re.IGNORECASE,
)
YEAR_PATTERN = re.compile(r"^(19|20)\d{2}$")

HEADER_FOOTER_PATTERN = re.compile(
    r"(scientific reports|www\.|https?://|doi\.org|open\s+scientific|nature\.com|contents lists available|journal homepage)",
    re.IGNORECASE,
)
AFFILIATION_PATTERN = re.compile(
    r"\b(department|faculty|university|school|email:|pakistan|spain|korea|oman|bangladesh|republic of)\b",
    re.IGNORECASE,
)
SECTION_PATTERN = re.compile(
    r"^\s*(section|table|figure|algorithm)\s+\d+\.?\s*$",
    re.IGNORECASE,
)
SHORT_LABEL_PATTERN = re.compile(r"^\s*\d+\.?\s*$")
MODEL_TOKEN_PATTERN = re.compile(
    r"\b(?:yolo|vhr|r-cnn|rcnn|ssd|detr|resnet|vgg|gpt)[a-z\-]*\d+[a-z\-]*\b",
    re.IGNORECASE,
)
CITATION_TAIL_PATTERN = re.compile(r"[A-Za-z][A-Za-z\s,\(\)\-]*\d{1,3}[.,]?$")
BAD_REFERENCE_NUMBER_PATTERN = re.compile(
    r"^\d{1,3}[.,]?$"
)

SAFE_UNITS = {
    "percent",
    "currency",
    "million",
    "billion",
    "thousand",
    "ms",
    "s",
    "gb",
    "mb",
    "kb",
    "epochs",
    "pixels",
    "px",
    "images",
}


def split_sentences(text: str) -> list[str]:
    text = " ".join((text or "").split())
    if not text:
        return []
    parts = SENTENCE_SPLIT_PATTERN.split(text)
    return [part.strip() for part in parts if part.strip()]


def normalize_numeric_value(raw_value: str) -> float | None:
    text = raw_value.strip()

    lower_text = text.lower()
    multiplier = 1.0

    if "billion" in lower_text:
        multiplier = 1_000_000_000.0
    elif "million" in lower_text:
        multiplier = 1_000_000.0
    elif "thousand" in lower_text:
        multiplier = 1_000.0

    cleaned = re.sub(
        r"[$€£৳]|USD|BDT|Tk\.?|%|percent|percentage|million|billion|thousand|ms|s|GB|MB|KB|epochs|pixels|px|images",
        "",
        text,
        flags=re.IGNORECASE,
    )
    cleaned = cleaned.replace(",", "").strip()

    try:
        return float(cleaned) * multiplier
    except Exception:
        return None


def infer_claim_type(sentence: str, raw_value: str) -> tuple[str, str | None, str | None]:
    trend_direction = None
    comparator = None

    if TREND_UP_PATTERN.search(sentence):
        trend_direction = "up"
    elif TREND_DOWN_PATTERN.search(sentence):
        trend_direction = "down"

    if COMPARISON_PATTERN.search(sentence):
        comparator = "comparison"

    if PERCENT_PATTERN.search(raw_value):
        return "percentage", trend_direction, comparator

    if CURRENCY_PATTERN.search(raw_value):
        return "currency", trend_direction, comparator

    if RANKING_PATTERN.search(sentence):
        return "ranking", trend_direction, comparator

    if trend_direction:
        return "trend", trend_direction, comparator

    if comparator:
        return "comparison", trend_direction, comparator

    return "absolute", trend_direction, comparator


def infer_unit(raw_value: str) -> str | None:
    lower = raw_value.lower()

    if "%" in raw_value or "percent" in lower or "percentage" in lower:
        return "percent"
    if re.search(r"[$€£৳]|USD|BDT|Tk\.?", raw_value, re.IGNORECASE):
        return "currency"
    if "billion" in lower:
        return "billion"
    if "million" in lower:
        return "million"
    if "thousand" in lower:
        return "thousand"
    if "ms" in lower:
        return "ms"
    if re.search(r"\bgb\b", lower):
        return "gb"
    if re.search(r"\bmb\b", lower):
        return "mb"
    if re.search(r"\bkb\b", lower):
        return "kb"
    if "epochs" in lower:
        return "epochs"
    if "pixels" in lower or "px" in lower:
        return "pixels"
    if "images" in lower:
        return "images"
    return None


def is_noise_sentence(sentence: str) -> bool:
    sentence = sentence.strip()

    if not sentence:
        return True

    if HEADER_FOOTER_PATTERN.search(sentence):
        return True

    if sentence.lower().startswith("scientific reports"):
        return True

    if "@" in sentence or "doi" in sentence.lower():
        return True

    if SECTION_PATTERN.match(sentence):
        return True

    if SHORT_LABEL_PATTERN.match(sentence):
        return True

    if AFFILIATION_PATTERN.search(sentence) and len(sentence) < 180:
        return True

    if MODEL_TOKEN_PATTERN.search(sentence) and len(sentence.split()) <= 8:
        return True

    return False


def should_skip_token(raw_value: str, sentence: str) -> bool:
    token = raw_value.strip()

    if BAD_REFERENCE_NUMBER_PATTERN.match(token):
        if CITATION_TAIL_PATTERN.search(sentence):
            return True

    if YEAR_PATTERN.match(re.sub(r"[^\d]", "", token)):
        other_numbers = NUMBER_PATTERN.findall(sentence)
        if len(other_numbers) > 1:
            return True

    if token.endswith(",") and len(re.sub(r"[^\d]", "", token)) <= 2:
        return True

    if re.match(r"^\d+\.$", token):
        return True

    if re.search(r"\b(?:0\.5|0\.95)\b", token) and "map@" in sentence.lower():
        return False

    if len(re.sub(r"[^\d]", "", token)) <= 2 and MODEL_TOKEN_PATTERN.search(sentence):
        return True

    return False


def extract_claims_from_page_text(page_number: int, text: str) -> list[ClaimCandidate]:
    claims: list[ClaimCandidate] = []

    for sentence in split_sentences(text):
        if is_noise_sentence(sentence):
            continue

        if not any(ch.isdigit() for ch in sentence):
            continue

        matches = list(NUMBER_PATTERN.finditer(sentence))
        if not matches:
            continue

        kept = []
        for match in matches:
            raw_value = match.group("token").strip()
            if not raw_value:
                continue
            if should_skip_token(raw_value, sentence):
                continue
            kept.append(raw_value)

        if not kept:
            continue

        for raw_value in kept:
            claim_type, trend_direction, comparator = infer_claim_type(sentence, raw_value)
            numeric_value = normalize_numeric_value(raw_value)
            unit = infer_unit(raw_value)

            if unit is None and len(re.sub(r"[^\d]", "", raw_value)) <= 2:
                continue

            confidence = 0.55
            if claim_type in {"percentage", "currency"}:
                confidence = 0.78
            elif claim_type in {"trend", "comparison", "ranking"}:
                confidence = 0.68

            claims.append(
                ClaimCandidate(
                    claim_id=uuid4().hex,
                    page_number=page_number,
                    sentence_text=sentence,
                    claim_type=claim_type,
                    raw_value=raw_value,
                    numeric_value=numeric_value,
                    unit=unit,
                    trend_direction=trend_direction,
                    comparator=comparator,
                    confidence=confidence,
                )
            )

    return claims


def extract_claims_from_resolved_pages(resolved_pages: list) -> list[ClaimCandidate]:
    all_claims: list[ClaimCandidate] = []

    for page in resolved_pages:
        page_claims = extract_claims_from_page_text(
            page_number=page.page_number,
            text=page.text,
        )
        all_claims.extend(page_claims)

    return all_claims