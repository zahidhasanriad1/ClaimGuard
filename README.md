# ClaimGuard
ClaimGuard, A Multimodal Agent for Verifying Numerical Claims Against Charts, Tables, and Reports.
# Three layers are there:
1. orchestration layer
2. document understanding layer
3. verification layer

# Workflow: 
Upload PDF or report → PyMuPDF parse → PaddleOCR fallback for scanned pages → Gemini দিয়ে claim extraction plus evidence extraction → Python deterministic math verifier → LangGraph review loop → React UI with evidence highlight

# Folder Structure:
```` claimguard/
├── app/                  # Main application logic
│   ├── api/              # REST/GraphQL endpoints (FastAPI/Flask)
│   ├── graph/            # LangGraph or state machine orchestration
│   ├── agents/           # LLM-based autonomous agents
│   ├── parsers/          # Logic for structured data conversion
│   ├── ocr/              # Optical Character Recognition processing
│   ├── extractors/       # Entity and data extraction logic
│   ├── verifier/         # Rules engines and cross-referencing
│   ├── schemas/          # Pydantic models and data validation
│   ├── storage/          # Database connectors (Vector, SQL, NoSQL)
│   └── ui_hooks/         # Backend-to-Frontend communication triggers
├── data/                 # Data persistence layer
│   ├── raw/              # Unprocessed input files (PDFs, Images)
│   ├── parsed/           # Intermediate structured data
│   ├── evidence/         # External documentation for verification
│   └── eval/             # Benchmarking datasets for evaluation
├── frontend/             # User interface (React, Next.js, or Streamlit)
├── tests/                # Unit, integration, and E2E tests
└── notebooks/            # Research, EDA, and prototyping
