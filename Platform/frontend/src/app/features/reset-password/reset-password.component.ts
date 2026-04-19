import { ChangeDetectorRef, Component, inject } from '@angular/core';
import { FormBuilder, ReactiveFormsModule, Validators } from '@angular/forms';
import { ActivatedRoute, RouterLink } from '@angular/router';
import { finalize } from 'rxjs';

import { AuthService } from '../../core/services/auth.service';

@Component({
  selector: 'app-reset-password',
  standalone: true,
  imports: [ReactiveFormsModule, RouterLink],
  templateUrl: './reset-password.component.html',
  styleUrl: './reset-password.component.css',
})
export class ResetPasswordComponent {
  private readonly authService = inject(AuthService);
  private readonly formBuilder = inject(FormBuilder);
  private readonly route = inject(ActivatedRoute);
  private readonly cdr = inject(ChangeDetectorRef);

  readonly uid = this.route.snapshot.queryParamMap.get('uid') || '';
  readonly token = this.route.snapshot.queryParamMap.get('token') || '';

  isSubmitting = false;
  successMessage = '';
  errorMessage = this.uid && this.token ? '' : 'This password reset link is missing required data.';

  readonly form = this.formBuilder.nonNullable.group({
    newPassword: ['', [Validators.required, Validators.minLength(8)]],
    confirmPassword: ['', [Validators.required]],
  });

  submit(): void {
    if (!this.uid || !this.token) {
      this.errorMessage = 'This password reset link is invalid.';
      this.cdr.detectChanges();
      return;
    }

    if (this.form.invalid) {
      this.form.markAllAsTouched();
      return;
    }

    const formValue = this.form.getRawValue();
    if (formValue.newPassword !== formValue.confirmPassword) {
      this.errorMessage = 'Passwords do not match.';
      this.cdr.detectChanges();
      return;
    }

    this.isSubmitting = true;
    this.successMessage = '';
    this.errorMessage = '';
    this.cdr.detectChanges();

    this.authService.resetPassword({
      uid: this.uid,
      token: this.token,
      new_password: formValue.newPassword,
      confirm_password: formValue.confirmPassword,
    }).pipe(
      finalize(() => {
        this.isSubmitting = false;
        this.cdr.detectChanges();
      }),
    ).subscribe({
      next: (response) => {
        this.successMessage = response.message;
        this.form.reset();
        this.cdr.detectChanges();
      },
      error: (error) => {
        const errors = error.error || {};
        this.errorMessage =
          errors.token?.[0] ||
          errors.uid?.[0] ||
          errors.new_password?.[0] ||
          errors.confirm_password?.[0] ||
          errors.non_field_errors?.[0] ||
          'Could not reset password. The link may be invalid or expired.';
        this.cdr.detectChanges();
      },
    });
  }
}
