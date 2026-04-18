import { AsyncPipe, DatePipe } from '@angular/common';
import { Component, inject } from '@angular/core';
import { RouterLink } from '@angular/router';
import { catchError, of } from 'rxjs';

import { LessonActivityService } from '../../core/services/lesson-activity.service';

@Component({
  selector: 'app-my-tasks',
  standalone: true,
  imports: [AsyncPipe, DatePipe, RouterLink],
  template: `
    <section class="page simple-page">
      <div class="page-heading">
        <h1>My Tasks</h1>
        <p>Written answers you submitted from lesson pages are shown here.</p>
      </div>

      @if (loadError) {
        <div class="empty-state error-state">
          <strong>Could not load tasks</strong>
          <span>Please check that you are logged in as a student and the backend is running.</span>
        </div>
      }

      @if (submissions$ | async; as submissions) {
        @if (submissions.length > 0) {
          <div class="stack-list">
            @for (submission of submissions; track submission.id) {
              <article class="content-card">
                <div class="card-title-row">
                  <div>
                    <h2>{{ submission.task_title }}</h2>
                    <p>{{ submission.course_title }} / {{ submission.lesson_title }}</p>
                  </div>
                  <span class="status-pill">{{ submission.status }}</span>
                </div>
                <p class="answer-preview">{{ submission.answer_text }}</p>
                <small>Updated: {{ submission.updated_at | date: 'medium' }}</small>
                <a class="primary-link" [routerLink]="['/lessons', submission.lesson_id]">Open lesson</a>
              </article>
            }
          </div>
        } @else if (!loadError) {
          <div class="empty-state">
            <strong>No written tasks submitted yet</strong>
            <span>Open an enrolled lesson, write an answer in the task section, and submit it.</span>
            <a class="primary-link" routerLink="/my-courses">Go to my courses</a>
          </div>
        }
      }
    </section>
  `,
})
export class MyTasksComponent {
  private readonly lessonActivity = inject(LessonActivityService);

  loadError = false;
  submissions$ = this.lessonActivity.getMyTaskSubmissions().pipe(
    catchError(() => {
      this.loadError = true;
      return of([]);
    }),
  );
}
