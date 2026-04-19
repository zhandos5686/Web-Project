import { inject, Injectable } from '@angular/core';
import { Observable } from 'rxjs';

import { ApiService } from './api.service';

export interface LessonSlot {
  id: number;
  teacher: number;
  teacher_name: string;
  starts_at: string;
  ends_at: string;
  meeting_url: string;
  is_available: boolean;
  booking?: SlotBookingSummary | null;
}

export interface SlotBookingSummary {
  id: number;
  student_username: string;
  created_at: string;
}

export interface LiveBooking {
  id: number;
  slot: LessonSlot;
  student_username: string;
  created_at: string;
}

export interface SlotResponse {
  status: 'slot_created';
  message: string;
  slot: LessonSlot;
}

export interface BookingResponse {
  status: 'slot_booked' | 'already_booked' | 'forbidden';
  message: string;
  booking?: LiveBooking;
}

export interface CreateSlotPayload {
  starts_at: string;
  ends_at: string;
  meeting_url: string;
}

export interface DeleteSlotResponse {
  status: 'slot_deleted' | 'cannot_delete_booked_slot';
  message: string;
}

@Injectable({ providedIn: 'root' })
export class BookingService {
  private readonly api = inject(ApiService);

  createSlot(payload: CreateSlotPayload): Observable<SlotResponse> {
    return this.api.post<SlotResponse>('/booking/teacher/slots/', payload);
  }

  deleteSlot(slotId: number): Observable<DeleteSlotResponse> {
    return this.api.delete<DeleteSlotResponse>(`/booking/teacher/slots/${slotId}/`);
  }

  getTeacherSlots(): Observable<LessonSlot[]> {
    return this.api.get<LessonSlot[]>('/booking/teacher/my-slots/');
  }

  getTeacherBookings(): Observable<LiveBooking[]> {
    return this.api.get<LiveBooking[]>('/booking/teacher/bookings/');
  }

  getAvailableSlots(): Observable<LessonSlot[]> {
    return this.api.get<LessonSlot[]>('/booking/available-slots/');
  }

  bookSlot(slotId: number): Observable<BookingResponse> {
    return this.api.post<BookingResponse>(`/booking/book/${slotId}/`, {});
  }

  getMyBookings(): Observable<LiveBooking[]> {
    return this.api.get<LiveBooking[]>('/booking/my-bookings/');
  }
}
