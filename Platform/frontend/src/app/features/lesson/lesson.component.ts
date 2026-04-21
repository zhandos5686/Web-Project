import { AsyncPipe } from '@angular/common';
import { AfterViewChecked, ChangeDetectorRef, Component, OnDestroy, inject } from '@angular/core';
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
export class LessonComponent implements AfterViewChecked, OnDestroy {
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

  youtubeProgress = 0;
  youtubeWatched = false;

  private ytPlayer: any = null;
  private progressInterval: ReturnType<typeof setInterval> | null = null;
  private pendingVideoUrl: string | null = null;
  private ytInitialized = false;

  readonly lesson$ = this.route.paramMap.pipe(
    map((params) => params.get('id')),
    switchMap((id) => {
      if (!id) {
        this.loadError = true;
        return of(null);
      }

      return this.courseService.getLesson(id).pipe(
        tap((lesson) => {
          this.destroyPlayer();
          this.youtubeProgress = 0;
          this.youtubeWatched = false;
          this.pendingVideoUrl = lesson.youtube_url || null;
          this.ytInitialized = false;
          this.loadLessonActivities(lesson.id);
        }),
        catchError(() => {
          this.loadError = true;
          return of(null);
        }),
      );
    }),
  );

  ngAfterViewChecked(): void {
    if (!this.ytInitialized && this.pendingVideoUrl) {
      const el = document.getElementById('youtube-player');
      if (el) {
        this.ytInitialized = true;
        this.createYouTubePlayer(this.pendingVideoUrl);
      }
    }
  }

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

  ngOnDestroy(): void {
    this.destroyPlayer();
  }

  private extractVideoId(url: string): string {
    try {
      const parsed = new URL(url);
      if (parsed.hostname === 'youtu.be') return parsed.pathname.slice(1).split('?')[0];
      return parsed.searchParams.get('v') ?? '';
    } catch {
      return '';
    }
  }

  private loadYouTubeApi(): Promise<void> {
    return new Promise((resolve) => {
      if ((window as any).YT?.Player) {
        resolve();
        return;
      }
      const prev = (window as any).onYouTubeIframeAPIReady;
      (window as any).onYouTubeIframeAPIReady = () => {
        if (typeof prev === 'function') prev();
        resolve();
      };
      if (!document.querySelector('script[src*="youtube.com/iframe_api"]')) {
        const tag = document.createElement('script');
        tag.src = 'https://www.youtube.com/iframe_api';
        document.body.appendChild(tag);
      }
    });
  }

  private createYouTubePlayer(url: string): void {
    const videoId = this.extractVideoId(url);
    if (!videoId) return;

    this.loadYouTubeApi().then(() => {
      const el = document.getElementById('youtube-player');
      if (!el) return;
      this.ytPlayer = new (window as any).YT.Player('youtube-player', {
        videoId,
        playerVars: { rel: 0, playsinline: 1, origin: window.location.origin },
        events: {
          onStateChange: (event: any) => {
            const state = (window as any).YT.PlayerState;
            if (event.data === state.PLAYING) {
              this.startProgressTracking();
            } else {
              this.stopProgressTracking();
            }
          },
        },
      });
    });
  }

  private startProgressTracking(): void {
    this.stopProgressTracking();
    this.progressInterval = setInterval(() => {
      if (!this.ytPlayer?.getDuration) return;
      const duration: number = this.ytPlayer.getDuration();
      const current: number = this.ytPlayer.getCurrentTime();
      if (duration > 0) {
        this.youtubeProgress = Math.min(100, Math.round((current / duration) * 100));
        if (this.youtubeProgress >= 80) {
          this.youtubeWatched = true;
        }
        this.cdr.detectChanges();
      }
    }, 1000);
  }

  private stopProgressTracking(): void {
    if (this.progressInterval !== null) {
      clearInterval(this.progressInterval);
      this.progressInterval = null;
    }
  }

  private destroyPlayer(): void {
    this.stopProgressTracking();
    if (this.ytPlayer) {
      try { this.ytPlayer.destroy(); } catch { /* ignore */ }
      this.ytPlayer = null;
    }
  }
}
