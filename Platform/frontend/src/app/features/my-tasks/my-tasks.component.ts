import { ChangeDetectorRef, Component, OnInit, inject } from '@angular/core';
import { RouterLink } from '@angular/router';
import { catchError, finalize, of } from 'rxjs';

import {
  LessonActivityService,
  MyActivities,
} from '../../core/services/lesson-activity.service';

@Component({
  selector: 'app-my-tasks',
  standalone: true,
  imports: [RouterLink],
  template: `
    <section class="page simple-page">
      <div class="page-heading">
        <h1>My Tasks</h1>
        <p>All quizzes and written tasks from your enrolled courses.</p>
      </div>

      @if (isLoading) {
        <p class="state-text">Loading...</p>
      }

      @if (loadError) {
        <div class="empty-state error-state">
          <strong>Could not load activities</strong>
          <span>Please check that you are logged in as a student and the backend is running.</span>
        </div>
      }

      @if (activities && !isLoading) {
        @if (activities.quizzes.length === 0 && activities.tasks.length === 0) {
          <div class="empty-state">
            <strong>No activities yet</strong>
            <span>Enroll in a course and open a lesson to find quizzes and tasks.</span>
            <a class="primary-link" routerLink="/catalog">Browse courses</a>
          </div>
        }

        @if (activities.quizzes.length > 0) {
          <div class="section-block">
            <h2 class="section-title">Quizzes</h2>
            <div class="stack-list">
              @for (quiz of activities.quizzes; track quiz.id) {
                <article class="content-card" [class.passed-card]="quiz.passed">
                  <div class="card-title-row">
                    <div>
                      <h3>{{ quiz.title }}</h3>
                      <p class="card-meta">{{ quiz.course_title }} / {{ quiz.lesson_title }}</p>
                    </div>
                    @if (quiz.passed) {
                      <span class="status-pill passed">Passed ✓</span>
                    } @else if (quiz.attempt_count > 0) {
                      <span class="status-pill failed">Not passed</span>
                    } @else {
                      <span class="status-pill new">New</span>
                    }
                  </div>
                  @if (quiz.attempt_count > 0) {
                    <p class="attempts-info">
                      {{ quiz.attempt_count }} attempt{{ quiz.attempt_count === 1 ? '' : 's' }}
                      @if (quiz.best_percentage !== null) {
                        — best score: <strong>{{ quiz.best_percentage }}%</strong>
                      }
                    </p>
                  }
                  <a class="primary-link" [routerLink]="['/my-tasks/quiz', quiz.id]">
                    {{ quiz.attempt_count === 0 ? 'Start quiz' : (quiz.passed ? 'View results' : 'Try again') }}
                  </a>
                </article>
              }
            </div>
          </div>
        }

        @if (activities.tasks.length > 0) {
          <div class="section-block">
            <h2 class="section-title">Written Tasks</h2>
            <div class="stack-list">
              @for (task of activities.tasks; track task.id) {
                <article class="content-card"
                  [class.passed-card]="task.latest_passed === true"
                  [class.failed-card]="task.latest_passed === false">
                  <div class="card-title-row">
                    <div>
                      <h3>{{ task.title }}</h3>
                      <p class="card-meta">{{ task.course_title }} / {{ task.lesson_title }}</p>
                    </div>
                    @if (task.latest_status === null) {
                      <span class="status-pill new">New</span>
                    } @else if (task.latest_status === 'submitted') {
                      <span class="status-pill pending">Awaiting review</span>
                    } @else if (task.latest_passed === true) {
                      <span class="status-pill passed">Passed ✓</span>
                    } @else {
                      <span class="status-pill failed">Not passed</span>
                    }
                  </div>
                  @if (task.attempt_count > 0) {
                    <p class="attempts-info">{{ task.attempt_count }} attempt{{ task.attempt_count === 1 ? '' : 's' }}</p>
                  }
                  <a class="primary-link" [routerLink]="['/my-tasks/task', task.id]">
                    {{ task.attempt_count === 0 ? 'Write answer' : 'View / retry' }}
                  </a>
                </article>
              }
            </div>
          </div>
        }
      }
    </section>
  `,
  styles: [`
    .section-block { display: grid; gap: 14px; }
    .section-title { font-size: 21px; margin: 0; color: var(--color-text); }
    .stack-list { display: grid; gap: 14px; }
    .content-card {
      padding: var(--space-card);
      border: 1px solid var(--color-line);
      border-radius: var(--radius);
      background: var(--color-surface);
      display: grid;
      gap: 12px;
      box-shadow: 0 10px 28px rgb(23 32 51 / 5%);
    }
    .content-card.passed-card { border-color: #b9ddc5; background: #f8fffb; }
    .content-card.failed-card { border-color: #f0b8b8; background: #fffafa; }
    .card-title-row { display: flex; justify-content: space-between; align-items: flex-start; gap: 12px; }
    .card-title-row h3 { margin: 0; font-size: 18px; color: var(--color-text); }
    .card-meta { margin: 2px 0 0; font-size: 13px; color: var(--color-muted); }
    .attempts-info { margin: 0; font-size: 13px; color: var(--color-muted); }
    .primary-link {
      display: inline-flex;
      align-items: center;
      justify-content: center;
      width: fit-content;
      min-height: 38px;
      padding: 0 18px;
      background: var(--color-primary);
      color: #ffffff !important;
      font-weight: 800;
      font-size: 14px;
      text-decoration: none;
      border-radius: var(--radius-control);
      margin-top: 4px;
      box-shadow: 0 8px 18px rgb(36 84 166 / 15%);
    }
    .primary-link:hover { background: var(--color-primary-strong); }
    .empty-state { display: grid; gap: 8px; padding: 32px; text-align: center; border: 1px dashed var(--color-line); border-radius: var(--radius); }
    .error-state { color: #a42222; }
    .state-text { color: var(--color-muted); }
    .page-heading p { color: var(--color-muted); font-size: 14px; margin: 4px 0 0; }
    @media (max-width: 640px) {
      .card-title-row { flex-direction: column; }
      .primary-link { width: 100%; }
    }
  `],
})
export class MyTasksComponent implements OnInit {
  private readonly lessonActivity = inject(LessonActivityService);
  private readonly cdr = inject(ChangeDetectorRef);

  activities: MyActivities | null = null;
  isLoading = true;
  loadError = false;

  ngOnInit(): void {
    this.lessonActivity.getMyActivities().pipe(
      catchError(() => {
        this.loadError = true;
        return of(null);
      }),
      finalize(() => {
        this.isLoading = false;
        this.cdr.detectChanges();
      }),
    ).subscribe((data) => {
      this.activities = data;
      this.cdr.detectChanges();
    });
  }
}
