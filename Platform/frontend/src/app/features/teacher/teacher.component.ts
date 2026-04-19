import { DatePipe } from '@angular/common';
import { ChangeDetectorRef, Component, OnDestroy, OnInit, inject } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { catchError, finalize, forkJoin, Observable, of, Subscription } from 'rxjs';

import { Course, CourseModule, Lesson } from '../../core/services/course.service';
import { AuthService } from '../../core/services/auth.service';
import {
  EnrollmentRequest,
  EnrollmentService,
  TeacherStudentProgress,
} from '../../core/services/enrollment.service';
import { LessonQuiz, LessonTask, MyTaskSubmission, QuizChoice, QuizQuestion } from '../../core/services/lesson-activity.service';
import { TeacherContentService, TeacherQuizSubmission } from '../../core/services/teacher-content.service';

type EditableContentType = 'course' | 'module' | 'lesson' | 'quiz' | 'question' | 'choice' | 'task';

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
  reviewingSubmissionId: number | null = null;
  savingReviewId: number | null = null;
  editingItem: { type: EditableContentType; id: number } | null = null;
  deletingItem: { type: EditableContentType; id: number } | null = null;
  savingContentKey = '';
  deletingContentKey = '';
  reviewForm = {
    score: 0,
    teacher_feedback: '',
  };

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
  choices: QuizChoice[] = [];
  tasks: LessonTask[] = [];
  enrollmentRequests: EnrollmentRequest[] = [];
  studentProgress: TeacherStudentProgress[] = [];
  quizSubmissions: TeacherQuizSubmission[] = [];
  taskSubmissions: MyTaskSubmission[] = [];
  editForms: any = {
    course: {},
    module: {},
    lesson: {},
    quiz: {},
    question: {},
    choice: {},
    task: {},
  };

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

  openReviewForm(submission: MyTaskSubmission): void {
    this.clearMessages();
    this.reviewingSubmissionId = submission.id;
    this.reviewForm = {
      score: submission.score ?? 0,
      teacher_feedback: submission.teacher_feedback || '',
    };
    this.cdr.detectChanges();
  }

  cancelReview(): void {
    this.reviewingSubmissionId = null;
    this.savingReviewId = null;
    this.reviewForm = {
      score: 0,
      teacher_feedback: '',
    };
    this.cdr.detectChanges();
  }

  saveTaskReview(submissionId: number): void {
    this.clearMessages();
    this.savingReviewId = submissionId;
    this.teacherContent.reviewTaskSubmission(submissionId, this.reviewForm).pipe(
      finalize(() => {
        this.savingReviewId = null;
        this.cdr.detectChanges();
      }),
    ).subscribe({
      next: (response) => {
        this.message = response.message;
        this.taskSubmissions = this.taskSubmissions.map((submission) =>
          submission.id === response.submission.id ? response.submission : submission,
        );
        this.reviewingSubmissionId = null;
        this.cdr.detectChanges();
      },
      error: () => {
        this.errorMessage = 'Could not save review. Score must be between 0 and 100 and the submission must belong to your course.';
        this.cdr.detectChanges();
      },
    });
  }

  startEdit(type: EditableContentType, item: any): void {
    this.clearMessages();
    this.editingItem = { type, id: item.id };
    this.deletingItem = null;

    if (type === 'course') {
      this.editForms.course = {
        title: item.title,
        description: item.description,
        level: item.level,
        image_url: item.image_url,
        category_name: item.category?.name || '',
        is_published: item.is_published,
      };
    } else if (type === 'module') {
      this.editForms.module = { title: item.title, order: item.order };
    } else if (type === 'lesson') {
      this.editForms.lesson = {
        title: item.title,
        youtube_url: item.youtube_url,
        content: item.content,
        order: item.order,
      };
    } else if (type === 'quiz') {
      this.editForms.quiz = { title: item.title };
    } else if (type === 'question') {
      this.editForms.question = { text: item.text, order: item.order };
    } else if (type === 'choice') {
      this.editForms.choice = { text: item.text, is_correct: Boolean(item.is_correct), order: item.order };
    } else if (type === 'task') {
      this.editForms.task = { title: item.title, instructions: item.instructions };
    }

    this.cdr.detectChanges();
  }

  cancelEdit(): void {
    this.editingItem = null;
    this.savingContentKey = '';
    this.cdr.detectChanges();
  }

  isEditing(type: EditableContentType, id: number): boolean {
    return this.editingItem?.type === type && this.editingItem.id === id;
  }

  askDelete(type: EditableContentType, id: number): void {
    this.clearMessages();
    this.editingItem = null;
    this.deletingItem = { type, id };
    this.cdr.detectChanges();
  }

  cancelDelete(): void {
    this.deletingItem = null;
    this.deletingContentKey = '';
    this.cdr.detectChanges();
  }

  isDeleting(type: EditableContentType, id: number): boolean {
    return this.deletingItem?.type === type && this.deletingItem.id === id;
  }

  saveContent(type: EditableContentType, id: number): void {
    this.clearMessages();
    const key = `${type}-${id}`;
    this.savingContentKey = key;
    const payload = this.editForms[type];
    const request$: Observable<any> = type === 'course'
      ? this.teacherContent.updateCourse(id, payload)
      : type === 'module'
        ? this.teacherContent.updateModule(id, payload)
        : type === 'lesson'
          ? this.teacherContent.updateLesson(id, payload)
          : type === 'quiz'
            ? this.teacherContent.updateQuiz(id, payload)
            : type === 'question'
              ? this.teacherContent.updateQuestion(id, payload)
              : type === 'choice'
                ? this.teacherContent.updateChoice(id, payload)
                : this.teacherContent.updateTask(id, payload);

    request$.pipe(
      finalize(() => {
        this.savingContentKey = '';
        this.cdr.detectChanges();
      }),
    ).subscribe({
      next: () => {
        this.message = `${this.contentLabel(type)} updated successfully.`;
        this.editingItem = null;
        this.reloadOptions();
        this.cdr.detectChanges();
      },
      error: () => {
        this.errorMessage = `Could not update this ${this.contentLabel(type).toLowerCase()}. Make sure it belongs to you.`;
        this.cdr.detectChanges();
      },
    });
  }

  confirmDelete(type: EditableContentType, id: number): void {
    this.clearMessages();
    const key = `${type}-${id}`;
    this.deletingContentKey = key;
    const request$: Observable<{ message: string }> = type === 'course'
      ? this.teacherContent.deleteCourse(id)
      : type === 'module'
        ? this.teacherContent.deleteModule(id)
        : type === 'lesson'
          ? this.teacherContent.deleteLesson(id)
          : type === 'quiz'
            ? this.teacherContent.deleteQuiz(id)
            : type === 'question'
              ? this.teacherContent.deleteQuestion(id)
              : type === 'choice'
                ? this.teacherContent.deleteChoice(id)
                : this.teacherContent.deleteTask(id);

    request$.pipe(
      finalize(() => {
        this.deletingContentKey = '';
        this.cdr.detectChanges();
      }),
    ).subscribe({
      next: (response) => {
        this.message = response.message;
        this.deletingItem = null;
        this.reloadOptions();
        this.cdr.detectChanges();
      },
      error: () => {
        this.errorMessage = `Could not delete this ${this.contentLabel(type).toLowerCase()}. Make sure it belongs to you.`;
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
      choices: this.teacherContent.getMyChoices().pipe(catchError(() => of([] as QuizChoice[]))),
      tasks: this.teacherContent.getMyTasks().pipe(catchError(() => of([] as LessonTask[]))),
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
        this.choices = data.choices;
        this.tasks = data.tasks;
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

  private contentLabel(type: EditableContentType): string {
    const labels: Record<EditableContentType, string> = {
      course: 'Course',
      module: 'Module',
      lesson: 'Lesson',
      quiz: 'Quiz',
      question: 'Question',
      choice: 'Choice',
      task: 'Written task',
    };
    return labels[type];
  }
}
