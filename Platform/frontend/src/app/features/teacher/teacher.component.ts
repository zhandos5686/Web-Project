import { AsyncPipe, DatePipe } from '@angular/common';
import { Component, inject } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { catchError, of } from 'rxjs';

import { EnrollmentService } from '../../core/services/enrollment.service';
import { TeacherContentService } from '../../core/services/teacher-content.service';

@Component({
  selector: 'app-teacher',
  standalone: true,
  imports: [AsyncPipe, DatePipe, FormsModule],
  templateUrl: './teacher.component.html',
  styleUrl: './teacher.component.css',
})
export class TeacherComponent {
  private readonly teacherContent = inject(TeacherContentService);
  private readonly enrollmentService = inject(EnrollmentService);

  message = '';
  errorMessage = '';

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

  courses$ = this.teacherContent.getCourses().pipe(catchError(() => of([])));
  modules$ = this.teacherContent.getModules().pipe(catchError(() => of([])));
  lessons$ = this.teacherContent.getLessons().pipe(catchError(() => of([])));
  enrollmentRequests$ = this.enrollmentService.getTeacherEnrollmentRequests().pipe(catchError(() => of([])));
  studentProgress$ = this.enrollmentService.getTeacherStudentProgress().pipe(catchError(() => of([])));
  quizSubmissions$ = this.teacherContent.getQuizSubmissions().pipe(catchError(() => of([])));
  taskSubmissions$ = this.teacherContent.getTaskSubmissions().pipe(catchError(() => of([])));

  createCourse(): void {
    this.clearMessages();
    this.teacherContent.createCourse(this.courseForm).subscribe({
      next: (course) => {
        this.message = `Course created: ${course.title} (id ${course.id})`;
        this.moduleForm.course = course.id;
        this.reloadOptions();
      },
      error: () => this.errorMessage = 'Could not create course. Check the form and teacher permissions.',
    });
  }

  createModule(): void {
    this.clearMessages();
    this.teacherContent.createModule(this.moduleForm).subscribe({
      next: (module) => {
        this.message = `Module created: ${module.title} (id ${module.id})`;
        this.lessonForm.module = module.id;
        this.reloadOptions();
      },
      error: () => this.errorMessage = 'Could not create module. Make sure the course belongs to you.',
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
      },
      error: () => this.errorMessage = 'Could not create lesson. Make sure the module belongs to you.',
    });
  }

  createQuiz(): void {
    this.clearMessages();
    this.teacherContent.createQuiz(this.quizForm).subscribe({
      next: (quiz) => {
        this.message = `Quiz created: ${quiz.title} (id ${quiz.id})`;
        this.questionForm.quiz = quiz.id;
      },
      error: () => this.errorMessage = 'Could not create quiz. Each lesson can have only one quiz.',
    });
  }

  createQuestion(): void {
    this.clearMessages();
    this.teacherContent.createQuestion(this.questionForm).subscribe({
      next: (question) => {
        this.message = `Question created (id ${question.id})`;
        this.choiceForm.question = question.id;
      },
      error: () => this.errorMessage = 'Could not create question. Make sure the quiz belongs to you.',
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
      },
      error: () => this.errorMessage = 'Could not create choice. Make sure the question belongs to you.',
    });
  }

  createTask(): void {
    this.clearMessages();
    this.teacherContent.createTask(this.taskForm).subscribe({
      next: (task) => {
        this.message = `Written task created: ${task.title} (id ${task.id})`;
      },
      error: () => this.errorMessage = 'Could not create task. Each lesson can have only one written task.',
    });
  }

  updateEnrollmentRequest(requestId: number, action: 'approve' | 'reject'): void {
    this.clearMessages();
    this.enrollmentService.updateEnrollmentRequest(requestId, action).subscribe({
      next: (response) => {
        this.message = response.message;
        this.reloadOptions();
      },
      error: () => this.errorMessage = `Could not ${action} this enrollment request.`,
    });
  }

  reloadOptions(): void {
    this.courses$ = this.teacherContent.getCourses().pipe(catchError(() => of([])));
    this.modules$ = this.teacherContent.getModules().pipe(catchError(() => of([])));
    this.lessons$ = this.teacherContent.getLessons().pipe(catchError(() => of([])));
    this.enrollmentRequests$ = this.enrollmentService.getTeacherEnrollmentRequests().pipe(catchError(() => of([])));
    this.studentProgress$ = this.enrollmentService.getTeacherStudentProgress().pipe(catchError(() => of([])));
    this.quizSubmissions$ = this.teacherContent.getQuizSubmissions().pipe(catchError(() => of([])));
    this.taskSubmissions$ = this.teacherContent.getTaskSubmissions().pipe(catchError(() => of([])));
  }

  private clearMessages(): void {
    this.message = '';
    this.errorMessage = '';
  }
}
