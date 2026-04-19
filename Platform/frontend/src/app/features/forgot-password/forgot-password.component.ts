import { ChangeDetectorRef, Component, inject } from '@angular/core';
import { FormBuilder, ReactiveFormsModule, Validators } from '@angular/forms';
import { RouterLink } from '@angular/router';
import { finalize } from 'rxjs';

import { AuthService } from '../../core/services/auth.service';

@Component({
  selector: 'app-forgot-password',
  standalone: true,
  imports: [ReactiveFormsModule, RouterLink],
  templateUrl: './forgot-password.component.html',
  styleUrl: './forgot-password.component.css',
})
export class ForgotPasswordComponent {
  private readonly authService = inject(AuthService);
  private readonly formBuilder = inject(FormBuilder);
  private readonly cdr = inject(ChangeDetectorRef);

  isSubmitting = false;
  successMessage = '';
  errorMessage = '';
  resetUrl = '';

  readonly form = this.formBuilder.nonNullable.group({
    email: ['', [Validators.required, Validators.email]],
  });

  submit(): void {
    if (this.form.invalid) {
      this.form.markAllAsTouched();
      return;
    }

    this.isSubmitting = true;
    this.successMessage = '';
    this.errorMessage = '';
    this.resetUrl = '';
    this.cdr.detectChanges();

    this.authService.requestPasswordReset(this.form.getRawValue().email).pipe(
      finalize(() => {
        this.isSubmitting = false;
        this.cdr.detectChanges();
      }),
    ).subscribe({
      next: (response) => {
        this.successMessage = response.message || 'If an account with this email exists, a password reset link has been generated.';
        this.resetUrl = response.reset_url || '';
        this.cdr.detectChanges();
      },
      error: () => {
        this.errorMessage = 'Could not create a reset link. Check the email format and try again.';
        this.cdr.detectChanges();
      },
    });
  }
}
