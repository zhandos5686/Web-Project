import { Routes } from '@angular/router';
import { LoginComponent } from './pages/login/login.component';
import { CatalogComponent } from './pages/catalog/catalog.component';
import { MyCoursesComponent } from './pages/my-courses/my-courses.component';
import { MyTasksComponent } from './pages/my-tasks/my-tasks.component';
import { ProfileComponent } from './pages/profile/profile.component';

export const routes: Routes = [
  { path: '', redirectTo: 'catalog', pathMatch: 'full' },
  { path: 'login', component: LoginComponent },
  { path: 'catalog', component: CatalogComponent },
  { path: 'my-courses', component: MyCoursesComponent },
  { path: 'my-tasks', component: MyTasksComponent },
  { path: 'profile', component: ProfileComponent },
];
