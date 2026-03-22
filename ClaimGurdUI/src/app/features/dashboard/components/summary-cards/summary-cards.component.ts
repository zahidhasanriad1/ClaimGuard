import { CommonModule } from '@angular/common';
import { Component, Input } from '@angular/core';

import { VerificationResponse } from '../../../../core/models/verification.models';

@Component({
  selector: 'app-summary-cards',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './summary-cards.component.html',
  styleUrl: './summary-cards.component.css'
})
export class SummaryCardsComponent {
  @Input() data: VerificationResponse | null = null;
}
