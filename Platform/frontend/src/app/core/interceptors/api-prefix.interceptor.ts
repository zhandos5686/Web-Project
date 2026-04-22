import { HttpBackend, HttpClient, HttpErrorResponse, HttpInterceptorFn, HttpRequest } from '@angular/common/http';
import { inject, Injector } from '@angular/core';
import { catchError, map, switchMap, tap, throwError } from 'rxjs';

import { environment } from '../../../environments/environment';
import { AuthService } from '../services/auth.service';

const accessTokenKey = 'access_token';
const refreshTokenKey = 'refresh_token';
const legacyTokenKey = 'english_platform_token';

interface RefreshResponse {
  access: string;
}

function addApiPrefix(request: HttpRequest<unknown>): HttpRequest<unknown> {
  if (/^https?:\/\//.test(request.url)) {
    return request;
  }

  return request.clone({
    url: `${environment.apiUrl}${request.url.startsWith('/') ? '' : '/'}${request.url}`,
  });
}

function addAuthHeader(request: HttpRequest<unknown>, accessToken: string | null): HttpRequest<unknown> {
  if (!accessToken) {
    return request;
  }

  return request.clone({
    setHeaders: {
      Authorization: `Bearer ${accessToken}`,
    },
  });
}

export const apiPrefixInterceptor: HttpInterceptorFn = (request, next) => {
  const injector = inject(Injector);
  const httpBackend = inject(HttpBackend);
  const nextRequest = addApiPrefix(addAuthHeader(request, localStorage.getItem(accessTokenKey)));
  const isAuthRefreshRequest = nextRequest.url.endsWith('/users/auth/refresh/');

  return next(nextRequest).pipe(
    catchError((error) => {
      if (!(error instanceof HttpErrorResponse) || error.status !== 401 || isAuthRefreshRequest) {
        return throwError(() => error);
      }

      const refreshToken = localStorage.getItem(refreshTokenKey);
      if (!refreshToken) {
        injector.get(AuthService).clearAuthState();
        return throwError(() => error);
      }

      return new HttpClient(httpBackend).post<RefreshResponse>(`${environment.apiUrl}/users/auth/refresh/`, {
        refresh: refreshToken,
      }).pipe(
        tap((response) => {
          localStorage.setItem(accessTokenKey, response.access);
          localStorage.removeItem(legacyTokenKey);
        }),
        map((response) => response.access),
        switchMap((accessToken) => next(addApiPrefix(addAuthHeader(request, accessToken)))),
        catchError((refreshError) => {
          injector.get(AuthService).clearAuthState();
          return throwError(() => refreshError);
        }),
      );
    }),
  );
};
