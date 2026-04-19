import { HttpClient } from '@angular/common/http';
import { Injectable, inject } from '@angular/core';
import { Observable, of } from 'rxjs';
import { catchError, map } from 'rxjs/operators';

@Injectable({ providedIn: 'root' })
export class TranslationService {
  private readonly http = inject(HttpClient);

  translate(text: string): Observable<string> {
    return this.http.post<{ translated?: string; error?: string }>('/translate/', { text }).pipe(
      map((res) => res.translated ?? 'Перевод недоступен'),
      catchError(() => of('Ошибка перевода')),
    );
  }
}
