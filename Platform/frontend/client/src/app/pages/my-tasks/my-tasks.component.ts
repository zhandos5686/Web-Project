import { Component, inject, OnInit, ChangeDetectorRef } from '@angular/core';
import { CommonModule } from '@angular/common';
import { CourseService } from '../../services/course.service';
import { Task } from '../../interfaces/task';

@Component({
  selector: 'app-my-tasks',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './my-tasks.component.html',
  styleUrl: './my-tasks.component.css'
})
export class MyTasksComponent implements OnInit {
  private courseService = inject(CourseService);
  private cdr = inject(ChangeDetectorRef);

  tasks: Task[] = [];
  errorMessage = '';
  successMessage = '';
  isLoading = true;

  ngOnInit(): void {
    this.loadMyTasks();
  }

  loadMyTasks(): void {
    this.isLoading = true;
    this.errorMessage = '';
    this.successMessage = '';

    this.courseService.getMyTasks().subscribe({
      next: (data) => {
        this.tasks = data;
        this.isLoading = false;
        this.cdr.detectChanges();
      },
      error: () => {
        this.errorMessage = 'Failed to load my tasks. Please login first.';
        this.isLoading = false;
        this.cdr.detectChanges();
      }
    });
  }

  completeTask(taskId: number): void {
    this.errorMessage = '';
    this.successMessage = '';

    this.courseService.completeTask(taskId).subscribe({
      next: (response) => {
        this.successMessage = response.message || 'Task completed';
        this.loadMyTasks();
      },
      error: () => {
        this.errorMessage = 'Failed to complete task';
        this.cdr.detectChanges();
      }
    });
  }

  get completedCount(): number {
    return this.tasks.filter(task => task.is_completed).length;
  }

  get activeCount(): number {
    return this.tasks.filter(task => !task.is_completed).length;
  }
}
