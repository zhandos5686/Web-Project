import { AsyncPipe } from '@angular/common';
import { Component, inject } from '@angular/core';
import { RouterLink } from '@angular/router';
import { catchError, of } from 'rxjs';

import { CourseService } from '../../core/services/course.service';

@Component({
  selector: 'app-catalog',
  standalone: true,
  imports: [AsyncPipe, RouterLink],
  templateUrl: './catalog.component.html',
  styleUrl: './catalog.component.css',
})
export class CatalogComponent {
  private readonly courseService = inject(CourseService);

  readonly courses$ = this.courseService.getCourses().pipe(
    catchError(() => {
      this.loadError = true;
      return of([]);
    }),
  );

  loadError = false;
}
