import { DatePipe } from '@angular/common';
import { ChangeDetectorRef, Component, OnInit, inject } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { ActivatedRoute, RouterLink } from '@angular/router';
import { catchError, finalize, of } from 'rxjs';

import {
  LessonActivityService,
  TaskAttempt,
  TaskDetail,
} from '../../core/services/lesson-activity.service';

@Component({
  selector: 'app-task-attempt',
  standalone: true,
  imports: [DatePipe, FormsModule, RouterLink],
  templateUrl: './task-attempt.component.html',
  styleUrl: './task-attempt.component.css',
})
export class TaskAttemptComponent implements OnInit {
  private readonly route = inject(ActivatedRoute);
  private readonly service = inject(LessonActivityService);
  private readonly cdr = inject(ChangeDetectorRef);

  task: TaskDetail | null = null;
  isLoading = true;
  errorMessage = '';

  // Form state
  answerText = '';
  isSubmitting = false;
  submitMessage = '';
  submitError = '';
  showForm = false;

  ngOnInit(): void {
    const id = Number(this.route.snapshot.paramMap.get('id'));
    this.service.getTaskDetail(id).pipe(
      catchError(() => {
        this.errorMessage = 'Could not load this task.';
        return of(null);
      }),
      finalize(() => {
        this.isLoading = false;
        this.cdr.detectChanges();
      }),
    ).subscribe((task) => {
      this.task = task;
      this.showForm = task !== null && task.attempts.length === 0;
      this.cdr.detectChanges();
    });
  }

  tryAgain(): void {
    this.answerText = '';
    this.submitMessage = '';
    this.submitError = '';
    this.showForm = true;
    this.cdr.detectChanges();
  }

  submit(): void {
    if (!this.task) { return; }
    if (!this.answerText.trim()) {
      this.submitError = 'Answer text is required.';
      return;
    }

    this.isSubmitting = true;
    this.submitMessage = '';
    this.submitError = '';

    this.service.submitTaskById(this.task.id, this.answerText.trim()).pipe(
      finalize(() => {
        this.isSubmitting = false;
        this.cdr.detectChanges();
      }),
    ).subscribe({
      next: (result) => {
        this.submitMessage = result.message;
        this.showForm = false;
        this.answerText = '';
        if (this.task) {
          this.task = {
            ...this.task,
            attempts: [result.attempt, ...this.task.attempts],
            can_retry: false,
          };
        }
        this.cdr.detectChanges();
      },
      error: (err) => {
        this.submitError = err.error?.message ?? 'Could not submit. Try again.';
        this.cdr.detectChanges();
      },
    });
  }

  statusLabel(attempt: TaskAttempt): string {
    if (attempt.status === 'submitted') { return 'Awaiting review'; }
    if (attempt.passed === true) { return 'Passed ✓'; }
    if (attempt.passed === false) { return 'Not passed'; }
    return 'Reviewed';
  }
}
