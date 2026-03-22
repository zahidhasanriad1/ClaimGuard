export interface EvidenceMatch {
  source_type: string;
  page_number: number;
  sentence_text: string;
  raw_numbers: string[];
  keyword_overlap: string[];
  score: number;
  table_index: number | null;
  row_index: number | null;
  row_text: string | null;
}

export interface ClaimVerificationResult {
  claim_id: string;
  claim_page_number: number;
  claim_text: string;
  claim_type: string;
  raw_value: string;
  numeric_value: number | null;
  verdict: 'supported' | 'contradicted' | 'insufficient';
  confidence: number;
  matched_evidence: EvidenceMatch | null;
  notes: string[];
}

export interface VerificationResponse {
  document_id: string;
  total_claims: number;
  supported: number;
  contradicted: number;
  insufficient: number;
  results: ClaimVerificationResult[];
}

export interface ExportFileResponse {
  document_id: string;
  export_type: string;
  file_path: string;
  total_items: number;
}
