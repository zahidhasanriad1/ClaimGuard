# ClaimGuard
ClaimGuard, A Multimodal Agent for Verifying Numerical Claims Against Charts, Tables, and Reports.
# Three layers are there:
1. orchestration layer
2. document understanding layer
3. verification layer
Workflow: Upload PDF or report → PyMuPDF parse → PaddleOCR fallback for scanned pages → Gemini দিয়ে claim extraction plus evidence extraction → Python deterministic math verifier → LangGraph review loop → React UI with evidence highlight
