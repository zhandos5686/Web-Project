import { inject, Injectable } from '@angular/core';
import { Observable } from 'rxjs';

import { ApiService } from './api.service';
import { Course, CourseModule, Lesson } from './course.service';
import { LessonQuiz, LessonTask, MyTaskSubmission, QuizChoice, QuizQuestion } from './lesson-activity.service';

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
  lesson_title?: string;
  course_title?: string;
  title: string;
  questions?: QuizQuestion[];
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

export type UpdateCoursePayload = Partial<CreateCoursePayload>;
export type UpdateModulePayload = Partial<Omit<CreateModulePayload, 'course'>>;
export type UpdateLessonPayload = Partial<Omit<CreateLessonPayload, 'module'>>;
export type UpdateQuizPayload = Partial<Omit<CreateQuizPayload, 'lesson'>>;
export type UpdateQuestionPayload = Partial<Omit<CreateQuestionPayload, 'quiz'>>;
export type UpdateChoicePayload = Partial<Omit<CreateChoicePayload, 'question'>>;
export type UpdateTaskPayload = Partial<Omit<CreateTaskPayload, 'lesson'>>;

export interface DeleteResponse {
  message: string;
}

export interface ReviewTaskSubmissionPayload {
  score: number;
  teacher_feedback: string;
}

export interface ReviewTaskSubmissionResponse {
  status: 'reviewed';
  message: string;
  submission: MyTaskSubmission;
}

@Injectable({ providedIn: 'root' })
export class TeacherContentService {
  private readonly api = inject(ApiService);

  getMyCourses(): Observable<Course[]> {
    return this.api.get<Course[]>('/courses/teacher/my-courses/');
  }

  getMyModules(): Observable<CourseModule[]> {
    return this.api.get<CourseModule[]>('/courses/teacher/my-modules/');
  }

  getMyLessons(): Observable<Lesson[]> {
    return this.api.get<Lesson[]>('/courses/teacher/my-lessons/');
  }

  getMyQuizzes(): Observable<LessonQuiz[]> {
    return this.api.get<LessonQuiz[]>('/learning/teacher/my-quizzes/');
  }

  getMyQuestions(): Observable<QuizQuestion[]> {
    return this.api.get<QuizQuestion[]>('/learning/teacher/my-questions/');
  }

  getMyChoices(): Observable<QuizChoice[]> {
    return this.api.get<QuizChoice[]>('/learning/teacher/my-choices/');
  }

  getMyTasks(): Observable<LessonTask[]> {
    return this.api.get<LessonTask[]>('/learning/teacher/my-tasks/');
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

  updateCourse(id: number, payload: UpdateCoursePayload): Observable<Course> {
    return this.api.patch<Course>(`/courses/teacher/courses/${id}/`, payload);
  }

  deleteCourse(id: number): Observable<DeleteResponse> {
    return this.api.delete<DeleteResponse>(`/courses/teacher/courses/${id}/`);
  }

  updateModule(id: number, payload: UpdateModulePayload): Observable<CourseModule> {
    return this.api.patch<CourseModule>(`/courses/teacher/modules/${id}/`, payload);
  }

  deleteModule(id: number): Observable<DeleteResponse> {
    return this.api.delete<DeleteResponse>(`/courses/teacher/modules/${id}/`);
  }

  updateLesson(id: number, payload: UpdateLessonPayload): Observable<Lesson> {
    return this.api.patch<Lesson>(`/courses/teacher/lessons/${id}/`, payload);
  }

  deleteLesson(id: number): Observable<DeleteResponse> {
    return this.api.delete<DeleteResponse>(`/courses/teacher/lessons/${id}/`);
  }

  updateQuiz(id: number, payload: UpdateQuizPayload): Observable<LessonQuiz> {
    return this.api.patch<LessonQuiz>(`/learning/teacher/quizzes/${id}/`, payload);
  }

  deleteQuiz(id: number): Observable<DeleteResponse> {
    return this.api.delete<DeleteResponse>(`/learning/teacher/quizzes/${id}/`);
  }

  updateQuestion(id: number, payload: UpdateQuestionPayload): Observable<QuizQuestion> {
    return this.api.patch<QuizQuestion>(`/learning/teacher/questions/${id}/`, payload);
  }

  deleteQuestion(id: number): Observable<DeleteResponse> {
    return this.api.delete<DeleteResponse>(`/learning/teacher/questions/${id}/`);
  }

  updateChoice(id: number, payload: UpdateChoicePayload): Observable<QuizChoice> {
    return this.api.patch<QuizChoice>(`/learning/teacher/choices/${id}/`, payload);
  }

  deleteChoice(id: number): Observable<DeleteResponse> {
    return this.api.delete<DeleteResponse>(`/learning/teacher/choices/${id}/`);
  }

  updateTask(id: number, payload: UpdateTaskPayload): Observable<LessonTask> {
    return this.api.patch<LessonTask>(`/learning/teacher/tasks/${id}/`, payload);
  }

  deleteTask(id: number): Observable<DeleteResponse> {
    return this.api.delete<DeleteResponse>(`/learning/teacher/tasks/${id}/`);
  }

  getQuizSubmissions(): Observable<TeacherQuizSubmission[]> {
    return this.api.get<TeacherQuizSubmission[]>('/learning/teacher/quiz-submissions/');
  }

  getTaskSubmissions(): Observable<MyTaskSubmission[]> {
    return this.api.get<MyTaskSubmission[]>('/learning/teacher/task-submissions/');
  }

  reviewTaskSubmission(
    submissionId: number,
    payload: ReviewTaskSubmissionPayload,
  ): Observable<ReviewTaskSubmissionResponse> {
    return this.api.post<ReviewTaskSubmissionResponse>(
      `/learning/teacher/task-submissions/${submissionId}/review/`,
      payload,
    );
  }
}
