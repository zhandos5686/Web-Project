import { Injectable, inject } from '@angular/core';
import { BehaviorSubject, Observable } from 'rxjs';
import { tap } from 'rxjs/operators';

import { ApiService } from './api.service';

export interface AppNotification {
  id: number;
  type: string;
  title: string;
  message: string;
  link: string;
  is_read: boolean;
  created_at: string;
  extra_data: Record<string, unknown>;
}

export interface NotificationPage {
  count: number;
  next: string | null;
  previous: string | null;
  results: AppNotification[];
}

@Injectable({ providedIn: 'root' })
export class NotificationService {
  private readonly api = inject(ApiService);

  readonly unreadCount$ = new BehaviorSubject<number>(0);

  refreshUnreadCount(): void {
    this.api.get<{ count: number }>('/notifications/unread-count/').subscribe({
      next: (res) => this.unreadCount$.next(res.count),
      error: () => {},
    });
  }

  getPage(page = 1, pageSize = 20): Observable<NotificationPage> {
    return this.api.get<NotificationPage>(`/notifications/?page=${page}&page_size=${pageSize}`);
  }

  markRead(id: number): Observable<AppNotification> {
    return this.api.patch<AppNotification>(`/notifications/${id}/mark_read/`, {}).pipe(
      tap(() => {
        const c = this.unreadCount$.value;
        if (c > 0) this.unreadCount$.next(c - 1);
      }),
    );
  }

  markAllRead(): Observable<{ marked_read: number }> {
    return this.api.patch<{ marked_read: number }>('/notifications/mark_all_read/', {}).pipe(
      tap(() => this.unreadCount$.next(0)),
    );
  }

  remove(id: number): Observable<void> {
    return this.api.delete<void>(`/notifications/${id}/`);
  }
}
