import { DatePipe } from '@angular/common';
import { ChangeDetectorRef, Component, OnDestroy, OnInit, inject } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { catchError, finalize, forkJoin, of, Subscription } from 'rxjs';

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
  private readonly cdr = inject(ChangeDetectorRef);

  currentUser: AuthUser | null = null;
  private userSubscription?: Subscription;
  message = '';
  errorMessage = '';
  isLoading = false;
  isCreatingSlot = false;
  deletingSlotId: number | null = null;
  bookingSlotId: number | null = null;
  expandedBookedSlotId: number | null = null;

  slotForm = {
    starts_at: '',
    ends_at: '',
    meeting_url: '',
  };

  expandedSlotId: number | null = null;
  teacherSlots: LessonSlot[] = [];
  availableSlots: LessonSlot[] = [];
  myBookings: LiveBooking[] = [];

  get teacherAvailableSlots(): LessonSlot[] {
    return this.teacherSlots.filter((slot) => slot.is_available && !slot.booking);
  }

  get teacherBookedSlots(): LessonSlot[] {
    return this.teacherSlots.filter((slot) => !slot.is_available || !!slot.booking);
  }

  ngOnInit(): void {
    this.userSubscription = this.authService.currentUser$.subscribe((user) => {
      const previousRole = this.currentUser?.role;
      const previousId = this.currentUser?.id;
      this.currentUser = user;
      if (user && (previousRole !== user.role || previousId !== user.id)) {
        this.reload();
      }
      this.cdr.detectChanges();
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
    }).pipe(
      finalize(() => {
        this.isCreatingSlot = false;
        this.cdr.detectChanges();
      }),
    ).subscribe({
      next: (response) => {
        this.message = response.message;
        this.slotForm = { starts_at: '', ends_at: '', meeting_url: '' };
        this.teacherSlots = [response.slot, ...this.teacherSlots].sort(
          (first, second) => new Date(first.starts_at).getTime() - new Date(second.starts_at).getTime(),
        );
        this.cdr.detectChanges();
      },
      error: (error) => {
        this.errorMessage = error.error?.non_field_errors?.[0] || error.error?.message || 'Could not create slot.';
        this.cdr.detectChanges();
      },
    });
  }

  deleteSlot(slotId: number): void {
    this.clearMessages();
    this.deletingSlotId = slotId;
    this.bookingService.deleteSlot(slotId).pipe(
      finalize(() => {
        this.deletingSlotId = null;
        this.cdr.detectChanges();
      }),
    ).subscribe({
      next: (response) => {
        this.message = response.message;
        this.teacherSlots = this.teacherSlots.filter((slot) => slot.id !== slotId);
        if (this.expandedBookedSlotId === slotId) {
          this.expandedBookedSlotId = null;
        }
        this.cdr.detectChanges();
      },
      error: (error) => {
        this.errorMessage = error.error?.message || 'Could not delete this slot.';
        this.cdr.detectChanges();
      },
    });
  }

  bookSlot(slotId: number): void {
    this.clearMessages();
    this.bookingSlotId = slotId;
    this.bookingService.bookSlot(slotId).pipe(
      finalize(() => {
        this.bookingSlotId = null;
        this.cdr.detectChanges();
      }),
    ).subscribe({
      next: (response) => {
        this.message = response.message;
        if (response.booking) {
          this.myBookings = [response.booking, ...this.myBookings];
        }
        this.availableSlots = this.availableSlots.filter((slot) => slot.id !== slotId);
        this.cdr.detectChanges();
      },
      error: (error) => {
        this.errorMessage = error.error?.message || 'Could not book this slot.';
        this.cdr.detectChanges();
      },
    });
  }

  reload(): void {
    if (!this.currentUser) {
      this.isLoading = false;
      this.isCreatingSlot = false;
      this.deletingSlotId = null;
      this.bookingSlotId = null;
      this.expandedBookedSlotId = null;
      this.cdr.detectChanges();
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
    this.bookingService.getTeacherSlots().pipe(
      catchError(() => of([] as LessonSlot[])),
      finalize(() => {
        this.finishLoading();
        this.cdr.detectChanges();
      }),
    ).subscribe({
      next: (slots) => {
        this.teacherSlots = slots;
        this.cdr.detectChanges();
      },
    });
  }

  private loadStudentData(): void {
    forkJoin({
      slots: this.bookingService.getAvailableSlots().pipe(catchError(() => of([] as LessonSlot[]))),
      bookings: this.bookingService.getMyBookings().pipe(catchError(() => of([] as LiveBooking[]))),
    }).pipe(
      finalize(() => {
        this.finishLoading();
        this.cdr.detectChanges();
      }),
    ).subscribe({
      next: ({ slots, bookings }) => {
        this.availableSlots = slots;
        this.myBookings = bookings;
        this.cdr.detectChanges();
      },
    });
  }

  private finishLoading(): void {
    this.isLoading = false;

  }

  toggleBookedSlot(slotId: number): void {
    this.expandedBookedSlotId = this.expandedBookedSlotId === slotId ? null : slotId;
    this.cdr.detectChanges();
  }

  private toIsoDate(value: string): string {
    return value ? new Date(value).toISOString() : '';
  }

  private clearMessages(): void {
    this.message = '';
    this.errorMessage = '';
  }
}
