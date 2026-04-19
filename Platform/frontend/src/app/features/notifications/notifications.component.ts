import { DatePipe } from '@angular/common';
import { ChangeDetectorRef, Component, OnInit, inject } from '@angular/core';
import { catchError, finalize, of } from 'rxjs';

import { AppNotification, NotificationService } from '../../core/services/notification.service';

@Component({
  selector: 'app-notifications',
  standalone: true,
  imports: [DatePipe],
  templateUrl: './notifications.component.html',
  styleUrl: './notifications.component.css',
})
export class NotificationsComponent implements OnInit {
  private readonly notificationService = inject(NotificationService);
  private readonly cdr = inject(ChangeDetectorRef);

  notifications: AppNotification[] = [];
  isLoading = false;
  message = '';
  errorMessage = '';

  ngOnInit(): void {
    this.loadNotifications();
  }

  loadNotifications(): void {
    this.isLoading = true;
    this.message = '';
    this.errorMessage = '';
    this.notificationService.getNotifications().pipe(
      catchError(() => {
        this.errorMessage = 'Could not load notifications.';
        return of([] as AppNotification[]);
      }),
      finalize(() => {
        this.isLoading = false;
        this.cdr.detectChanges();
      }),
    ).subscribe((notifications) => {
      this.notifications = notifications;
      this.cdr.detectChanges();
    });
  }

  markRead(notification: AppNotification): void {
    if (notification.is_read) {
      return;
    }

    this.notificationService.markRead(notification.id).subscribe({
      next: (response) => {
        this.notifications = this.notifications.map((item) =>
          item.id === response.notification.id ? response.notification : item,
        );
        this.cdr.detectChanges();
      },
      error: () => {
        this.errorMessage = 'Could not mark notification as read.';
        this.cdr.detectChanges();
      },
    });
  }

  markAllRead(): void {
    this.notificationService.markAllRead().subscribe({
      next: () => {
        this.notifications = this.notifications.map((n) => ({ ...n, is_read: true }));
        this.notificationService.unreadCount$.next(0);
        this.cdr.detectChanges();
      },
      error: () => {
        this.errorMessage = 'Could not mark all notifications as read.';
        this.cdr.detectChanges();
      },
    });
  }

  deleteNotification(notificationId: number): void {
    this.notificationService.deleteNotification(notificationId).subscribe({
      next: () => {
        this.notifications = this.notifications.filter((n) => n.id !== notificationId);
        this.cdr.detectChanges();
      },
      error: () => {
        this.errorMessage = 'Could not delete notification.';
        this.cdr.detectChanges();
      },
    });
  }
}
