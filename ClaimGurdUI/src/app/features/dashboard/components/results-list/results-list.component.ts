import { CommonModule } from '@angular/common';
import { Component, Input } from '@angular/core';

import { ClaimVerificationResult } from '../../../../core/models/verification.models';

@Component({
  selector: 'app-results-list',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './results-list.component.html',
  styleUrl: './results-list.component.css'
})
export class ResultsListComponent {
  @Input() results: ClaimVerificationResult[] = [];

  trackByClaim(_: number, item: ClaimVerificationResult): string {
    return item.claim_id;
  }
}
