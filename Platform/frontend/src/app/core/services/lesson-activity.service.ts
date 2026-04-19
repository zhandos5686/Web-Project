import { inject, Injectable } from '@angular/core';
import { Observable } from 'rxjs';

import { ApiService } from './api.service';

export interface QuizChoice {
  id: number;
  question?: number;
  question_text?: string;
  quiz_title?: string;
  lesson_title?: string;
  course_title?: string;
  text: string;
  is_correct?: boolean;
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
  passed?: boolean;
}

export interface LessonTask {
  id: number;
  lesson: number;
  lesson_title?: string;
  course_title?: string;
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
    teacher_feedback: string;
    passed: boolean | null;
    submitted_at: string;
    updated_at: string;
    reviewed_at: string | null;
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
  teacher_feedback: string;
  passed: boolean | null;
  submitted_at: string;
  updated_at: string;
  reviewed_at: string | null;
}

// ── Attempt history types ────────────────────────────────────────────────────

export interface QuizAttempt {
  id: number;
  score: number;
  total_questions: number;
  percentage: number;
  submitted_at: string;
}

export interface QuizDetail extends LessonQuiz {
  lesson_id: number;
  lesson_title: string;
  course_title: string;
  attempts: QuizAttempt[];
  passed: boolean;
}

export interface TaskAttempt {
  id: number;
  answer_text: string;
  status: 'submitted' | 'reviewed';
  score: number | null;
  teacher_feedback: string;
  passed: boolean | null;
  submitted_at: string;
  reviewed_at: string | null;
}

export interface TaskDetail extends LessonTask {
  lesson_id: number;
  lesson_title: string;
  course_title: string;
  attempts: TaskAttempt[];
  can_retry: boolean;
}

export interface QuizActivityItem {
  type: 'quiz';
  id: number;
  title: string;
  lesson_id: number;
  lesson_title: string;
  course_title: string;
  attempt_count: number;
  best_percentage: number | null;
  passed: boolean;
  can_retry: boolean;
}

export interface TaskActivityItem {
  type: 'task';
  id: number;
  title: string;
  lesson_id: number;
  lesson_title: string;
  course_title: string;
  attempt_count: number;
  latest_status: string | null;
  latest_score: number | null;
  latest_passed: boolean | null;
  can_retry: boolean;
}

export interface MyActivities {
  quizzes: QuizActivityItem[];
  tasks: TaskActivityItem[];
}

export interface QuizSubmitResult {
  status: string;
  message: string;
  score: number;
  total_questions: number;
  percentage: number;
  passed: boolean;
  attempt: QuizAttempt;
}

export interface TaskSubmitResult {
  status: string;
  message: string;
  attempt: TaskAttempt;
}

// ────────────────────────────────────────────────────────────────────────────

@Injectable({ providedIn: 'root' })
export class LessonActivityService {
  private readonly api = inject(ApiService);

  // Lesson-page endpoints (keep for lesson component)
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

  // My Tasks / attempt-history endpoints
  getMyActivities(): Observable<MyActivities> {
    return this.api.get<MyActivities>('/learning/my-activities/');
  }

  getQuizDetail(quizId: number): Observable<QuizDetail> {
    return this.api.get<QuizDetail>(`/learning/quizzes/${quizId}/detail/`);
  }

  submitQuizById(quizId: number, answers: QuizAnswer[]): Observable<QuizSubmitResult> {
    return this.api.post<QuizSubmitResult>(`/learning/quizzes/${quizId}/submit/`, { answers });
  }

  getTaskDetail(taskId: number): Observable<TaskDetail> {
    return this.api.get<TaskDetail>(`/learning/tasks/${taskId}/detail/`);
  }

  submitTaskById(taskId: number, answerText: string): Observable<TaskSubmitResult> {
    return this.api.post<TaskSubmitResult>(`/learning/tasks/${taskId}/submit/`, {
      answer_text: answerText,
    });
  }
}
