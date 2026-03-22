from typing import TypedDict

from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import InMemorySaver

from app.schemas.claim import ClaimCandidate
from app.schemas.document import UploadResponse
from app.schemas.verification import VerificationResponse
from app.services.claim_extractor import extract_claims_from_resolved_pages
from app.services.claim_postprocessor import deduplicate_claims, prioritize_claims
from app.services.claim_verifier import verify_claims_against_resolved_pages
from app.services.gemini_claim_extractor import extract_claims_with_gemini
from app.storage.claim_store import claim_cache_exists, load_claims, save_claims
from app.storage.document_store import load_upload_response
from app.storage.verification_store import save_verification


class ClaimGuardGraphState(TypedDict, total=False):
    document_id: str
    mode: str
    max_claims: int
    use_tables: bool
    include_results: bool
    use_cache: bool
    refresh: bool
    payload: UploadResponse
    claims: list[ClaimCandidate]
    full_verification_payload: VerificationResponse
    verification_payload: VerificationResponse


def load_document_node(state: ClaimGuardGraphState) -> ClaimGuardGraphState:
    document_id = state["document_id"]
    payload = load_upload_response(document_id)
    return {"payload": payload}


def extract_claims_node(state: ClaimGuardGraphState) -> ClaimGuardGraphState:
    payload = state["payload"]
    document_id = state["document_id"]
    mode = state.get("mode", "rule")
    max_claims = state.get("max_claims", 100)
    use_cache = state.get("use_cache", True)
    refresh = state.get("refresh", False)

    if use_cache and not refresh and claim_cache_exists(document_id, mode):
        claims = load_claims(document_id, mode)
    else:
        if mode == "gemini":
            claims = extract_claims_with_gemini(payload.metadata.resolved_pages)
        else:
            claims = extract_claims_from_resolved_pages(payload.metadata.resolved_pages)

        claims = deduplicate_claims(claims)
        save_claims(document_id, mode, claims)

    claims = deduplicate_claims(claims)
    claims = prioritize_claims(claims, max_claims=max_claims)

    return {"claims": claims}


def verify_claims_node(state: ClaimGuardGraphState) -> ClaimGuardGraphState:
    payload = state["payload"]
    claims = state["claims"]
    document_id = state["document_id"]
    mode = state.get("mode", "rule")
    use_tables = state.get("use_tables", False)

    results = verify_claims_against_resolved_pages(
        claims=claims,
        resolved_pages=payload.metadata.resolved_pages,
        extracted_tables=payload.metadata.extracted_tables,
        use_tables=use_tables,
    )

    supported = sum(1 for item in results if item.verdict == "supported")
    contradicted = sum(1 for item in results if item.verdict == "contradicted")
    insufficient = sum(1 for item in results if item.verdict == "insufficient")

    full_payload = VerificationResponse(
        document_id=document_id,
        total_claims=len(results),
        supported=supported,
        contradicted=contradicted,
        insufficient=insufficient,
        results=results,
    )

    save_verification(document_id, mode, full_payload)

    return {"full_verification_payload": full_payload}


def finalize_response_node(state: ClaimGuardGraphState) -> ClaimGuardGraphState:
    include_results = state.get("include_results", False)
    full_payload = state["full_verification_payload"]

    public_payload = VerificationResponse(
        document_id=full_payload.document_id,
        total_claims=full_payload.total_claims,
        supported=full_payload.supported,
        contradicted=full_payload.contradicted,
        insufficient=full_payload.insufficient,
        results=full_payload.results if include_results else [],
    )

    return {"verification_payload": public_payload}


def build_verification_graph():
    workflow = StateGraph(ClaimGuardGraphState)

    workflow.add_node("load_document", load_document_node)
    workflow.add_node("extract_claims", extract_claims_node)
    workflow.add_node("verify_claims", verify_claims_node)
    workflow.add_node("finalize_response", finalize_response_node)

    workflow.add_edge(START, "load_document")
    workflow.add_edge("load_document", "extract_claims")
    workflow.add_edge("extract_claims", "verify_claims")
    workflow.add_edge("verify_claims", "finalize_response")
    workflow.add_edge("finalize_response", END)

    checkpointer = InMemorySaver()
    return workflow.compile(checkpointer=checkpointer)


VERIFICATION_GRAPH = build_verification_graph()


def run_verification_graph(
    document_id: str,
    mode: str = "rule",
    max_claims: int = 100,
    use_tables: bool = False,
    include_results: bool = False,
    use_cache: bool = True,
    refresh: bool = False,
) -> VerificationResponse:
    initial_state: ClaimGuardGraphState = {
        "document_id": document_id,
        "mode": mode,
        "max_claims": max_claims,
        "use_tables": use_tables,
        "include_results": include_results,
        "use_cache": use_cache,
        "refresh": refresh,
    }

    thread_id = f"{document_id}_{mode}_{max_claims}_{int(use_tables)}"

    result = VERIFICATION_GRAPH.invoke(
        initial_state,
        config={"configurable": {"thread_id": thread_id}},
    )

    return result["verification_payload"]