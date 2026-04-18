import { inject, Injectable } from '@angular/core';
import { Observable } from 'rxjs';

import { ApiService } from './api.service';
import { Course } from './course.service';

export interface Enrollment {
  id: number;
  student_username: string;
  course: Course;
  created_at: string;
}

export type EnrollmentRequestStatus = 'pending' | 'approved' | 'rejected';

export interface EnrollmentRequest {
  id: number;
  student_username: string;
  course: Course;
  status: EnrollmentRequestStatus;
  created_at: string;
  updated_at: string;
}

export interface EnrollmentResponse {
  status: 'request_created' | 'request_pending' | 'already_enrolled' | 'forbidden';
  message: string;
  enrollment?: Enrollment;
  request?: EnrollmentRequest;
}

export interface EnrollmentDecisionResponse {
  status: 'approved' | 'rejected';
  message: string;
  request: EnrollmentRequest;
  enrollment?: Enrollment;
}

export interface TeacherStudentProgress {
  enrollment_id: number;
  student_username: string;
  course_id: number;
  course_title: string;
  completed_lessons: number;
  total_lessons: number;
  percentage: number;
}

@Injectable({ providedIn: 'root' })
export class EnrollmentService {
  private readonly api = inject(ApiService);

  enroll(courseId: number): Observable<EnrollmentResponse> {
    return this.api.post<EnrollmentResponse>(`/learning/enroll/${courseId}/`, {});
  }

  getMyCourses(): Observable<Enrollment[]> {
    return this.api.get<Enrollment[]>('/learning/my-courses/');
  }

  getMyEnrollmentRequests(): Observable<EnrollmentRequest[]> {
    return this.api.get<EnrollmentRequest[]>('/learning/my-enrollment-requests/');
  }

  getTeacherEnrollmentRequests(): Observable<EnrollmentRequest[]> {
    return this.api.get<EnrollmentRequest[]>('/learning/teacher/enrollment-requests/');
  }

  updateEnrollmentRequest(requestId: number, action: 'approve' | 'reject'): Observable<EnrollmentDecisionResponse> {
    return this.api.post<EnrollmentDecisionResponse>(`/learning/teacher/enrollment-requests/${requestId}/${action}/`, {});
  }

  getTeacherStudentProgress(): Observable<TeacherStudentProgress[]> {
    return this.api.get<TeacherStudentProgress[]>('/learning/teacher/student-progress/');
  }
}
