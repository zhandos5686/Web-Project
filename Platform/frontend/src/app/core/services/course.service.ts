import { inject, Injectable } from '@angular/core';
import { Observable } from 'rxjs';

import { ApiService } from './api.service';

export interface CourseCategory {
  id: number;
  name: string;
  description: string;
}

export interface Lesson {
  id: number;
  title: string;
  youtube_url: string;
  content: string;
  order: number;
  module_title: string;
  course_id: number;
  course_title: string;
}

export interface CourseModule {
  id: number;
  course_id?: number;
  course_title?: string;
  title: string;
  order: number;
  lessons: Lesson[];
}

export interface Course {
  id: number;
  title: string;
  description: string;
  level: string;
  image_url: string;
  category: CourseCategory | null;
  teacher_name: string;
  is_published: boolean;
  modules: CourseModule[];
}

@Injectable({ providedIn: 'root' })
export class CourseService {
  private readonly api = inject(ApiService);

  getCourses(): Observable<Course[]> {
    return this.api.get<Course[]>('/courses/courses/');
  }

  getCourse(id: string | number): Observable<Course> {
    return this.api.get<Course>(`/courses/courses/${id}/`);
  }

  getLesson(id: string | number): Observable<Lesson> {
    return this.api.get<Lesson>(`/courses/lessons/${id}/`);
  }
}
