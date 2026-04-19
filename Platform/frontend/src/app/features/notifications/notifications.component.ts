import { DatePipe } from '@angular/common';
import { Component, OnInit, inject } from '@angular/core';

import { AppNotification, NotificationPage, NotificationService } from '../../core/services/notification.service';

@Component({
  selector: 'app-notifications',
  standalone: true,
  imports: [DatePipe],
  templateUrl: './notifications.component.html',
  styleUrl: './notifications.component.css',
})
export class NotificationsComponent implements OnInit {
  private readonly notificationService = inject(NotificationService);

  notifications: AppNotification[] = [];
  totalCount = 0;
  currentPage = 1;
  readonly pageSize = 20;
  isLoading = false;
  hasMore = false;

  ngOnInit(): void {
    this.loadPage(1);
  }

  loadPage(page: number): void {
    this.isLoading = true;
    this.notificationService.getPage(page, this.pageSize).subscribe({
      next: (data: NotificationPage) => {
        this.notifications = page === 1 ? data.results : [...this.notifications, ...data.results];
        this.totalCount = data.count;
        this.currentPage = page;
        this.hasMore = data.next !== null;
        this.isLoading = false;
      },
      error: () => { this.isLoading = false; },
    });
  }

  loadMore(): void {
    this.loadPage(this.currentPage + 1);
  }

  markRead(notif: AppNotification): void {
    if (notif.is_read) { return; }
    this.notificationService.markRead(notif.id).subscribe(() => {
      notif.is_read = true;
    });
  }

  markAllRead(): void {
    this.notificationService.markAllRead().subscribe(() => {
      this.notifications.forEach((n) => { n.is_read = true; });
    });
  }

  remove(notif: AppNotification, event: Event): void {
    event.stopPropagation();
    this.notificationService.remove(notif.id).subscribe(() => {
      this.notifications = this.notifications.filter((n) => n.id !== notif.id);
      this.totalCount--;
    });
  }
}
