from app.schemas.claim import ClaimCandidate


def normalize_sentence(text: str) -> str:
    return " ".join((text or "").lower().split())


def normalize_raw_value(text: str) -> str:
    return " ".join((text or "").lower().split())


def is_low_value_claim(claim: ClaimCandidate) -> bool:
    sentence = normalize_sentence(claim.sentence_text)
    raw_value = normalize_raw_value(claim.raw_value)

    if len(sentence) < 20:
        return True

    if claim.numeric_value is None and claim.unit is None:
        return True

    digits_only = "".join(ch for ch in raw_value if ch.isdigit())
    if len(digits_only) <= 1 and claim.unit is None:
        return True

    bad_prefixes = (
        "figure ",
        "table ",
        "algorithm ",
        "section ",
    )
    if sentence.startswith(bad_prefixes):
        return True

    return False


def deduplicate_claims(claims: list[ClaimCandidate]) -> list[ClaimCandidate]:
    seen: set[tuple] = set()
    unique_claims: list[ClaimCandidate] = []

    for claim in claims:
        if is_low_value_claim(claim):
            continue

        key = (
            claim.page_number,
            normalize_sentence(claim.sentence_text),
            claim.claim_type,
            normalize_raw_value(claim.raw_value),
        )

        if key in seen:
            continue

        seen.add(key)
        unique_claims.append(claim)

    return unique_claims


def prioritize_claims(claims: list[ClaimCandidate], max_claims: int = 200) -> list[ClaimCandidate]:
    def score(claim: ClaimCandidate) -> tuple[float, int, int]:
        base = claim.confidence

        if claim.claim_type in {"percentage", "currency", "comparison", "trend", "ranking"}:
            base += 0.15

        if claim.unit in {"percent", "currency", "million", "billion", "thousand"}:
            base += 0.10

        sentence_len = len(claim.sentence_text)
        return (base, sentence_len, claim.page_number)

    ranked = sorted(claims, key=score, reverse=True)
    return ranked[:max_claims]