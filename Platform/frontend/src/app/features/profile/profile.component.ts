import { AsyncPipe } from '@angular/common';
import { Component, inject } from '@angular/core';
import { RouterLink } from '@angular/router';

import { AuthService } from '../../core/services/auth.service';

@Component({
  selector: 'app-profile',
  standalone: true,
  imports: [AsyncPipe, RouterLink],
  template: `
    <section class="page simple-page">
      <div class="page-heading">
        <h1>Profile</h1>
        <p>This page uses the current-user endpoint to show the authenticated account and role.</p>
      </div>

      @if (currentUser$ | async; as user) {
        <article class="content-card profile-card">
          <div class="card-title-row">
            <div>
              <h2>{{ user.username }}</h2>
              <p>{{ user.email }}</p>
            </div>
            <span class="status-pill">{{ user.role }}</span>
          </div>

          <div class="profile-field">
            <strong>Bio</strong>
            <span>{{ user.bio || 'No bio added yet.' }}</span>
          </div>

          @if (user.role === 'teacher') {
            <a class="primary-link" routerLink="/teacher">Open teacher dashboard</a>
          } @else {
            <a class="primary-link" routerLink="/my-courses">Open my courses</a>
          }
        </article>
      }
    </section>
  `,
})
export class ProfileComponent {
  private readonly authService = inject(AuthService);

  readonly currentUser$ = this.authService.currentUser$;
}
