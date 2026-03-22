import re

from app.schemas.claim import ClaimCandidate
from app.schemas.verification import (
    ClaimVerificationResult,
    EvidenceMatch,
)
from app.services.claim_extractor import (
    NUMBER_PATTERN,
    normalize_numeric_value,
    split_sentences,
)

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
    return {
        token
        for token in tokens
        if len(token) >= 3 and token not in STOPWORDS
    }


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


def build_sentence_index(resolved_pages: list) -> list[dict]:
    index: list[dict] = []

    for page in resolved_pages:
        sentences = split_sentences(page.text)
        for sentence in sentences:
            index.append(
                {
                    "source_type": "text",
                    "page_number": page.page_number,
                    "sentence_text": sentence,
                    "keywords": tokenize_keywords(sentence),
                    "raw_numbers": extract_numbers_from_text(sentence),
                }
            )

    return index


def build_table_index(extracted_tables: list) -> list[dict]:
    index: list[dict] = []

    for row in extracted_tables:
        index.append(
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

    score = len(overlap) / len(claim_keywords)
    return score, overlap


def evaluate_numbers(claim_value: float | None, candidate_raw_numbers: list[str]) -> tuple[bool, bool]:
    has_match = False
    has_conflict = False

    if claim_value is None:
        return False, False

    for raw_number in candidate_raw_numbers:
        candidate_value = normalize_numeric_value(raw_number)
        if values_match(claim_value, candidate_value):
            has_match = True
            break

    if not has_match and candidate_raw_numbers:
        has_conflict = True

    return has_match, has_conflict


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


def find_best_evidence_for_claim(
    claim: ClaimCandidate,
    sentence_index: list[dict],
    table_index: list[dict],
) -> tuple[str, float, EvidenceMatch | None, list[str]]:
    claim_keywords = tokenize_keywords(claim.sentence_text)
    claim_page = claim.page_number

    best_support: tuple[float, EvidenceMatch, list[str]] | None = None
    best_contradiction: tuple[float, EvidenceMatch, list[str]] | None = None
    self_sentence_match: EvidenceMatch | None = None

    for item in sentence_index:
        candidate_page = item["page_number"]
        if abs(candidate_page - claim_page) > 1:
            continue

        score, overlap = keyword_overlap_score(claim_keywords, item["keywords"])
        if score <= 0:
            continue

        evidence = build_text_evidence(item, overlap, score)

        if item["sentence_text"] == claim.sentence_text:
            self_sentence_match = evidence
            continue

        has_match, has_conflict = evaluate_numbers(claim.numeric_value, item["raw_numbers"])

        if has_match:
            weighted_score = score + 0.30
            if candidate_page == claim_page:
                weighted_score += 0.10

            notes = ["Matched related text evidence with similar numeric value."]
            if best_support is None or weighted_score > best_support[0]:
                best_support = (min(weighted_score, 0.92), evidence, notes)

        elif has_conflict and score >= 0.25:
            weighted_score = score + 0.15
            if candidate_page == claim_page:
                weighted_score += 0.05

            notes = ["Found related text evidence with different numeric value."]
            if best_contradiction is None or weighted_score > best_contradiction[0]:
                best_contradiction = (min(weighted_score, 0.82), evidence, notes)

    for item in table_index:
        candidate_page = item["page_number"]
        if abs(candidate_page - claim_page) > 1:
            continue

        score, overlap = keyword_overlap_score(claim_keywords, item["keywords"])
        has_match, has_conflict = evaluate_numbers(claim.numeric_value, item["raw_numbers"])

        if score <= 0 and not has_match:
            continue

        evidence = build_table_evidence(item, overlap, score)

        if has_match:
            weighted_score = max(score, 0.25) + 0.45
            if candidate_page == claim_page:
                weighted_score += 0.10

            notes = ["Matched table row evidence with similar numeric value."]
            if best_support is None or weighted_score > best_support[0]:
                best_support = (min(weighted_score, 0.95), evidence, notes)

        elif has_conflict and (score >= 0.15 or candidate_page == claim_page):
            weighted_score = max(score, 0.20) + 0.25
            if candidate_page == claim_page:
                weighted_score += 0.05

            notes = ["Found table row evidence with different numeric value."]
            if best_contradiction is None or weighted_score > best_contradiction[0]:
                best_contradiction = (min(weighted_score, 0.86), evidence, notes)

    if best_support is not None:
        return "supported", best_support[0], best_support[1], best_support[2]

    if best_contradiction is not None:
        return "contradicted", best_contradiction[0], best_contradiction[1], best_contradiction[2]

    if self_sentence_match is not None:
        return "insufficient", 0.30, self_sentence_match, [
            "Only direct claim sentence found. Independent supporting evidence not found yet."
        ]

    return "insufficient", 0.20, None, [
        "No sufficiently related evidence sentence or table row found in current page window."
    ]


def verify_claims_against_resolved_pages(
    claims: list[ClaimCandidate],
    resolved_pages: list,
    extracted_tables: list,
) -> list[ClaimVerificationResult]:
    sentence_index = build_sentence_index(resolved_pages)
    table_index = build_table_index(extracted_tables)

    results: list[ClaimVerificationResult] = []

    for claim in claims:
        verdict, confidence, matched_evidence, notes = find_best_evidence_for_claim(
            claim=claim,
            sentence_index=sentence_index,
            table_index=table_index,
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