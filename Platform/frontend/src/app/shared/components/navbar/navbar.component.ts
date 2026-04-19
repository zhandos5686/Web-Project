import { Component, OnDestroy, OnInit, inject } from '@angular/core';
import { AsyncPipe, DatePipe } from '@angular/common';
import { Router } from '@angular/router';
import { RouterLink, RouterLinkActive } from '@angular/router';
import { interval, Subscription } from 'rxjs';

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
  private authSubscription?: Subscription;
  private pollingSubscription?: Subscription;

  readonly currentUser$ = this.authService.currentUser$;
  notifications: AppNotification[] = [];
  unreadCount = 0;
  isNotificationDropdownOpen = false;

  ngOnInit(): void {
    this.authSubscription = this.authService.currentUser$.subscribe((user) => {
      this.pollingSubscription?.unsubscribe();
      this.isNotificationDropdownOpen = false;
      if (user) {
        this.loadNotificationPreview();
        this.pollingSubscription = interval(30000).subscribe(() => this.loadNotificationPreview());
      } else {
        this.notifications = [];
        this.unreadCount = 0;
      }
    });
  }

  ngOnDestroy(): void {
    this.authSubscription?.unsubscribe();
    this.pollingSubscription?.unsubscribe();
  }

  toggleNotifications(): void {
    this.isNotificationDropdownOpen = !this.isNotificationDropdownOpen;
    if (this.isNotificationDropdownOpen) {
      this.loadNotificationPreview();
    }
  }

  markRead(notification: AppNotification): void {
    if (notification.is_read) {
      return;
    }

    this.notificationService.markRead(notification.id).subscribe((response) => {
      this.notifications = this.notifications.map((item) =>
        item.id === response.notification.id ? response.notification : item,
      );
      this.unreadCount = Math.max(this.unreadCount - 1, 0);
    });
  }

  closeNotifications(): void {
    this.isNotificationDropdownOpen = false;
  }

  logout(): void {
    this.authService.logout().subscribe(() => {
      this.notifications = [];
      this.unreadCount = 0;
      this.isNotificationDropdownOpen = false;
      this.router.navigate(['/catalog']);
    });
  }

  private loadNotificationPreview(): void {
    this.notificationService.getUnreadCount().subscribe((response) => {
      this.unreadCount = response.unread_count;
    });
    this.notificationService.getNotifications().subscribe((notifications) => {
      this.notifications = notifications.slice(0, 5);
    });
  }
}
