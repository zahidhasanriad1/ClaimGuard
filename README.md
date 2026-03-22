# 🛡️ ClaimGuard: Document Intelligence System

[](https://fastapi.tiangolo.com/)
[](https://angular.io/)
[](https://github.com/langchain-ai/langgraph)
[](https://opensource.org/licenses/MIT)

**ClaimGuard** is an automated document intelligence system designed to verify numerical claims within PDF documents. By processing reports, research papers, and financial statements, it checks whether written assertions (percentages, metrics, growth values) are supported by evidence found within the same document.

-----

## 📖 Overview

Manual validation of numerical statements in technical documents is slow and error-prone. ClaimGuard addresses this with an end-to-end verification pipeline that classifies claims into three categories:

  * ✅ **Supported:** The claim is backed by related evidence in the document.
  * ❌ **Contradicted:** The numerical value in the claim conflicts with found evidence.
  * ⚠️ **Insufficient:** No reliable evidence was found to confirm or reject the claim.

-----

## ⚙️ How It Works

The system follows a multi-stage automated pipeline:

1.  **Ingestion:** Native PDF parsing using PyMuPDF with an **OCR Fallback** (PaddleOCR) for scanned pages.
2.  **Table Extraction:** Detection and conversion of structured tables into searchable row-based records.
3.  **Claim Extraction:** Dual-mode extraction (Rule-based or **Gemini Pro**) focusing on currencies, percentages, and trends.
4.  **Verification (LangGraph):** A state-machine-based workflow involving:
      * `load_document` → `extract_claims` → `verify_claims` → `finalize_response`.
5.  **Evidence Linking:** Matching claims to sentences or table rows using numerical similarity and unit compatibility.

-----

## 🛠️ Tech Stack

| Category | Technology |
| :--- | :--- |
| **Backend** | Python 3.11+, FastAPI, Pydantic V2 |
| **AI / Orchestration** | LangGraph, Google Gemini API |
| **Document Processing** | PyMuPDF (fitz), PaddleOCR |
| **Frontend** | Angular 17+, Tailwind CSS |
| **Storage** | Local file-based caching (JSON/Images) |

-----

## 📂 Project Structure

```text
ClaimGuard/
├── app/
│   ├── api/routes/       # FastAPI endpoints (Ingest, Claims, Verify)
│   ├── core/             # Configuration, logging, and constants
│   ├── graph/            # LangGraph state machine and node logic
│   ├── ocr/              # PaddleOCR integration and image processing
│   ├── parsers/          # Native PDF and Table extraction engines
│   ├── schemas/          # Pydantic models for data validation
│   ├── services/         # Business logic and AI extraction services
│   ├── storage/          # Local persistence and cache management
│   └── main.py           # Application entry point
├── data/                 # Data Persistence Layer
│   ├── raw/              # Uploaded PDF files
│   ├── pages/            # Rendered page images for OCR
│   ├── parsed/           # Structured JSON cache
│   └── exports/          # Generated CSV/JSON reports
├── frontend-angular/     # Angular workspace
└── tests/                # Unit and integration tests
```

-----

## 🚀 Installation

### 1\. Backend Setup

```bash
# Create and activate virtual environment
python -m venv .venv
.venv\Scripts\activate  # On Linux/Mac: source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Start the server
uvicorn app.main:app --reload
```

### 2\. Frontend Setup

```bash
cd frontend-angular
npm install
ng serve
```

Access the dashboard at `http://localhost:4200`.

### 3\. Environment Variables

Create a `.env` file in the root directory:

```env
APP_NAME=ClaimGuard
GEMINI_API_KEY=your_gemini_api_key
OCR_ENABLED=true
RAW_DOCS_DIR=data/raw
PARSED_DOCS_DIR=data/parsed
```

-----

## 🔌 API Endpoints

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `GET` | `/health` | Check if the service is running. |
| `POST` | `/ingest/upload` | Upload a PDF and trigger parsing. |
| `GET` | `/claims/{id}` | Extract claims (Params: `mode=rule/gemini`). |
| `GET` | `/verify/{id}` | Run the LangGraph verification pipeline. |
| `POST` | `/exports/{id}/csv` | Generate and download a CSV report. |

-----

## 🎯 Scope & Future Work

  * **Current Scope:** Best for text-based numerical claims and structured PDF tables.
  * **Limitations:** Chart-based verification and image-based table detection are in development.
  * **Future Work:** Implementing a reviewer workflow for manual validation and stronger contradiction reasoning.

-----

## 🌟 Why This Project Matters

ClaimGuard demonstrates an industrial-grade approach to AI Engineering. It combines document parsing, OCR, stateful graph orchestration (LangGraph), and a modern web interface to solve real-world data integrity problems. It is designed for high-stakes environments like research auditing and financial reporting.

Would you like me to generate a **`.gitignore`** file to help keep your `data/` and `.venv/` folders out of your repository?