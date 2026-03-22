from pathlib import Path

import pymupdf

from app.schemas.document import ExtractedTableRow


def clean_cell(value) -> str:
    if value is None:
        return ""
    return " ".join(str(value).split()).strip()


def make_default_headers(width: int) -> list[str]:
    return [f"col_{idx}" for idx in range(1, width + 1)]


def build_row_text(headers: list[str], values: list[str]) -> str:
    parts: list[str] = []

    for header, value in zip(headers, values):
        if not value:
            continue
        if header:
            parts.append(f"{header}: {value}")
        else:
            parts.append(value)

    return "; ".join(parts).strip()


def extract_tables_from_pdf(pdf_path: Path) -> list[ExtractedTableRow]:
    extracted_rows: list[ExtractedTableRow] = []

    with pymupdf.open(str(pdf_path)) as doc:
        for page_index in range(len(doc)):
            page = doc.load_page(page_index)

            try:
                finder = page.find_tables()
                tables = getattr(finder, "tables", []) or []
            except Exception:
                tables = []

            for table_idx, table in enumerate(tables, start=1):
                try:
                    raw_rows = table.extract()
                except Exception:
                    continue

                if not raw_rows:
                    continue

                cleaned_rows = [
                    [clean_cell(cell) for cell in row]
                    for row in raw_rows
                ]
                cleaned_rows = [
                    row for row in cleaned_rows
                    if any(cell for cell in row)
                ]

                if not cleaned_rows:
                    continue

                first_row = cleaned_rows[0]
                headers = first_row if len(cleaned_rows) > 1 else make_default_headers(len(first_row))
                data_rows = cleaned_rows[1:] if len(cleaned_rows) > 1 else cleaned_rows

                if not headers:
                    continue

                if len(headers) < max(len(row) for row in data_rows):
                    headers = headers + [""] * (max(len(row) for row in data_rows) - len(headers))

                for row_idx, row in enumerate(data_rows, start=1):
                    if len(row) < len(headers):
                        row = row + [""] * (len(headers) - len(row))

                    row_text = build_row_text(headers, row)
                    if not row_text:
                        continue

                    extracted_rows.append(
                        ExtractedTableRow(
                            page_number=page_index + 1,
                            table_index=table_idx,
                            row_index=row_idx,
                            headers=headers,
                            values=row,
                            row_text=row_text,
                        )
                    )

    return extracted_rows