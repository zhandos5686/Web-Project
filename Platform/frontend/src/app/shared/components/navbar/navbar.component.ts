import { AsyncPipe } from '@angular/common';
import { Component, OnDestroy, OnInit, inject } from '@angular/core';
import { Router, RouterLink, RouterLinkActive } from '@angular/router';
import { Subscription } from 'rxjs';

import { AuthService } from '../../../core/services/auth.service';
import { NotificationService } from '../../../core/services/notification.service';
import { NotificationBellComponent } from '../notification-bell/notification-bell.component';

@Component({
  selector: 'app-navbar',
  standalone: true,
  imports: [AsyncPipe, RouterLink, RouterLinkActive, NotificationBellComponent],
  templateUrl: './navbar.component.html',
  styleUrl: './navbar.component.css',
})
export class NavbarComponent implements OnInit, OnDestroy {
  private readonly authService = inject(AuthService);
  private readonly notificationService = inject(NotificationService);
  private readonly router = inject(Router);

  readonly currentUser$ = this.authService.currentUser$;

  private authSub?: Subscription;
  private pollInterval?: ReturnType<typeof setInterval>;

  ngOnInit(): void {
    this.authSub = this.currentUser$.subscribe((user) => {
      if (user) {
        this.notificationService.refreshUnreadCount();
        if (!this.pollInterval) {
          this.pollInterval = setInterval(
            () => this.notificationService.refreshUnreadCount(),
            30_000,
          );
        }
      } else {
        this.stopPolling();
        this.notificationService.unreadCount$.next(0);
      }
    });
  }

  ngOnDestroy(): void {
    this.authSub?.unsubscribe();
    this.stopPolling();
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
