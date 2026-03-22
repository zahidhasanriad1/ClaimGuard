import re

from app.schemas.claim import ClaimCandidate
from app.schemas.verification import ClaimVerificationResult, EvidenceMatch
from app.services.claim_extractor import NUMBER_PATTERN, normalize_numeric_value, split_sentences

STOPWORDS = {
    "the",
    "a",
    "an",
    "and",
    "or",
    "of",
    "in",
    "on",
    "at",
    "to",
    "for",
    "by",
    "with",
    "from",
    "that",
    "this",
    "is",
    "was",
    "were",
    "are",
    "be",
    "as",
    "it",
    "its",
    "than",
    "into",
    "over",
    "under",
    "after",
    "before",
    "during",
    "between",
    "quarter",
    "report",
    "page",
    "year",
    "table",
    "figure",
}


def tokenize_keywords(text: str) -> set[str]:
    tokens = re.findall(r"[A-Za-z]+", (text or "").lower())
    return {token for token in tokens if len(token) >= 3 and token not in STOPWORDS}


def extract_numbers_from_text(text: str) -> list[str]:
    return [match.group("token").strip() for match in NUMBER_PATTERN.finditer(text)]


def values_match(claim_value: float | None, candidate_value: float | None) -> bool:
    if claim_value is None or candidate_value is None:
        return False

    if claim_value == candidate_value:
        return True

    diff = abs(claim_value - candidate_value)

    if claim_value == 0:
        return diff <= 0.1

    relative_diff = diff / abs(claim_value)
    return relative_diff <= 0.01


def infer_candidate_units(raw_numbers: list[str]) -> set[str]:
    units: set[str] = set()

    for raw in raw_numbers:
        text = raw.lower()

        if "%" in raw or "percent" in text or "percentage" in text:
            units.add("percent")
        elif any(sym in raw for sym in ["$", "€", "£", "৳"]) or "usd" in text or "bdt" in text or "tk" in text:
            units.add("currency")
        elif "billion" in text:
            units.add("billion")
        elif "million" in text:
            units.add("million")
        elif "thousand" in text:
            units.add("thousand")
        elif "ms" in text:
            units.add("ms")
        elif "epochs" in text:
            units.add("epochs")
        elif "images" in text:
            units.add("images")
        elif "px" in text or "pixels" in text:
            units.add("pixels")

    return units


def units_are_compatible(claim_unit: str | None, candidate_units: set[str]) -> bool:
    if claim_unit is None:
        return True

    if not candidate_units:
        return False

    if claim_unit in candidate_units:
        return True

    numeric_scale_group = {"billion", "million", "thousand"}
    if claim_unit in numeric_scale_group and candidate_units.intersection(numeric_scale_group):
        return True

    return False


def build_sentence_index_by_page(resolved_pages: list) -> dict[int, list[dict]]:
    index: dict[int, list[dict]] = {}

    for page in resolved_pages:
        page_items: list[dict] = []
        for sentence in split_sentences(page.text):
            page_items.append(
                {
                    "source_type": "text",
                    "page_number": page.page_number,
                    "sentence_text": sentence,
                    "keywords": tokenize_keywords(sentence),
                    "raw_numbers": extract_numbers_from_text(sentence),
                }
            )
        index[page.page_number] = page_items

    return index


def build_table_index_by_page(extracted_tables: list) -> dict[int, list[dict]]:
    index: dict[int, list[dict]] = {}

    for row in extracted_tables:
        index.setdefault(row.page_number, []).append(
            {
                "source_type": "table",
                "page_number": row.page_number,
                "table_index": row.table_index,
                "row_index": row.row_index,
                "row_text": row.row_text,
                "keywords": tokenize_keywords(row.row_text),
                "raw_numbers": extract_numbers_from_text(row.row_text),
            }
        )

    return index


def keyword_overlap_score(claim_keywords: set[str], candidate_keywords: set[str]) -> tuple[float, list[str]]:
    overlap = sorted(claim_keywords.intersection(candidate_keywords))
    if not claim_keywords:
        return 0.0, overlap
    return len(overlap) / len(claim_keywords), overlap


def evaluate_numbers(
    claim_value: float | None,
    claim_unit: str | None,
    candidate_raw_numbers: list[str],
) -> tuple[bool, bool]:
    if claim_value is None:
        return False, False

    candidate_units = infer_candidate_units(candidate_raw_numbers)

    if not units_are_compatible(claim_unit, candidate_units):
        return False, False

    for raw_number in candidate_raw_numbers:
        candidate_value = normalize_numeric_value(raw_number)
        if values_match(claim_value, candidate_value):
            return True, False

    if candidate_raw_numbers:
        if len(candidate_raw_numbers) > 3:
            return False, False
        return False, True

    return False, False


def build_text_evidence(item: dict, overlap: list[str], score: float) -> EvidenceMatch:
    return EvidenceMatch(
        source_type="text",
        page_number=item["page_number"],
        sentence_text=item["sentence_text"],
        raw_numbers=item["raw_numbers"],
        keyword_overlap=overlap,
        score=score,
        table_index=None,
        row_index=None,
        row_text=None,
    )


def build_table_evidence(item: dict, overlap: list[str], score: float) -> EvidenceMatch:
    return EvidenceMatch(
        source_type="table",
        page_number=item["page_number"],
        sentence_text="",
        raw_numbers=item["raw_numbers"],
        keyword_overlap=overlap,
        score=score,
        table_index=item["table_index"],
        row_index=item["row_index"],
        row_text=item["row_text"],
    )


def shortlist_candidates(
    claim_keywords: set[str],
    candidates: list[dict],
    top_k: int = 10,
) -> list[tuple[dict, float, list[str]]]:
    scored: list[tuple[dict, float, list[str]]] = []

    for item in candidates:
        score, overlap = keyword_overlap_score(claim_keywords, item["keywords"])
        if score <= 0:
            continue
        scored.append((item, score, overlap))

    scored.sort(key=lambda x: x[1], reverse=True)
    return scored[:top_k]


def find_best_evidence_for_claim(
    claim: ClaimCandidate,
    sentence_index_by_page: dict[int, list[dict]],
    table_index_by_page: dict[int, list[dict]],
    use_tables: bool = False,
) -> tuple[str, float, EvidenceMatch | None, list[str]]:
    claim_keywords = tokenize_keywords(claim.sentence_text)
    claim_page = claim.page_number

    best_support: tuple[float, EvidenceMatch, list[str]] | None = None
    best_contradiction: tuple[float, EvidenceMatch, list[str]] | None = None
    self_sentence_match: EvidenceMatch | None = None

    sentence_candidates = sentence_index_by_page.get(claim_page, [])
    for item, score, overlap in shortlist_candidates(claim_keywords, sentence_candidates, top_k=10):
        evidence = build_text_evidence(item, overlap, score)

        if item["sentence_text"] == claim.sentence_text:
            self_sentence_match = evidence
            continue

        has_match, has_conflict = evaluate_numbers(
            claim.numeric_value,
            claim.unit,
            item["raw_numbers"],
        )

        if has_match:
            weighted_score = score + 0.35
            notes = ["Matched related text evidence with similar numeric value."]
            if best_support is None or weighted_score > best_support[0]:
                best_support = (min(weighted_score, 0.92), evidence, notes)

        elif has_conflict and score >= 0.55:
            weighted_score = score + 0.12
            notes = ["Found strongly related text evidence with different numeric value."]
            if best_contradiction is None or weighted_score > best_contradiction[0]:
                best_contradiction = (min(weighted_score, 0.72), evidence, notes)

    if use_tables:
        table_candidates = table_index_by_page.get(claim_page, [])
        for item, score, overlap in shortlist_candidates(claim_keywords, table_candidates, top_k=8):
            evidence = build_table_evidence(item, overlap, score)

            has_match, has_conflict = evaluate_numbers(
                claim.numeric_value,
                claim.unit,
                item["raw_numbers"],
            )

            if has_match:
                weighted_score = max(score, 0.25) + 0.45
                notes = ["Matched table row evidence with similar numeric value."]
                if best_support is None or weighted_score > best_support[0]:
                    best_support = (min(weighted_score, 0.95), evidence, notes)

            elif has_conflict and score >= 0.50:
                weighted_score = max(score, 0.20) + 0.15
                notes = ["Found strongly related table row evidence with different numeric value."]
                if best_contradiction is None or weighted_score > best_contradiction[0]:
                    best_contradiction = (min(weighted_score, 0.74), evidence, notes)

    if best_support is not None:
        return "supported", best_support[0], best_support[1], best_support[2]

    if best_contradiction is not None:
        return "contradicted", best_contradiction[0], best_contradiction[1], best_contradiction[2]

    if self_sentence_match is not None:
        return "insufficient", 0.30, self_sentence_match, [
            "Only direct claim sentence found. Independent supporting evidence not found yet."
        ]

    return "insufficient", 0.20, None, [
        "No sufficiently related evidence found on the same page."
    ]


def verify_claims_against_resolved_pages(
    claims: list[ClaimCandidate],
    resolved_pages: list,
    extracted_tables: list,
    use_tables: bool = False,
) -> list[ClaimVerificationResult]:
    sentence_index_by_page = build_sentence_index_by_page(resolved_pages)
    table_index_by_page = build_table_index_by_page(extracted_tables) if use_tables else {}

    results: list[ClaimVerificationResult] = []

    for claim in claims:
        verdict, confidence, matched_evidence, notes = find_best_evidence_for_claim(
            claim=claim,
            sentence_index_by_page=sentence_index_by_page,
            table_index_by_page=table_index_by_page,
            use_tables=use_tables,
        )

        results.append(
            ClaimVerificationResult(
                claim_id=claim.claim_id,
                claim_page_number=claim.page_number,
                claim_text=claim.sentence_text,
                claim_type=claim.claim_type,
                raw_value=claim.raw_value,
                numeric_value=claim.numeric_value,
                verdict=verdict,
                confidence=confidence,
                matched_evidence=matched_evidence,
                notes=notes,
            )
        )

    return results