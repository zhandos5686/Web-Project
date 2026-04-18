import { HttpClient } from '@angular/common/http';
import { inject, Injectable } from '@angular/core';
import { BehaviorSubject, catchError, map, Observable, of, tap } from 'rxjs';

export type UserRole = 'student' | 'teacher';

export interface AuthUser {
  id: number;
  username: string;
  email: string;
  role: UserRole;
  bio: string;
}

export interface LoginPayload {
  username: string;
  password: string;
}

export interface RegisterPayload {
  username: string;
  email: string;
  password: string;
  role: UserRole;
  bio: string;
}

interface AuthResponse {
  token: string;
  user: AuthUser;
}

@Injectable({ providedIn: 'root' })
export class AuthService {
  private readonly http = inject(HttpClient);
  private readonly tokenKey = 'english_platform_token';
  private readonly currentUserSubject = new BehaviorSubject<AuthUser | null>(null);

  readonly currentUser$ = this.currentUserSubject.asObservable();
  readonly isLoggedIn$ = this.currentUser$.pipe(map((user) => Boolean(user)));

  constructor() {
    if (this.hasToken()) {
      this.loadCurrentUser().subscribe();
    }
  }

  currentUser(): AuthUser | null {
    return this.currentUserSubject.value;
  }

  hasToken(): boolean {
    return Boolean(this.getToken());
  }

  getToken(): string | null {
    return localStorage.getItem(this.tokenKey);
  }

  register(payload: RegisterPayload): Observable<AuthUser> {
    return this.http.post<AuthResponse>('/users/auth/register/', payload).pipe(
      tap((response) => this.saveAuth(response)),
      map((response) => response.user),
    );
  }

  login(payload: LoginPayload): Observable<AuthUser> {
    return this.http.post<AuthResponse>('/users/auth/login/', payload).pipe(
      tap((response) => this.saveAuth(response)),
      map((response) => response.user),
    );
  }

  loadCurrentUser(): Observable<AuthUser | null> {
    if (!this.hasToken()) {
      this.currentUserSubject.next(null);
      return of(null);
    }

    return this.http.get<AuthUser>('/users/auth/me/').pipe(
      tap((user) => this.currentUserSubject.next(user)),
      catchError(() => {
        this.clearAuth();
        return of(null);
      }),
    );
  }

  logout(): Observable<void> {
    if (!this.hasToken()) {
      this.clearAuth();
      return of(undefined);
    }

    return this.http.post<{ message: string }>('/users/auth/logout/', {}).pipe(
      map(() => undefined),
      catchError(() => of(undefined)),
      tap(() => this.clearAuth()),
    );
  }

  private saveAuth(response: AuthResponse): void {
    localStorage.setItem(this.tokenKey, response.token);
    this.currentUserSubject.next(response.user);
  }

  private clearAuth(): void {
    localStorage.removeItem(this.tokenKey);
    this.currentUserSubject.next(null);
  }
}
