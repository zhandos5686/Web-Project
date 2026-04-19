import { AsyncPipe, DatePipe } from '@angular/common';
import { Component, OnDestroy, OnInit, inject } from '@angular/core';
import { Router, RouterLink, RouterLinkActive } from '@angular/router';
import { Subscription } from 'rxjs';

import { AuthService } from '../../../core/services/auth.service';
import { AppNotification, NotificationService } from '../../../core/services/notification.service';

@Component({
  selector: 'app-navbar',
  standalone: true,
  imports: [AsyncPipe, DatePipe, RouterLink, RouterLinkActive],
  templateUrl: './navbar.component.html',
  styleUrl: './navbar.component.css',
})
export class NavbarComponent implements OnInit, OnDestroy {
  private readonly authService = inject(AuthService);
  private readonly notificationService = inject(NotificationService);
  private readonly router = inject(Router);

  readonly currentUser$ = this.authService.currentUser$;
  notifications: AppNotification[] = [];
  unreadCount = 0;
  isNotificationDropdownOpen = false;

  private authSub?: Subscription;
  private unreadSub?: Subscription;
  private pollInterval?: ReturnType<typeof setInterval>;

  ngOnInit(): void {
    this.unreadSub = this.notificationService.unreadCount$.subscribe((count) => {
      this.unreadCount = count;
    });

    this.authSub = this.currentUser$.subscribe((user) => {
      if (user) {
        this.notificationService.refreshUnreadCount();
        if (!this.pollInterval) {
          this.pollInterval = setInterval(() => this.notificationService.refreshUnreadCount(), 30_000);
        }
      } else {
        this.stopPolling();
        this.notificationService.unreadCount$.next(0);
        this.notifications = [];
        this.isNotificationDropdownOpen = false;
      }
    });
  }

  ngOnDestroy(): void {
    this.authSub?.unsubscribe();
    this.unreadSub?.unsubscribe();
    this.stopPolling();
  }

  toggleNotifications(): void {
    this.isNotificationDropdownOpen = !this.isNotificationDropdownOpen;
    if (this.isNotificationDropdownOpen) {
      this.notificationService.getNotifications().subscribe({
        next: (notifications) => { this.notifications = notifications.slice(0, 5); },
        error: () => {},
      });
    }
  }

  markRead(notification: AppNotification): void {
    if (notification.is_read) { return; }
    this.notificationService.markRead(notification.id).subscribe({
      next: (response) => {
        this.notifications = this.notifications.map((n) =>
          n.id === response.notification.id ? response.notification : n,
        );
      },
      error: () => {},
    });
  }

  closeNotifications(): void {
    this.isNotificationDropdownOpen = false;
  }

  logout(): void {
    this.authService.logout().subscribe(() => {
      this.router.navigate(['/catalog']);
    });
  }

  private stopPolling(): void {
    if (this.pollInterval) {
      clearInterval(this.pollInterval);
      this.pollInterval = undefined;
    }
  }
}
