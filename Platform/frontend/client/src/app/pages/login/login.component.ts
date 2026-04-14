import { Component, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { Router } from '@angular/router';
import { AuthService } from '../../services/auth.service';

@Component({
  selector: 'app-login',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './login.component.html',
  styleUrl: './login.component.css'
})
export class LoginComponent {
  private authService = inject(AuthService);
  private router = inject(Router);

  username = '';
  password = '';
  errorMessage = '';
  successMessage = '';
  isLoading = false;

  onLogin(): void {
    this.errorMessage = '';
    this.successMessage = '';
    this.isLoading = true;

    console.log('Login button clicked');
    console.log('Username:', this.username);

    this.authService.login(this.username, this.password).subscribe({
      next: (response) => {
        console.log('Login success:', response);
        this.successMessage = 'Login successful';
        this.isLoading = false;
        this.router.navigate(['/catalog']);
      },
      error: (error) => {
        console.log('Login error:', error);
        this.errorMessage = 'Login failed. Check username, password, or backend server.';
        this.isLoading = false;
      }
    });
  }
}
