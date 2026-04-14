import { Component, inject, OnInit, ChangeDetectorRef } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { CourseService } from '../../services/course.service';
import { AuthService } from '../../services/auth.service';
import { Course } from '../../interfaces/course';
import { Category } from '../../interfaces/category';

@Component({
  selector: 'app-catalog',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './catalog.component.html',
  styleUrl: './catalog.component.css'
})
export class CatalogComponent implements OnInit {
  private courseService = inject(CourseService);
  private authService = inject(AuthService);
  private cdr = inject(ChangeDetectorRef);

  courses: Course[] = [];
  filteredCourses: Course[] = [];
  categories: Category[] = [];
  enrolledCourseIds = new Set<number>();

  errorMessage = '';
  successMessage = '';
  isLoading = true;

  searchText = '';
  selectedCategoryId = 0;

  ngOnInit(): void {
    this.loadCatalogData();
  }

  loadCatalogData(): void {
    this.isLoading = true;
    this.errorMessage = '';
    this.successMessage = '';

    this.courseService.getCourses().subscribe({
      next: (coursesData) => {
        this.courses = coursesData;
        this.filteredCourses = coursesData;

        this.courseService.getCategories().subscribe({
          next: (categoriesData) => {
            this.categories = categoriesData;

            if (this.isLoggedIn()) {
              this.courseService.getMyCourses().subscribe({
                next: (myCourses) => {
                  this.enrolledCourseIds = new Set(myCourses.map(c => c.id));
                  this.isLoading = false;
                  this.applyFilters();
                  this.cdr.detectChanges();
                },
                error: () => {
                  this.isLoading = false;
                  this.applyFilters();
                  this.cdr.detectChanges();
                }
              });
            } else {
              this.isLoading = false;
              this.applyFilters();
              this.cdr.detectChanges();
            }
          },
          error: () => {
            this.errorMessage = 'Failed to load categories';
            this.isLoading = false;
            this.cdr.detectChanges();
          }
        });
      },
      error: () => {
        this.errorMessage = 'Failed to load courses';
        this.isLoading = false;
        this.cdr.detectChanges();
      }
    });
  }

  isLoggedIn(): boolean {
    return this.authService.isLoggedIn();
  }

  isEnrolled(courseId: number): boolean {
    return this.enrolledCourseIds.has(courseId);
  }

  enroll(courseId: number): void {
    this.errorMessage = '';
    this.successMessage = '';

    this.courseService.enrollInCourse(courseId).subscribe({
      next: (response) => {
        this.successMessage = response.message || 'Enrolled successfully';
        this.enrolledCourseIds.add(courseId);
        this.cdr.detectChanges();
      },
      error: () => {
        this.errorMessage = 'Failed to enroll. Please login first.';
        this.cdr.detectChanges();
      }
    });
  }

  applyFilters(): void {
    const search = this.searchText.trim().toLowerCase();

    this.filteredCourses = this.courses.filter((course) => {
      const matchesSearch =
        course.title.toLowerCase().includes(search) ||
        course.description.toLowerCase().includes(search);

      const matchesCategory =
        this.selectedCategoryId === 0 || course.category === this.selectedCategoryId;

      return matchesSearch && matchesCategory;
    });

    this.cdr.detectChanges();
  }

  getCategoryName(categoryId: number): string {
    const category = this.categories.find((c) => c.id === categoryId);
    return category ? category.name : 'Unknown';
  }
}
