import { inject, Injectable } from '@angular/core';
import { Observable } from 'rxjs';

import { ApiService } from './api.service';

export interface QuizChoice {
  id: number;
  text: string;
  order: number;
}

export interface QuizQuestion {
  id: number;
  quiz?: number;
  quiz_title?: string;
  lesson_title?: string;
  course_title?: string;
  text: string;
  order: number;
  choices: QuizChoice[];
}

export interface LessonQuiz {
  id: number;
  lesson: number;
  lesson_title?: string;
  course_title?: string;
  title: string;
  questions: QuizQuestion[];
}

export interface QuizAnswer {
  question_id: number;
  choice_id: number;
}

export interface QuizResult {
  status: 'submitted';
  message: string;
  score: number;
  total_questions: number;
  percentage: number;
}

export interface LessonTask {
  id: number;
  lesson: number;
  title: string;
  instructions: string;
}

export interface TaskSubmissionResult {
  status: 'submitted' | 'updated';
  message: string;
  submission: {
    id: number;
    task: number;
    answer_text: string;
    status: string;
    score: number | null;
    submitted_at: string;
    updated_at: string;
  };
}

export interface MyTaskSubmission {
  id: number;
  student_username: string;
  task: number;
  task_title: string;
  lesson_id: number;
  lesson_title: string;
  course_id: number;
  course_title: string;
  answer_text: string;
  status: string;
  score: number | null;
  submitted_at: string;
  updated_at: string;
}

@Injectable({ providedIn: 'root' })
export class LessonActivityService {
  private readonly api = inject(ApiService);

  getQuiz(lessonId: number): Observable<LessonQuiz> {
    return this.api.get<LessonQuiz>(`/learning/lessons/${lessonId}/quiz/`);
  }

  submitQuiz(lessonId: number, answers: QuizAnswer[]): Observable<QuizResult> {
    return this.api.post<QuizResult>(`/learning/lessons/${lessonId}/quiz/submit/`, { answers });
  }

  getTask(lessonId: number): Observable<LessonTask> {
    return this.api.get<LessonTask>(`/learning/lessons/${lessonId}/task/`);
  }

  submitTask(lessonId: number, answerText: string): Observable<TaskSubmissionResult> {
    return this.api.post<TaskSubmissionResult>(`/learning/lessons/${lessonId}/task/submit/`, {
      answer_text: answerText,
    });
  }

  getMyTaskSubmissions(): Observable<MyTaskSubmission[]> {
    return this.api.get<MyTaskSubmission[]>('/learning/my-task-submissions/');
  }
}
