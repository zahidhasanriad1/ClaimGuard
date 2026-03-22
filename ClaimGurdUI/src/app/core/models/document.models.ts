export interface DocumentListItem {
  document_id: string;
  original_filename: string;
  saved_path: string;
  page_count: number;
  title: string | null;
  author: string | null;
}

export interface DocumentListResponse {
  total_documents: number;
  documents: DocumentListItem[];
}

export interface UploadResponse {
  document_id: string;
  original_filename: string;
  saved_path: string;
  metadata: {
    title: string | null;
    author: string | null;
    page_count: number;
    file_size_bytes: number;
  };
}
