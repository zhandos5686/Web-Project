import { inject, Injectable } from '@angular/core';
import { Observable } from 'rxjs';

import { ApiService } from './api.service';

export interface LessonCompletionResponse {
  status: 'completed' | 'already_completed' | 'forbidden' | 'not_enrolled';
  message: string;
}

export interface CourseProgress {
  course_id: number;
  course_title: string;
  total_lessons: number;
  completed_lessons: number;
  watched_percent: number;
  total_tasks: number;
  completed_tasks: number;
  tasks_percent: number;
  overall_progress: number;
  percentage: number;
}

@Injectable({ providedIn: 'root' })
export class ProgressService {
  private readonly api = inject(ApiService);

  completeLesson(lessonId: number): Observable<LessonCompletionResponse> {
    return this.api.post<LessonCompletionResponse>(`/learning/lessons/${lessonId}/complete/`, {});
  }

  getProgressSummary(): Observable<CourseProgress[]> {
    return this.api.get<CourseProgress[]>('/learning/progress-summary/');
  }

  getCourseProgress(courseId: number): Observable<CourseProgress> {
    return this.api.get<CourseProgress>(`/learning/courses/${courseId}/progress/`);
  }
}
