# ClaimGuard
ClaimGuard is a document intelligence system for verifying numerical claims in PDF files. It analyzes reports, research papers, and other document based files, then checks whether written numerical statements are supported by evidence found in the same document.

The system extracts meaningful claims, finds related evidence from text and tables, assigns a verification verdict, and provides exportable outputs for review.

Overview

Many reports and research documents contain important numerical statements such as percentages, counts, rankings, growth values, financial figures, and performance metrics. These statements are often repeated in summaries, conclusions, or discussion sections. Manual checking is slow and error prone.

ClaimGuard helps solve this problem by building an end to end verification pipeline. It reads a PDF, extracts page level text, applies OCR when needed, identifies numerical claims, searches for matching evidence, and classifies each claim as supported, contradicted, or insufficient.

Key Features
PDF upload and document ingestion
Native PDF text extraction
OCR fallback for scan like pages
Page image rendering for later visual analysis
Resolved page text selection between native text and OCR text
Numerical claim extraction in rule based mode and Gemini based mode
Claim cleanup through deduplication and prioritization
Evidence retrieval from text and table rows
Claim verification with transparent evidence matching
Result caching for faster repeated runs
JSON and CSV export support
Frontend dashboard for upload, verification, and export
Working Process
1. Document Ingestion

The process begins when a user uploads a PDF file through the API or the frontend. The uploaded file is stored in the project data directory for later processing.

2. Native PDF Parsing

The system reads the PDF using a native parser. It extracts document metadata, page count, page previews, and the full text of each page. This is the first choice because native text is usually more accurate and faster than OCR.

3. Page Rendering

Every page is converted into an image and stored locally. These page images support OCR fallback and future visual modules such as chart analysis.

4. OCR Fallback

When a page contains very little machine readable text, ClaimGuard marks it as scan like and runs OCR on the page image. This improves reliability for scanned PDFs and image based documents.

5. Final Page Text Resolution

For each page, the system decides which source should be used as the final page text. It chooses between native PDF text and OCR text. The selected output becomes the resolved page text for the next stages.

6. Table Extraction

ClaimGuard attempts to detect tables directly from the PDF. If tables are found, they are converted into row based records that include page number, table index, row index, headers, values, and row text.

7. Claim Extraction

The system extracts meaningful numerical claims from the resolved page text. Two modes are supported.

Rule based mode uses patterns and filters.

Gemini based mode uses a language model for cleaner and more contextual extraction.

The extractor focuses on claims related to percentages, counts, currency, rankings, trends, and comparisons.

8. Claim Post Processing

After extraction, claims are cleaned before verification. The system removes weak claims, filters obvious noise, merges duplicates, and prioritizes stronger claims. This improves both speed and result quality.

9. Evidence Indexing

ClaimGuard builds searchable evidence structures from page text sentences and extracted table rows. These structures are grouped by page so the verifier can focus on relevant nearby evidence.

10. Claim Verification

Each claim is checked against candidate evidence using keyword overlap, page relevance, numerical similarity, and unit compatibility. The verifier assigns one of three verdicts.

Supported

Contradicted

Insufficient

11. Evidence Linking

For every verified claim, the system stores the strongest evidence match. Evidence may come from a sentence or a table row. The result includes page number, evidence text, confidence score, and notes.

12. Caching

To avoid repeated work, ClaimGuard caches extracted claims and verification results. Reprocessing the same document becomes much faster, especially in Gemini mode.

13. Export

Results can be exported as summary JSON, full verification JSON, and CSV. This makes the output easy to inspect, share, and reuse in research or reporting workflows.

14. Frontend Review

The frontend provides a simple review interface where users can upload PDFs, select processed documents, run verification, inspect results, and export files.

Verification Labels

ClaimGuard currently uses three output labels.

Supported
The claim is backed by related evidence in the document.
Contradicted
The claim is strongly related to nearby evidence, but the numerical value conflicts with that evidence.
Insufficient
The system cannot find enough reliable evidence to confirm or reject the claim.
Tech Stack
Backend

Python, FastAPI, PyMuPDF, PaddleOCR, Gemini API, Pydantic

Frontend

Angular

Storage

Local file based storage for uploaded files, parsed documents, cached claims, cached verification results, and exports
ClaimGuard, A Multimodal Agent for Verifying Numerical Claims Against Charts, Tables, and Reports.
# Three layers are there:
1. orchestration layer
2. document understanding layer
3. verification layer

# Workflow: 
Upload PDF or report → PyMuPDF parse → PaddleOCR fallback for scanned pages → Gemini দিয়ে claim extraction plus evidence extraction → Python deterministic math verifier → LangGraph review loop → React UI with evidence highlight

# Folder Structure:
```` ClaimGuard/
  app/
    api/
      routes/
    core/
    ocr/
    parsers/
    schemas/
    services/
    storage/
    main.py
  data/
    raw/
    pages/
    parsed/
    exports/
  frontend-angular/
  
API Endpoints
Document Ingestion

POST /ingest/upload

Uploads a PDF and starts parsing.

Documents

GET /documents

Returns the list of processed documents.

Claim Extraction

GET /claims/{document_id}

Extracts claims from a processed document.

Query parameters:
mode=rule|gemini
max_claims=...

Verification

GET /verify/{document_id}

Verifies extracted claims against document evidence.

Query parameters:
mode=rule|gemini
max_claims=...
include_results=true|false
use_tables=true|false

Tables

GET /tables/{document_id}

Returns extracted table rows from the PDF.

Exports

POST /exports/{document_id}/summary

Exports a summary JSON.

POST /exports/{document_id}/verification-json

Exports detailed verification results in JSON.

POST /exports/{document_id}/verification-csv

Exports detailed verification results in CSV.

Installation
Backend

# Create and activate a virtual environment, then install dependencies.            # Research, EDA, and prototyping


1. python -m venv .venv
2. .venv\Scripts\activate
3. python -m pip install --upgrade pip
4. make requirments.txt
5. install requirments.txt
6. pip install -U langgraph
7. uvicorn app.main:app --reload