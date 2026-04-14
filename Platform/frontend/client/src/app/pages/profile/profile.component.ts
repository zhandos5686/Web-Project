import { Component, inject, OnInit, ChangeDetectorRef } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { ProfileService } from '../../services/profile.service';
import { Profile } from '../../interfaces/profile';

@Component({
  selector: 'app-profile',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './profile.component.html',
  styleUrl: './profile.component.css'
})
export class ProfileComponent implements OnInit {
  private profileService = inject(ProfileService);
  private cdr = inject(ChangeDetectorRef);

  profile: Profile = {
    id: 0,
    user: 0,
    full_name: '',
    phone: '',
    grade_level: '',
    bio: ''
  };

  isLoading = true;
  errorMessage = '';
  successMessage = '';

  ngOnInit(): void {
    console.log('ProfileComponent init');
    this.loadProfile();
  }

  loadProfile(): void {
    console.log('loadProfile started');
    this.isLoading = true;
    this.errorMessage = '';
    this.successMessage = '';

    this.profileService.getProfile().subscribe({
      next: (data) => {
        console.log('profile response:', data);
        this.profile = data;
        this.isLoading = false;
        this.cdr.detectChanges();
      },
      error: (err) => {
        console.log('profile error:', err);
        this.errorMessage = 'Failed to load profile. Please login first.';
        this.isLoading = false;
        this.cdr.detectChanges();
      }
    });
  }

  saveProfile(): void {
    this.errorMessage = '';
    this.successMessage = '';

    this.profileService.updateProfile(this.profile).subscribe({
      next: (data) => {
        console.log('profile update response:', data);
        this.profile = data;
        this.successMessage = 'Profile updated successfully';
        this.cdr.detectChanges();
      },
      error: (err) => {
        console.log('profile update error:', err);
        this.errorMessage = 'Failed to update profile';
        this.cdr.detectChanges();
      }
    });
  }
}
