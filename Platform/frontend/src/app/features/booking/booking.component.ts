import { DatePipe } from '@angular/common';
import { Component, OnDestroy, OnInit, inject } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { Subscription } from 'rxjs';

import { AuthService, AuthUser } from '../../core/services/auth.service';
import { BookingService, LessonSlot, LiveBooking } from '../../core/services/booking.service';

@Component({
  selector: 'app-booking',
  standalone: true,
  imports: [DatePipe, FormsModule],
  templateUrl: './booking.component.html',
  styleUrl: './booking.component.css',
})
export class BookingComponent implements OnInit, OnDestroy {
  private readonly authService = inject(AuthService);
  private readonly bookingService = inject(BookingService);

  currentUser: AuthUser | null = null;
  private userSubscription?: Subscription;
  message = '';
  errorMessage = '';
  isLoading = false;
  isCreatingSlot = false;
  deletingSlotId: number | null = null;
  bookingSlotId: number | null = null;

  slotForm = {
    starts_at: '',
    ends_at: '',
    meeting_url: '',
  };

  teacherSlots: LessonSlot[] = [];
  teacherBookings: LiveBooking[] = [];
  availableSlots: LessonSlot[] = [];
  myBookings: LiveBooking[] = [];

  ngOnInit(): void {
    this.userSubscription = this.authService.currentUser$.subscribe((user) => {
      const previousRole = this.currentUser?.role;
      const previousId = this.currentUser?.id;
      this.currentUser = user;
      if (user && (previousRole !== user.role || previousId !== user.id)) {
        this.reload();
      }
    });
  }

  ngOnDestroy(): void {
    this.userSubscription?.unsubscribe();
  }

  createSlot(): void {
    if (this.isCreatingSlot) {
      return;
    }

    this.clearMessages();
    this.isCreatingSlot = true;
    this.bookingService.createSlot({
      starts_at: this.toIsoDate(this.slotForm.starts_at),
      ends_at: this.toIsoDate(this.slotForm.ends_at),
      meeting_url: this.slotForm.meeting_url,
    }).subscribe({
      next: (response) => {
        this.message = response.message;
        this.slotForm = { starts_at: '', ends_at: '', meeting_url: '' };
        this.reload();
      },
      error: (error) => {
        this.errorMessage = error.error?.non_field_errors?.[0] || error.error?.message || 'Could not create slot.';
        this.isCreatingSlot = false;
      },
    });
  }

  deleteSlot(slotId: number): void {
    this.clearMessages();
    this.deletingSlotId = slotId;
    this.bookingService.deleteSlot(slotId).subscribe({
      next: (response) => {
        this.message = response.message;
        this.reload();
      },
      error: (error) => {
        this.errorMessage = error.error?.message || 'Could not delete this slot.';
        this.deletingSlotId = null;
      },
    });
  }

  bookSlot(slotId: number): void {
    this.clearMessages();
    this.bookingSlotId = slotId;
    this.bookingService.bookSlot(slotId).subscribe({
      next: (response) => {
        this.message = response.message;
        this.reload();
      },
      error: (error) => {
        this.errorMessage = error.error?.message || 'Could not book this slot.';
        this.bookingSlotId = null;
      },
    });
  }

  reload(): void {
    if (!this.currentUser) {
      this.isLoading = false;
      this.isCreatingSlot = false;
      this.deletingSlotId = null;
      this.bookingSlotId = null;
      return;
    }

    this.isLoading = true;
    if (this.currentUser.role === 'teacher') {
      this.loadTeacherData();
    } else {
      this.loadStudentData();
    }
  }

  private loadTeacherData(): void {
    this.bookingService.getTeacherSlots().subscribe({
      next: (slots) => this.teacherSlots = slots,
      error: () => this.errorMessage = 'Could not load teacher slots.',
    });
    this.bookingService.getTeacherBookings().subscribe({
      next: (bookings) => this.teacherBookings = bookings,
      error: () => {
        this.errorMessage = 'Could not load teacher bookings.';
        this.finishLoading();
      },
      complete: () => this.finishLoading(),
    });
  }

  private loadStudentData(): void {
    this.bookingService.getAvailableSlots().subscribe({
      next: (slots) => this.availableSlots = slots,
      error: () => this.errorMessage = 'Could not load available slots.',
    });
    this.bookingService.getMyBookings().subscribe({
      next: (bookings) => this.myBookings = bookings,
      error: () => {
        this.errorMessage = 'Could not load your booked lessons.';
        this.finishLoading();
      },
      complete: () => this.finishLoading(),
    });
  }

  private finishLoading(): void {
    this.isLoading = false;
    this.isCreatingSlot = false;
    this.deletingSlotId = null;
    this.bookingSlotId = null;
  }

  private toIsoDate(value: string): string {
    return value ? new Date(value).toISOString() : '';
  }

  private clearMessages(): void {
    this.message = '';
    this.errorMessage = '';
  }
}
