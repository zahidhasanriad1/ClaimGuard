This is a professional, high-impact `README.md` tailored for your **ClaimGuard** project. It is structured to appeal to recruiters and technical collaborators by highlighting the engineering complexity and the value of the AI pipeline.

-----

# 🛡️ ClaimGuard: Document Intelligence & Claim Verification

[](https://fastapi.tiangolo.com/)
[](https://angular.io/)
[](https://github.com/langchain-ai/langgraph)
[](https://ai.google.dev/)

**ClaimGuard** is a sophisticated document intelligence system designed to verify numerical claims within PDF documents. It processes complex reports, research papers, and business documents to determine if written assertions (percentages, metrics, growth values) are accurately supported by evidence found within the same file.

The system automates the journey from raw PDF ingestion to a verified audit trail, leveraging a state-of-the-art **LangGraph** orchestration and **Gemini Pro** for semantic reasoning.

-----

## 📸 Screenshots

### Login Interface

### Professional Dashboard

-----

## 📖 Overview

Manual validation of numerical statements in technical documents is slow and prone to human error. **ClaimGuard** addresses this through an end-to-end automated verification pipeline. It reads a PDF, extracts page-level text, applies OCR when necessary, identifies numerical claims, and searches for matching evidence to classify each claim as:

  * ✅ **Supported:** The claim is backed by related evidence in the document.
  * ❌ **Contradicted:** The numerical value in the claim conflicts with found evidence.
  * ⚠️ **Insufficient:** No reliable evidence was found to confirm or reject the claim.

-----

## ⚙️ How It Works: The Pipeline

### 1\. Hybrid Document Ingestion

  * **Native Parsing:** Uses PyMuPDF for fast, accurate machine-readable text extraction.
  * **OCR Fallback:** Automatically triggers **PaddleOCR** if a page is identified as scan-like or lacks native text.
  * **Page Rendering:** Converts pages to images for visual analysis and OCR processing.

### 2\. Intelligent Feature Extraction

  * **Table Extraction:** Detects structured tables and converts them into searchable row-based records.
  * **Claim Extraction:** Supports **Rule-based** (Regex) and **Gemini-based** modes to identify percentages, currency, trends, and comparisons while filtering noise (citations, affiliations, etc.).

### 3\. Agentic Verification (LangGraph)

The verification stage is orchestrated by a LangGraph state machine with the following nodes:
`load_document` ➔ `extract_claims` ➔ `verify_claims` ➔ `finalize_response`

### 4\. Evidence Linking & Scoring

Claims are checked against candidate evidence using:

  * Keyword overlap & page relevance
  * Numerical similarity & unit compatibility
  * Confidence scoring for transparent evidence matching

-----

## 🛠️ Tech Stack

| Category | Technology |
| :--- | :--- |
| **Backend** | Python 3.11+, FastAPI, Pydantic |
| **Orchestration** | **LangGraph** (Stateful Multi-Agent Workflows) |
| **AI Models** | **Google Gemini API** (Pro/Flash) |
| **Document Processing** | PyMuPDF (fitz), PaddleOCR |
| **Frontend** | **Angular 21+** (Reactive Dashboard) |
| **Storage** | Local file-based caching (JSON, CSV, Images) |

-----

## 📂 Project Structure

```text
ClaimGuard/
├── app/
│   ├── api/routes/       # FastAPI controllers & endpoint definitions
│   ├── core/             # Global configurations & app security
│   ├── graph/            # LangGraph workflow nodes & state definitions
│   ├── ocr/              # PaddleOCR logic & image preprocessing
│   ├── parsers/          # Native PDF & Table extraction engines
│   ├── schemas/          # Pydantic data models for validation
│   ├── services/         # Business logic & AI orchestration
│   ├── storage/          # Local persistence & cache management
│   └── main.py           # Application entry point
├── data/                 # Data Persistence Layer (Raw, Pages, Parsed, Exports)
├── ClaimGurdUI/          # Angular 21 Frontend source code
├── docs/                 # Documentation & architectural images
└── README.md
```

-----

## 🚀 Getting Started

### Backend Setup

1.  **Environment:** Create and activate a virtual environment.
    ```bash
    python -m venv .venv
    source .venv/bin/activate  # Windows: .venv\Scripts\activate
    ```
2.  **Dependencies:** Install required packages.
    ```bash
    pip install -r requirements.txt
    ```
3.  **Environment Variables:** Create a `.env` file in the root.
    ```env
    GEMINI_API_KEY=your_api_key
    OCR_ENABLED=true
    RAW_DOCS_DIR=data/raw
    PAGES_DIR=data/pages
    PARSED_DOCS_DIR=data/parsed
    EXPORTS_DIR=data/exports
    ```
4.  **Run:**
    ```bash
    uvicorn app.main:app --reload
    ```

### Frontend Setup

1.  **Navigate:** `cd ClaimGurdUI`
2.  **Install:** `npm install`
3.  **Run:** `npm start`
4.  **Access:** `http://localhost:4200`

-----

## 📊 Current Scope & Future Work

### Current Capabilities

  * Text-based numerical claims.
  * Nearby sentence-level evidence.
  * Basic table row evidence for structured PDF documents.
  * JSON & CSV export for research review.

### Limitations & Roadmap

  * 🔜 **Chart-based Verification:** Extracting evidence from visual charts.
  * 🔜 **Vision-Table Extraction:** Handling image-based/complex nested tables.
  * 🔜 **Human-in-the-loop:** Reviewer workflow for manual validation.
  * 🔜 **Full Graph Pipeline:** Moving ingestion and parsing entirely into the LangGraph state.

-----

## 🌟 Why This Project Matters

**ClaimGuard** is more than a PDF reader; it is a full-scale AI system. It demonstrates a mastery of:

  * **AI Engineering:** Designing complex agentic workflows with LangGraph.
  * **Document Intelligence:** Navigating the complexities of OCR and unstructured PDF data.
  * **Applied ML:** Utilizing LLMs (Gemini) for high-precision semantic verification.
  * **System Design:** Connecting a high-speed Python backend with a robust Angular frontend.

-----
