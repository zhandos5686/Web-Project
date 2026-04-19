import { DatePipe } from '@angular/common';
import { ChangeDetectorRef, Component, OnInit, inject } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { ActivatedRoute, RouterLink } from '@angular/router';
import { catchError, finalize, of } from 'rxjs';

import {
  LessonActivityService,
  QuizAnswer,
  QuizAttempt,
  QuizDetail,
} from '../../core/services/lesson-activity.service';

@Component({
  selector: 'app-quiz-attempt',
  standalone: true,
  imports: [DatePipe, FormsModule, RouterLink],
  templateUrl: './quiz-attempt.component.html',
  styleUrl: './quiz-attempt.component.css',
})
export class QuizAttemptComponent implements OnInit {
  private readonly route = inject(ActivatedRoute);
  private readonly service = inject(LessonActivityService);
  private readonly cdr = inject(ChangeDetectorRef);

  quiz: QuizDetail | null = null;
  isLoading = true;
  errorMessage = '';

  answers: Record<number, number> = {};
  isSubmitting = false;
  submitMessage = '';
  lastAttempt: QuizAttempt | null = null;
  showForm = false;

  ngOnInit(): void {
    const id = Number(this.route.snapshot.paramMap.get('id'));
    this.service.getQuizDetail(id).pipe(
      catchError(() => {
        this.errorMessage = 'Could not load this quiz.';
        return of(null);
      }),
      finalize(() => {
        this.isLoading = false;
        this.cdr.detectChanges();
      }),
    ).subscribe((quiz) => {
      this.quiz = quiz;
      this.showForm = quiz !== null && quiz.attempts.length === 0;
      this.cdr.detectChanges();
    });
  }

  tryAgain(): void {
    this.answers = {};
    this.submitMessage = '';
    this.lastAttempt = null;
    this.showForm = true;
    this.cdr.detectChanges();
  }

  submit(): void {
    if (!this.quiz) { return; }

    const unanswered = this.quiz.questions.filter((q) => !this.answers[q.id]);
    if (unanswered.length > 0) {
      this.submitMessage = `Answer all ${this.quiz.questions.length} questions before submitting.`;
      return;
    }

    const payload: QuizAnswer[] = this.quiz.questions.map((q) => ({
      question_id: q.id,
      choice_id: Number(this.answers[q.id]),
    }));

    this.isSubmitting = true;
    this.submitMessage = '';

    this.service.submitQuizById(this.quiz.id, payload).pipe(
      finalize(() => {
        this.isSubmitting = false;
        this.cdr.detectChanges();
      }),
    ).subscribe({
      next: (result) => {
        this.lastAttempt = result.attempt;
        this.submitMessage = result.message;
        this.showForm = false;
        this.answers = {};
        if (this.quiz) {
          this.quiz = { ...this.quiz, attempts: [result.attempt, ...this.quiz.attempts], passed: result.passed };
        }
        this.cdr.detectChanges();
      },
      error: (err) => {
        this.submitMessage = err.error?.message ?? 'Could not submit quiz. Try again.';
        this.cdr.detectChanges();
      },
    });
  }
}
