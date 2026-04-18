import { AsyncPipe } from '@angular/common';
import { Component, inject } from '@angular/core';
import { RouterLink } from '@angular/router';
import { catchError, of } from 'rxjs';

import { ProgressService } from '../../core/services/progress.service';

@Component({
  selector: 'app-progress',
  standalone: true,
  imports: [AsyncPipe, RouterLink],
  templateUrl: './progress.component.html',
  styleUrl: './progress.component.css',
})
export class ProgressComponent {
  private readonly progressService = inject(ProgressService);

  loadError = false;

  readonly progress$ = this.progressService.getProgressSummary().pipe(
    catchError(() => {
      this.loadError = true;
      return of([]);
    }),
  );
}
