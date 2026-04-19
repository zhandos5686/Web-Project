import { Routes } from '@angular/router';

import { authGuard } from './core/guards/auth.guard';
import { teacherGuard } from './core/guards/teacher.guard';
import { AuthComponent } from './features/auth/auth.component';
import { BookingComponent } from './features/booking/booking.component';
import { CatalogComponent } from './features/catalog/catalog.component';
import { CourseDetailComponent } from './features/course-detail/course-detail.component';
import { ForgotPasswordComponent } from './features/forgot-password/forgot-password.component';
import { HomeComponent } from './features/home/home.component';
import { LessonComponent } from './features/lesson/lesson.component';
import { MyCoursesComponent } from './features/my-courses/my-courses.component';
import { MyTasksComponent } from './features/my-tasks/my-tasks.component';
import { QuizAttemptComponent } from './features/quiz-attempt/quiz-attempt.component';
import { TaskAttemptComponent } from './features/task-attempt/task-attempt.component';
import { NotificationsComponent } from './features/notifications/notifications.component';
import { ProfileComponent } from './features/profile/profile.component';
import { ProgressComponent } from './features/progress/progress.component';
import { ResetPasswordComponent } from './features/reset-password/reset-password.component';
import { TeacherComponent } from './features/teacher/teacher.component';

export const routes: Routes = [
  { path: '', component: HomeComponent },
  { path: 'auth', component: AuthComponent },
  { path: 'forgot-password', component: ForgotPasswordComponent },
  { path: 'reset-password', component: ResetPasswordComponent },
  { path: 'catalog', component: CatalogComponent },
  { path: 'courses/:id', component: CourseDetailComponent },
  { path: 'lessons/:id', component: LessonComponent, canActivate: [authGuard] },
  { path: 'my-courses', component: MyCoursesComponent, canActivate: [authGuard] },
  { path: 'my-tasks', component: MyTasksComponent, canActivate: [authGuard] },
  { path: 'my-tasks/quiz/:id', component: QuizAttemptComponent, canActivate: [authGuard] },
  { path: 'my-tasks/task/:id', component: TaskAttemptComponent, canActivate: [authGuard] },
  { path: 'notifications', component: NotificationsComponent, canActivate: [authGuard] },
  { path: 'progress', component: ProgressComponent, canActivate: [authGuard] },
  { path: 'profile', component: ProfileComponent, canActivate: [authGuard] },
  { path: 'teacher', component: TeacherComponent, canActivate: [teacherGuard] },
  { path: 'booking', component: BookingComponent, canActivate: [authGuard] },
  { path: '**', redirectTo: 'catalog' },
];
