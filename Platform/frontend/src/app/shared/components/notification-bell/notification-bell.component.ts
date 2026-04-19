import { AsyncPipe, DatePipe } from '@angular/common';
import { Component, inject } from '@angular/core';
import { Router } from '@angular/router';

import { AppNotification, NotificationService } from '../../../core/services/notification.service';

@Component({
  selector: 'app-notification-bell',
  standalone: true,
  imports: [AsyncPipe, DatePipe],
  templateUrl: './notification-bell.component.html',
  styleUrl: './notification-bell.component.css',
})
export class NotificationBellComponent {
  private readonly notificationService = inject(NotificationService);
  private readonly router = inject(Router);

  readonly unreadCount$ = this.notificationService.unreadCount$;
  isOpen = false;
  recent: AppNotification[] = [];

  toggle(): void {
    this.isOpen = !this.isOpen;
    if (this.isOpen) {
      this.notificationService.getPage(1, 5).subscribe({
        next: (page) => { this.recent = page.results; },
        error: () => {},
      });
    }
  }

  open(notif: AppNotification): void {
    if (!notif.is_read) {
      this.notificationService.markRead(notif.id).subscribe();
      notif.is_read = true;
    }
    this.isOpen = false;
    if (notif.link) {
      this.router.navigateByUrl(notif.link);
    }
  }

  goToAll(): void {
    this.isOpen = false;
    this.router.navigate(['/notifications']);
  }
}
