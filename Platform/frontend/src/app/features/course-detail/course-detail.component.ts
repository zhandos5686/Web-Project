import { AsyncPipe } from '@angular/common';
import { Component, inject } from '@angular/core';
import { ActivatedRoute, Router, RouterLink } from '@angular/router';
import { catchError, map, of, switchMap } from 'rxjs';

import { AuthService } from '../../core/services/auth.service';
import { CourseService } from '../../core/services/course.service';
import { EnrollmentService } from '../../core/services/enrollment.service';

@Component({
  selector: 'app-course-detail',
  standalone: true,
  imports: [AsyncPipe, RouterLink],
  templateUrl: './course-detail.component.html',
  styleUrl: './course-detail.component.css',
})
export class CourseDetailComponent {
  private readonly route = inject(ActivatedRoute);
  private readonly router = inject(Router);
  private readonly authService = inject(AuthService);
  private readonly courseService = inject(CourseService);
  private readonly enrollmentService = inject(EnrollmentService);

  loadError = false;
  enrollMessage = '';
  enrollMessageType: 'success' | 'info' | 'error' = 'info';
  isEnrolling = false;
  readonly currentUser$ = this.authService.currentUser$;

  readonly course$ = this.route.paramMap.pipe(
    map((params) => params.get('id')),
    switchMap((id) => {
      if (!id) {
        this.loadError = true;
        return of(null);
      }

      return this.courseService.getCourse(id).pipe(
        catchError(() => {
          this.loadError = true;
          return of(null);
        }),
      );
    }),
  );

  enroll(courseId: number): void {
    if (!this.authService.hasToken()) {
      this.router.navigate(['/auth']);
      return;
    }

    this.isEnrolling = true;
    this.enrollMessage = '';

    this.enrollmentService.enroll(courseId).subscribe({
      next: (response) => {
        this.enrollMessage = response.message;
        this.enrollMessageType = response.status === 'request_created' ? 'success' : 'info';
      },
      error: (error) => {
        if (error.status === 401) {
          this.router.navigate(['/auth']);
          return;
        }

        this.enrollMessage = error.status === 403
          ? 'Only student users can request enrollment in courses.'
          : 'Could not send enrollment request. Please try again.';
        this.enrollMessageType = 'error';
        this.isEnrolling = false;
      },
      complete: () => {
        this.isEnrolling = false;
      },
    });
  }
}
