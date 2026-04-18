import { inject } from '@angular/core';
import { CanActivateFn, Router } from '@angular/router';
import { map } from 'rxjs';

import { AuthService } from '../services/auth.service';

export const teacherGuard: CanActivateFn = () => {
  const authService = inject(AuthService);
  const router = inject(Router);
  const currentUser = authService.currentUser();

  if (currentUser?.role === 'teacher') {
    return true;
  }

  if (!authService.hasToken()) {
    return router.createUrlTree(['/auth']);
  }

  return authService.loadCurrentUser().pipe(
    map((user) => (user?.role === 'teacher' ? true : router.createUrlTree(['/catalog']))),
  );
};
