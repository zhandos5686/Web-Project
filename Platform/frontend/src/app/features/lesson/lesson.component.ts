import { AsyncPipe } from '@angular/common';
import { ChangeDetectorRef, Component, inject } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { ActivatedRoute, Router, RouterLink } from '@angular/router';
import { catchError, finalize, map, of, switchMap, tap } from 'rxjs';

import { AuthService } from '../../core/services/auth.service';
import { CourseService } from '../../core/services/course.service';
import { LessonActivityService, LessonQuiz, LessonTask, QuizResult } from '../../core/services/lesson-activity.service';
import { ProgressService } from '../../core/services/progress.service';

@Component({
  selector: 'app-lesson',
  standalone: true,
  imports: [AsyncPipe, FormsModule, RouterLink],
  templateUrl: './lesson.component.html',
  styleUrl: './lesson.component.css',
})
export class LessonComponent {
  private readonly route = inject(ActivatedRoute);
  private readonly router = inject(Router);
  private readonly authService = inject(AuthService);
  private readonly courseService = inject(CourseService);
  private readonly lessonActivityService = inject(LessonActivityService);
  private readonly progressService = inject(ProgressService);
  private readonly cdr = inject(ChangeDetectorRef);

  loadError = false;
  completionMessage = '';
  completionMessageType: 'success' | 'info' | 'error' = 'info';
  isCompleting = false;
  quiz: LessonQuiz | null = null;
  quizAnswers: Record<number, number> = {};
  quizResult: QuizResult | null = null;
  quizMessage = '';
  isSubmittingQuiz = false;
  task: LessonTask | null = null;
  taskAnswer = '';
  taskMessage = '';
  taskStatus = '';
  isSubmittingTask = false;

  readonly lesson$ = this.route.paramMap.pipe(
    map((params) => params.get('id')),
    switchMap((id) => {
      if (!id) {
        this.loadError = true;
        return of(null);
      }

      return this.courseService.getLesson(id).pipe(
        tap((lesson) => this.loadLessonActivities(lesson.id)),
        catchError(() => {
          this.loadError = true;
          return of(null);
        }),
      );
    }),
  );

  loadLessonActivities(lessonId: number): void {
    this.quiz = null;
    this.quizAnswers = {};
    this.quizResult = null;
    this.quizMessage = '';
    this.task = null;
    this.taskAnswer = '';
    this.taskMessage = '';
    this.taskStatus = '';

    this.lessonActivityService.getQuiz(lessonId).pipe(
      catchError(() => of(null)),
    ).subscribe((quiz) => {
      this.quiz = quiz;
      this.cdr.detectChanges();
    });

    this.lessonActivityService.getTask(lessonId).pipe(
      catchError(() => of(null)),
    ).subscribe((task) => {
      this.task = task;
      this.cdr.detectChanges();
    });
  }

  markCompleted(lessonId: number): void {
    if (!this.authService.hasToken()) {
      this.router.navigate(['/auth']);
      return;
    }

    this.isCompleting = true;
    this.completionMessage = '';

    this.progressService.completeLesson(lessonId).pipe(
      finalize(() => {
        this.isCompleting = false;
        this.cdr.detectChanges();
      }),
    ).subscribe({
      next: (response) => {
        this.completionMessage = response.message;
        this.completionMessageType = response.status === 'completed' ? 'success' : 'info';
        this.cdr.detectChanges();
      },
      error: (error) => {
        if (error.status === 401) {
          this.isCompleting = false;
          this.cdr.detectChanges();
          this.router.navigate(['/auth']);
          return;
        }

        if (error.status === 403 && error.error?.message) {
          this.completionMessage = error.error.message;
        } else {
          this.completionMessage = 'Could not mark this lesson as completed.';
        }
        this.completionMessageType = 'error';
        this.cdr.detectChanges();
      },
    });
  }

  submitQuiz(lessonId: number): void {
    if (!this.quiz) {
      return;
    }

    const answers = this.quiz.questions
      .filter((question) => this.quizAnswers[question.id])
      .map((question) => ({
        question_id: question.id,
        choice_id: Number(this.quizAnswers[question.id]),
      }));

    if (answers.length !== this.quiz.questions.length) {
      this.quizMessage = 'Answer every quiz question before submitting.';
      return;
    }

    this.isSubmittingQuiz = true;
    this.quizMessage = '';
    this.quizResult = null;

    this.lessonActivityService.submitQuiz(lessonId, answers).pipe(
      finalize(() => {
        this.isSubmittingQuiz = false;
        this.cdr.detectChanges();
      }),
    ).subscribe({
      next: (result) => {
        this.quizResult = result;
        this.quizMessage = result.message;
        this.cdr.detectChanges();
      },
      error: (error) => {
        if (error.status === 401) {
          this.isSubmittingQuiz = false;
          this.cdr.detectChanges();
          this.router.navigate(['/auth']);
          return;
        }
        this.quizMessage = error.error?.message || 'Could not submit quiz answers.';
        this.cdr.detectChanges();
      },
    });
  }

  submitTask(lessonId: number): void {
    if (!this.taskAnswer.trim()) {
      this.taskMessage = 'Write your task answer before submitting.';
      return;
    }

    this.isSubmittingTask = true;
    this.taskMessage = '';
    this.taskStatus = '';

    this.lessonActivityService.submitTask(lessonId, this.taskAnswer).pipe(
      finalize(() => {
        this.isSubmittingTask = false;
        this.cdr.detectChanges();
      }),
    ).subscribe({
      next: (result) => {
        this.taskMessage = result.message;
        this.taskStatus = result.submission.status;
        this.taskAnswer = result.submission.answer_text;
        this.cdr.detectChanges();
      },
      error: (error) => {
        if (error.status === 401) {
          this.isSubmittingTask = false;
          this.cdr.detectChanges();
          this.router.navigate(['/auth']);
          return;
        }
        this.taskMessage = error.error?.message || 'Could not submit the task answer.';
        this.cdr.detectChanges();
      },
    });
  }
}
