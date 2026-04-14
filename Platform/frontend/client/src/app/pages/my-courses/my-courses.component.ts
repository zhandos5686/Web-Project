import { Component, inject, OnInit, ChangeDetectorRef } from '@angular/core';
import { CommonModule } from '@angular/common';
import { CourseService } from '../../services/course.service';
import { Course } from '../../interfaces/course';

@Component({
  selector: 'app-my-courses',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './my-courses.component.html',
  styleUrl: './my-courses.component.css'
})
export class MyCoursesComponent implements OnInit {
  private courseService = inject(CourseService);
  private cdr = inject(ChangeDetectorRef);

  courses: Course[] = [];
  errorMessage = '';
  isLoading = true;

  ngOnInit(): void {
    console.log('MyCoursesComponent init');
    this.loadMyCourses();
  }

  loadMyCourses(): void {
    console.log('loadMyCourses started');
    this.isLoading = true;
    this.errorMessage = '';

    this.courseService.getMyCourses().subscribe({
      next: (data) => {
        console.log('my-courses response:', data);
        this.courses = data;
        this.isLoading = false;
        this.cdr.detectChanges();
      },
      error: (err) => {
        console.log('my-courses error:', err);
        this.errorMessage = 'Failed to load my courses. Please login first.';
        this.isLoading = false;
        this.cdr.detectChanges();
      }
    });
  }
}
