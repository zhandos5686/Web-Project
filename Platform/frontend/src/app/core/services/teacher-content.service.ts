import { inject, Injectable } from '@angular/core';
import { Observable } from 'rxjs';

import { ApiService } from './api.service';
import { Course, CourseModule, Lesson } from './course.service';
import { LessonTask, MyTaskSubmission, QuizChoice, QuizQuestion } from './lesson-activity.service';

export interface CreateCoursePayload {
  title: string;
  description: string;
  level: string;
  image_url: string;
  category_name: string;
  is_published: boolean;
}

export interface CreateModulePayload {
  course: number;
  title: string;
  order: number;
}

export interface CreateLessonPayload {
  module: number;
  title: string;
  youtube_url: string;
  content: string;
  order: number;
}

export interface CreateQuizPayload {
  lesson: number;
  title: string;
}

export interface CreatedQuiz {
  id: number;
  lesson: number;
  title: string;
}

export interface TeacherQuizSubmission {
  id: number;
  student_username: string;
  quiz: number;
  quiz_title: string;
  lesson_id: number;
  lesson_title: string;
  course_id: number;
  course_title: string;
  selected_answers: Record<string, number>;
  score: number;
  total_questions: number;
  submitted_at: string;
}

export interface CreateQuestionPayload {
  quiz: number;
  text: string;
  order: number;
}

export interface CreateChoicePayload {
  question: number;
  text: string;
  is_correct: boolean;
  order: number;
}

export interface CreateTaskPayload {
  lesson: number;
  title: string;
  instructions: string;
}

@Injectable({ providedIn: 'root' })
export class TeacherContentService {
  private readonly api = inject(ApiService);

  getCourses(): Observable<Course[]> {
    return this.api.get<Course[]>('/courses/courses/');
  }

  getModules(): Observable<CourseModule[]> {
    return this.api.get<CourseModule[]>('/courses/modules/');
  }

  getLessons(): Observable<Lesson[]> {
    return this.api.get<Lesson[]>('/courses/lessons/');
  }

  createCourse(payload: CreateCoursePayload): Observable<Course> {
    return this.api.post<Course>('/courses/teacher/courses/', payload);
  }

  createModule(payload: CreateModulePayload): Observable<CourseModule> {
    return this.api.post<CourseModule>('/courses/teacher/modules/', payload);
  }

  createLesson(payload: CreateLessonPayload): Observable<Lesson> {
    return this.api.post<Lesson>('/courses/teacher/lessons/', payload);
  }

  createQuiz(payload: CreateQuizPayload): Observable<CreatedQuiz> {
    return this.api.post<CreatedQuiz>('/learning/teacher/quizzes/', payload);
  }

  createQuestion(payload: CreateQuestionPayload): Observable<QuizQuestion> {
    return this.api.post<QuizQuestion>('/learning/teacher/questions/', payload);
  }

  createChoice(payload: CreateChoicePayload): Observable<QuizChoice> {
    return this.api.post<QuizChoice>('/learning/teacher/choices/', payload);
  }

  createTask(payload: CreateTaskPayload): Observable<LessonTask> {
    return this.api.post<LessonTask>('/learning/teacher/tasks/', payload);
  }

  getQuizSubmissions(): Observable<TeacherQuizSubmission[]> {
    return this.api.get<TeacherQuizSubmission[]>('/learning/teacher/quiz-submissions/');
  }

  getTaskSubmissions(): Observable<MyTaskSubmission[]> {
    return this.api.get<MyTaskSubmission[]>('/learning/teacher/task-submissions/');
  }
}
