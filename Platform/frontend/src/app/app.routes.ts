import { Routes } from '@angular/router';

import { authGuard } from './core/guards/auth.guard';
import { teacherGuard } from './core/guards/teacher.guard';
import { AuthComponent } from './features/auth/auth.component';
import { BookingComponent } from './features/booking/booking.component';
import { CatalogComponent } from './features/catalog/catalog.component';
import { CourseDetailComponent } from './features/course-detail/course-detail.component';
import { HomeComponent } from './features/home/home.component';
import { LessonComponent } from './features/lesson/lesson.component';
import { MyCoursesComponent } from './features/my-courses/my-courses.component';
import { MyTasksComponent } from './features/my-tasks/my-tasks.component';
import { ProfileComponent } from './features/profile/profile.component';
import { ProgressComponent } from './features/progress/progress.component';
import { TeacherComponent } from './features/teacher/teacher.component';

export const routes: Routes = [
  { path: '', component: HomeComponent },
  { path: 'auth', component: AuthComponent },
  { path: 'catalog', component: CatalogComponent },
  { path: 'courses/:id', component: CourseDetailComponent },
  { path: 'lessons/:id', component: LessonComponent, canActivate: [authGuard] },
  { path: 'my-courses', component: MyCoursesComponent, canActivate: [authGuard] },
  { path: 'my-tasks', component: MyTasksComponent, canActivate: [authGuard] },
  { path: 'progress', component: ProgressComponent, canActivate: [authGuard] },
  { path: 'profile', component: ProfileComponent, canActivate: [authGuard] },
  { path: 'teacher', component: TeacherComponent, canActivate: [teacherGuard] },
  { path: 'booking', component: BookingComponent, canActivate: [authGuard] },
  { path: '**', redirectTo: 'catalog' },
];
