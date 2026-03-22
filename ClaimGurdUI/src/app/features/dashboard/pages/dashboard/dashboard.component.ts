import { CommonModule } from '@angular/common';
import { Component, OnInit, inject, signal } from '@angular/core';

import { AuthService } from '../../../../core/services/auth.service';
import { ApiService } from '../../../../core/services/api.service';
import { DocumentListItem } from '../../../../core/models/document.models';
import { VerificationResponse } from '../../../../core/models/verification.models';
import { UploadPanelComponent } from '../../components/upload-panel/upload-panel.component';
import { ControlPanelComponent } from '../../components/control-panel/control-panel.component';
import { SummaryCardsComponent } from '../../components/summary-cards/summary-cards.component';
import { ResultsListComponent } from '../../components/results-list/results-list.component';

@Component({
  selector: 'app-dashboard',
  standalone: true,
  imports: [CommonModule, UploadPanelComponent, ControlPanelComponent, SummaryCardsComponent, ResultsListComponent],
  templateUrl: './dashboard.component.html',
  styleUrl: './dashboard.component.css'
})
export class DashboardComponent implements OnInit {
  private readonly api = inject(ApiService);
  private readonly authService = inject(AuthService);

  documents = signal<DocumentListItem[]>([]);
  selectedDocumentId = signal<string>('');
  verifyData = signal<VerificationResponse | null>(null);
  loading = signal<boolean>(false);
  message = signal<string>('');
  claimMode = signal<'rule' | 'gemini'>('rule');
  maxClaims = signal<number>(25);
  uploadFile = signal<File | null>(null);

  ngOnInit(): void {
    this.loadDocuments();
  }

  loadDocuments(): void {
    this.api.getDocuments().subscribe({
      next: (response) => {
        this.documents.set(response.documents ?? []);
        if (!this.selectedDocumentId() && response.documents.length > 0) {
          this.selectedDocumentId.set(response.documents[0].document_id);
        }
      },
      error: () => {
        this.message.set('Failed to load documents.');
      }
    });
  }

  onFileSelected(file: File | null): void {
    this.uploadFile.set(file);
  }

  onUploadRequested(): void {
    const file = this.uploadFile();
    if (!file) return;

    this.loading.set(true);
    this.message.set('');

    this.api.uploadPdf(file).subscribe({
      next: (response) => {
        this.message.set('Upload complete.');
        this.selectedDocumentId.set(response.document_id);
        this.loadDocuments();
        this.loading.set(false);
      },
      error: (err) => {
        this.message.set(err?.error?.detail || 'Upload failed.');
        this.loading.set(false);
      }
    });
  }

  onRunVerify(): void {
    const documentId = this.selectedDocumentId();
    if (!documentId) return;

    this.loading.set(true);
    this.message.set('');

    this.api.verifyDocument(documentId, this.claimMode(), this.maxClaims()).subscribe({
      next: (response) => {
        this.verifyData.set(response);
        this.loading.set(false);
      },
      error: (err) => {
        this.message.set(err?.error?.detail || 'Verification failed.');
        this.loading.set(false);
      }
    });
  }

  onExportSummary(): void {
    const documentId = this.selectedDocumentId();
    if (!documentId) return;

    this.loading.set(true);
    this.message.set('');

    this.api.exportSummary(documentId, this.claimMode(), this.maxClaims()).subscribe({
      next: (response) => {
        this.message.set(`Summary exported to ${response.file_path}`);
        this.loading.set(false);
      },
      error: (err) => {
        this.message.set(err?.error?.detail || 'Summary export failed.');
        this.loading.set(false);
      }
    });
  }

  onExportJson(): void {
    const documentId = this.selectedDocumentId();
    if (!documentId) return;

    this.loading.set(true);
    this.message.set('');

    this.api.exportJson(documentId, this.claimMode(), this.maxClaims()).subscribe({
      next: (response) => {
        this.message.set(`JSON exported to ${response.file_path}`);
        this.loading.set(false);
      },
      error: (err) => {
        this.message.set(err?.error?.detail || 'JSON export failed.');
        this.loading.set(false);
      }
    });
  }

  onExportCsv(): void {
    const documentId = this.selectedDocumentId();
    if (!documentId) return;

    this.loading.set(true);
    this.message.set('');

    this.api.exportCsv(documentId, this.claimMode(), this.maxClaims()).subscribe({
      next: (response) => {
        this.message.set(`CSV exported to ${response.file_path}`);
        this.loading.set(false);
      },
      error: (err) => {
        this.message.set(err?.error?.detail || 'CSV export failed.');
        this.loading.set(false);
      }
    });
  }

  onLogout(): void {
    this.authService.logout();
  }
}
