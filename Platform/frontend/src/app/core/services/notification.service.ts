import { inject, Injectable } from '@angular/core';
import { Observable } from 'rxjs';

import { ApiService } from './api.service';

export interface AppNotification {
  id: number;
  title: string;
  message: string;
  type: 'booking_created' | 'task_submitted' | 'task_reviewed';
  is_read: boolean;
  metadata: Record<string, unknown>;
  created_at: string;
}

export interface UnreadCountResponse {
  unread_count: number;
}

export interface MarkReadResponse {
  status: 'marked_read';
  message: string;
  notification: AppNotification;
}

export interface MarkAllReadResponse {
  status: 'all_marked_read';
  message: string;
  updated_count: number;
}

export interface DeleteNotificationResponse {
  status: 'deleted';
  message: string;
}

@Injectable({ providedIn: 'root' })
export class NotificationService {
  private readonly api = inject(ApiService);

  getNotifications(): Observable<AppNotification[]> {
    return this.api.get<AppNotification[]>('/notifications/');
  }

  getUnreadCount(): Observable<UnreadCountResponse> {
    return this.api.get<UnreadCountResponse>('/notifications/unread-count/');
  }

  markRead(notificationId: number): Observable<MarkReadResponse> {
    return this.api.post<MarkReadResponse>(`/notifications/${notificationId}/mark-read/`, {});
  }

  markAllRead(): Observable<MarkAllReadResponse> {
    return this.api.post<MarkAllReadResponse>('/notifications/mark-all-read/', {});
  }

  deleteNotification(notificationId: number): Observable<DeleteNotificationResponse> {
    return this.api.delete<DeleteNotificationResponse>(`/notifications/${notificationId}/`);
  }
}
