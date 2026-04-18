import { DatePipe } from '@angular/common';
import { ChangeDetectorRef, Component, OnDestroy, OnInit, inject } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { catchError, finalize, forkJoin, of, Subscription } from 'rxjs';

import { Course, CourseModule, Lesson } from '../../core/services/course.service';
import { AuthService } from '../../core/services/auth.service';
import {
  EnrollmentRequest,
  EnrollmentService,
  TeacherStudentProgress,
} from '../../core/services/enrollment.service';
import { LessonQuiz, MyTaskSubmission, QuizQuestion } from '../../core/services/lesson-activity.service';
import { TeacherContentService, TeacherQuizSubmission } from '../../core/services/teacher-content.service';

@Component({
  selector: 'app-teacher',
  standalone: true,
  imports: [DatePipe, FormsModule],
  templateUrl: './teacher.component.html',
  styleUrl: './teacher.component.css',
})
export class TeacherComponent implements OnInit, OnDestroy {
  private readonly authService = inject(AuthService);
  private readonly teacherContent = inject(TeacherContentService);
  private readonly enrollmentService = inject(EnrollmentService);
  private readonly cdr = inject(ChangeDetectorRef);
  private authSubscription?: Subscription;

  message = '';
  errorMessage = '';
  isLoading = false;
  updatingRequestId: number | null = null;

  courseForm = {
    title: '',
    description: '',
    level: 'A1-A2',
    image_url: '',
    category_name: 'Speaking',
    is_published: true,
  };

  moduleForm = {
    course: 0,
    title: '',
    order: 1,
  };

  lessonForm = {
    module: 0,
    title: '',
    youtube_url: '',
    content: '',
    order: 1,
  };

  quizForm = {
    lesson: 0,
    title: '',
  };

  questionForm = {
    quiz: 0,
    text: '',
    order: 1,
  };

  choiceForm = {
    question: 0,
    text: '',
    is_correct: false,
    order: 1,
  };

  taskForm = {
    lesson: 0,
    title: '',
    instructions: '',
  };

  courses: Course[] = [];
  modules: CourseModule[] = [];
  lessons: Lesson[] = [];
  quizzes: LessonQuiz[] = [];
  questions: QuizQuestion[] = [];
  enrollmentRequests: EnrollmentRequest[] = [];
  studentProgress: TeacherStudentProgress[] = [];
  quizSubmissions: TeacherQuizSubmission[] = [];
  taskSubmissions: MyTaskSubmission[] = [];

  ngOnInit(): void {
    this.authSubscription = this.authService.currentUser$.subscribe((user) => {
      if (user?.role === 'teacher' && !this.isLoading && this.courses.length === 0) {
        this.reloadOptions();
      }
      this.cdr.detectChanges();
    });
  }

  ngOnDestroy(): void {
    this.authSubscription?.unsubscribe();
  }

  createCourse(): void {
    this.clearMessages();
    this.teacherContent.createCourse(this.courseForm).subscribe({
      next: (course) => {
        this.message = `Course created: ${course.title} (id ${course.id})`;
        this.moduleForm.course = course.id;
        this.reloadOptions();
        this.cdr.detectChanges();
      },
      error: () => {
        this.errorMessage = 'Could not create course. Check the form and teacher permissions.';
        this.cdr.detectChanges();
      },
    });
  }

  createModule(): void {
    this.clearMessages();
    this.teacherContent.createModule(this.moduleForm).subscribe({
      next: (module) => {
        this.message = `Module created: ${module.title} (id ${module.id})`;
        this.lessonForm.module = module.id;
        this.reloadOptions();
        this.cdr.detectChanges();
      },
      error: () => {
        this.errorMessage = 'Could not create module. Make sure the course belongs to you.';
        this.cdr.detectChanges();
      },
    });
  }

  createLesson(): void {
    this.clearMessages();
    this.teacherContent.createLesson(this.lessonForm).subscribe({
      next: (lesson) => {
        this.message = `Lesson created: ${lesson.title} (id ${lesson.id})`;
        this.quizForm.lesson = lesson.id;
        this.taskForm.lesson = lesson.id;
        this.reloadOptions();
        this.cdr.detectChanges();
      },
      error: () => {
        this.errorMessage = 'Could not create lesson. Make sure the module belongs to you.';
        this.cdr.detectChanges();
      },
    });
  }

  createQuiz(): void {
    this.clearMessages();
    this.teacherContent.createQuiz(this.quizForm).subscribe({
      next: (quiz) => {
        this.message = `Quiz created: ${quiz.title} (id ${quiz.id})`;
        this.questionForm.quiz = quiz.id;
        this.reloadOptions();
        this.cdr.detectChanges();
      },
      error: () => {
        this.errorMessage = 'Could not create quiz. Each lesson can have only one quiz.';
        this.cdr.detectChanges();
      },
    });
  }

  createQuestion(): void {
    this.clearMessages();
    this.teacherContent.createQuestion(this.questionForm).subscribe({
      next: (question) => {
        this.message = `Question created (id ${question.id})`;
        this.choiceForm.question = question.id;
        this.reloadOptions();
        this.cdr.detectChanges();
      },
      error: () => {
        this.errorMessage = 'Could not create question. Make sure the quiz belongs to you.';
        this.cdr.detectChanges();
      },
    });
  }

  createChoice(): void {
    this.clearMessages();
    this.teacherContent.createChoice(this.choiceForm).subscribe({
      next: (choice) => {
        this.message = `Choice created: ${choice.text} (id ${choice.id})`;
        this.choiceForm.text = '';
        this.choiceForm.is_correct = false;
        this.choiceForm.order += 1;
        this.reloadOptions();
        this.cdr.detectChanges();
      },
      error: () => {
        this.errorMessage = 'Could not create choice. Make sure the question belongs to you.';
        this.cdr.detectChanges();
      },
    });
  }

  createTask(): void {
    this.clearMessages();
    this.teacherContent.createTask(this.taskForm).subscribe({
      next: (task) => {
        this.message = `Written task created: ${task.title} (id ${task.id})`;
        this.reloadOptions();
        this.cdr.detectChanges();
      },
      error: () => {
        this.errorMessage = 'Could not create task. Each lesson can have only one written task.';
        this.cdr.detectChanges();
      },
    });
  }

  updateEnrollmentRequest(requestId: number, action: 'approve' | 'reject'): void {
    this.clearMessages();
    this.updatingRequestId = requestId;
    this.enrollmentService.updateEnrollmentRequest(requestId, action).pipe(
      finalize(() => {
        this.updatingRequestId = null;
        this.cdr.detectChanges();
      }),
    ).subscribe({
      next: (response) => {
        this.message = response.message;
        this.enrollmentRequests = this.enrollmentRequests.map((request) =>
          request.id === response.request.id ? response.request : request,
        );
        this.reloadOptions();
        this.cdr.detectChanges();
      },
      error: () => {
        this.errorMessage = `Could not ${action} this enrollment request.`;
        this.cdr.detectChanges();
      },
    });
  }

  reloadOptions(): void {
    this.isLoading = true;
    forkJoin({
      courses: this.teacherContent.getMyCourses().pipe(catchError(() => of([] as Course[]))),
      modules: this.teacherContent.getMyModules().pipe(catchError(() => of([] as CourseModule[]))),
      lessons: this.teacherContent.getMyLessons().pipe(catchError(() => of([] as Lesson[]))),
      quizzes: this.teacherContent.getMyQuizzes().pipe(catchError(() => of([] as LessonQuiz[]))),
      questions: this.teacherContent.getMyQuestions().pipe(catchError(() => of([] as QuizQuestion[]))),
      enrollmentRequests: this.enrollmentService.getTeacherEnrollmentRequests().pipe(
        catchError(() => of([] as EnrollmentRequest[])),
      ),
      studentProgress: this.enrollmentService.getTeacherStudentProgress().pipe(
        catchError(() => of([] as TeacherStudentProgress[])),
      ),
      quizSubmissions: this.teacherContent.getQuizSubmissions().pipe(
        catchError(() => of([] as TeacherQuizSubmission[])),
      ),
      taskSubmissions: this.teacherContent.getTaskSubmissions().pipe(
        catchError(() => of([] as MyTaskSubmission[])),
      ),
    }).pipe(
      finalize(() => {
        this.isLoading = false;
        this.cdr.detectChanges();
      }),
    ).subscribe({
      next: (data) => {
        this.courses = data.courses;
        this.modules = data.modules;
        this.lessons = data.lessons;
        this.quizzes = data.quizzes;
        this.questions = data.questions;
        this.enrollmentRequests = data.enrollmentRequests;
        this.studentProgress = data.studentProgress;
        this.quizSubmissions = data.quizSubmissions;
        this.taskSubmissions = data.taskSubmissions;
        this.cdr.detectChanges();
      },
      error: () => {
        this.errorMessage = 'Could not load teacher dashboard data.';
        this.cdr.detectChanges();
      },
    });
  }

  private clearMessages(): void {
    this.message = '';
    this.errorMessage = '';
  }
}
