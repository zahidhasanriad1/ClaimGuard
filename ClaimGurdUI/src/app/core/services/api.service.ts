import { Injectable, inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';

import { API_BASE_URL } from '../constants/api.constants';
import { DocumentListResponse, UploadResponse } from '../models/document.models';
import { ExportFileResponse, VerificationResponse } from '../models/verification.models';

@Injectable({
  providedIn: 'root'
})
export class ApiService {
  private readonly http = inject(HttpClient);

  getDocuments(): Observable<DocumentListResponse> {
    return this.http.get<DocumentListResponse>(`${API_BASE_URL}/documents`);
  }

  uploadPdf(file: File): Observable<UploadResponse> {
    const formData = new FormData();
    formData.append('file', file);
    return this.http.post<UploadResponse>(`${API_BASE_URL}/ingest/upload`, formData);
  }

  verifyDocument(documentId: string, mode: string, maxClaims: number): Observable<VerificationResponse> {
    return this.http.get<VerificationResponse>(
      `${API_BASE_URL}/verify/${documentId}?include_results=true&max_claims=${maxClaims}&mode=${mode}`
    );
  }

  exportSummary(documentId: string, mode: string, maxClaims: number): Observable<ExportFileResponse> {
    return this.http.post<ExportFileResponse>(
      `${API_BASE_URL}/exports/${documentId}/summary?mode=${mode}&max_claims=${maxClaims}`,
      {}
    );
  }

  exportJson(documentId: string, mode: string, maxClaims: number): Observable<ExportFileResponse> {
    return this.http.post<ExportFileResponse>(
      `${API_BASE_URL}/exports/${documentId}/verification-json?mode=${mode}&max_claims=${maxClaims}`,
      {}
    );
  }

  exportCsv(documentId: string, mode: string, maxClaims: number): Observable<ExportFileResponse> {
    return this.http.post<ExportFileResponse>(
      `${API_BASE_URL}/exports/${documentId}/verification-csv?mode=${mode}&max_claims=${maxClaims}`,
      {}
    );
  }
}
