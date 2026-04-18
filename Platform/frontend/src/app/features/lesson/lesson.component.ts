import { AsyncPipe } from '@angular/common';
import { Component, inject } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { ActivatedRoute, Router, RouterLink } from '@angular/router';
import { catchError, map, of, switchMap, tap } from 'rxjs';

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
    });

    this.lessonActivityService.getTask(lessonId).pipe(
      catchError(() => of(null)),
    ).subscribe((task) => {
      this.task = task;
    });
  }

  markCompleted(lessonId: number): void {
    if (!this.authService.hasToken()) {
      this.router.navigate(['/auth']);
      return;
    }

    this.isCompleting = true;
    this.completionMessage = '';

    this.progressService.completeLesson(lessonId).subscribe({
      next: (response) => {
        this.completionMessage = response.message;
        this.completionMessageType = response.status === 'completed' ? 'success' : 'info';
      },
      error: (error) => {
        if (error.status === 401) {
          this.router.navigate(['/auth']);
          return;
        }

        if (error.status === 403 && error.error?.message) {
          this.completionMessage = error.error.message;
        } else {
          this.completionMessage = 'Could not mark this lesson as completed.';
        }
        this.completionMessageType = 'error';
      },
      complete: () => {
        this.isCompleting = false;
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

    this.lessonActivityService.submitQuiz(lessonId, answers).subscribe({
      next: (result) => {
        this.quizResult = result;
        this.quizMessage = result.message;
      },
      error: (error) => {
        if (error.status === 401) {
          this.router.navigate(['/auth']);
          return;
        }

        this.quizMessage = error.error?.message || 'Could not submit quiz answers.';
      },
      complete: () => {
        this.isSubmittingQuiz = false;
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

    this.lessonActivityService.submitTask(lessonId, this.taskAnswer).subscribe({
      next: (result) => {
        this.taskMessage = result.message;
        this.taskStatus = result.submission.status;
        this.taskAnswer = result.submission.answer_text;
      },
      error: (error) => {
        if (error.status === 401) {
          this.router.navigate(['/auth']);
          return;
        }

        this.taskMessage = error.error?.message || 'Could not submit the task answer.';
      },
      complete: () => {
        this.isSubmittingTask = false;
      },
    });
  }
}
