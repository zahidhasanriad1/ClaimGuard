import { CommonModule } from '@angular/common';
import { Component, EventEmitter, Input, Output } from '@angular/core';
import { FormsModule } from '@angular/forms';

import { DocumentListItem } from '../../../../core/models/document.models';

@Component({
  selector: 'app-control-panel',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './control-panel.component.html',
  styleUrl: './control-panel.component.css'
})
export class ControlPanelComponent {
  @Input() documents: DocumentListItem[] = [];
  @Input() selectedDocumentId = '';
  @Input() claimMode: 'rule' | 'gemini' = 'rule';
  @Input() maxClaims = 25;
  @Input() loading = false;

  @Output() selectedDocumentIdChange = new EventEmitter<string>();
  @Output() claimModeChange = new EventEmitter<'rule' | 'gemini'>();
  @Output() maxClaimsChange = new EventEmitter<number>();
  @Output() verifyRequested = new EventEmitter<void>();
  @Output() exportSummaryRequested = new EventEmitter<void>();
  @Output() exportJsonRequested = new EventEmitter<void>();
  @Output() exportCsvRequested = new EventEmitter<void>();
  @Output() logoutRequested = new EventEmitter<void>();
}
