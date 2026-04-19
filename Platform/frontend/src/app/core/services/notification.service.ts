import { inject, Injectable } from '@angular/core';
import { BehaviorSubject, Observable } from 'rxjs';
import { tap } from 'rxjs/operators';

import { ApiService } from './api.service';

export interface AppNotification {
  id: number;
  title: string;
  message: string;
  type: string;
  is_read: boolean;
  metadata: Record<string, unknown>;
  created_at: string;
}

export interface UnreadCountResponse {
  unread_count: number;
}

export interface MarkReadResponse {
  status: string;
  message: string;
  notification: AppNotification;
}

export interface MarkAllReadResponse {
  status: string;
  message: string;
  updated_count: number;
}

export interface DeleteNotificationResponse {
  status: string;
  message: string;
}

@Injectable({ providedIn: 'root' })
export class NotificationService {
  private readonly api = inject(ApiService);

  readonly unreadCount$ = new BehaviorSubject<number>(0);

  refreshUnreadCount(): void {
    this.api.get<UnreadCountResponse>('/notifications/unread-count/').subscribe({
      next: (res) => this.unreadCount$.next(res.unread_count),
      error: () => {},
    });
  }

  getNotifications(): Observable<AppNotification[]> {
    return this.api.get<AppNotification[]>('/notifications/');
  }

  markRead(notificationId: number): Observable<MarkReadResponse> {
    return this.api.post<MarkReadResponse>(`/notifications/${notificationId}/mark-read/`, {}).pipe(
      tap(() => {
        const c = this.unreadCount$.value;
        if (c > 0) this.unreadCount$.next(c - 1);
      }),
    );
  }

  markAllRead(): Observable<MarkAllReadResponse> {
    return this.api.post<MarkAllReadResponse>('/notifications/mark-all-read/', {}).pipe(
      tap(() => this.unreadCount$.next(0)),
    );
  }

  deleteNotification(notificationId: number): Observable<DeleteNotificationResponse> {
    return this.api.delete<DeleteNotificationResponse>(`/notifications/${notificationId}/`);
  }
}
