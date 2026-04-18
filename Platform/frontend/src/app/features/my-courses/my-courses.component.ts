import { AsyncPipe, DatePipe } from '@angular/common';
import { Component, inject } from '@angular/core';
import { RouterLink } from '@angular/router';
import { catchError, of } from 'rxjs';

import { EnrollmentService } from '../../core/services/enrollment.service';

@Component({
  selector: 'app-my-courses',
  standalone: true,
  imports: [AsyncPipe, DatePipe, RouterLink],
  templateUrl: './my-courses.component.html',
  styleUrl: './my-courses.component.css',
})
export class MyCoursesComponent {
  private readonly enrollmentService = inject(EnrollmentService);

  loadError = false;
  requestLoadError = false;

  readonly enrollments$ = this.enrollmentService.getMyCourses().pipe(
    catchError(() => {
      this.loadError = true;
      return of([]);
    }),
  );

  readonly requests$ = this.enrollmentService.getMyEnrollmentRequests().pipe(
    catchError(() => {
      this.requestLoadError = true;
      return of([]);
    }),
  );
}
