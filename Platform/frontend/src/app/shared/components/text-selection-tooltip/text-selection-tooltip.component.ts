import { ChangeDetectorRef, Component, HostListener, OnDestroy, OnInit, inject } from '@angular/core';
import { Subject, Subscription } from 'rxjs';
import { debounceTime, switchMap } from 'rxjs/operators';

import { TranslationService } from '../../../core/services/translation.service';

interface TooltipState {
  text: string;
  translation: string | null;
  x: number;
  y: number;
  above: boolean;
}

@Component({
  selector: 'app-text-selection-tooltip',
  standalone: true,
  templateUrl: './text-selection-tooltip.component.html',
  styleUrl: './text-selection-tooltip.component.css',
})
export class TextSelectionTooltipComponent implements OnInit, OnDestroy {
  private readonly translationService = inject(TranslationService);
  private readonly cdr = inject(ChangeDetectorRef);

  tooltip: TooltipState | null = null;

  private readonly selectionSubject = new Subject<{ text: string; x: number; y: number; above: boolean }>();
  private subscription!: Subscription;

  ngOnInit(): void {
    this.subscription = this.selectionSubject.pipe(
      debounceTime(300),
      switchMap(({ text, x, y, above }) => {
        this.tooltip = { text, translation: null, x, y, above };
        this.cdr.detectChanges();
        return this.translationService.translate(text);
      }),
    ).subscribe((translation) => {
      if (this.tooltip) {
        this.tooltip = { ...this.tooltip, translation };
        this.cdr.detectChanges();
      }
    });
  }

  ngOnDestroy(): void {
    this.subscription?.unsubscribe();
    this.selectionSubject.complete();
  }

  @HostListener('document:mouseup', ['$event'])
  onMouseUp(event: MouseEvent): void {
    const target = event.target as HTMLElement;
    if (target.closest('.sel-tooltip')) { return; }

    // Let the browser finalise the selection before reading it
    setTimeout(() => {
      const selection = window.getSelection();
      const text = selection?.toString().trim() ?? '';

      if (!text || text.length < 2 || text.length > 50) { return; }

      // Skip Cyrillic — already Russian
      if (/[\u0400-\u04FF]/.test(text)) { return; }

      if (!selection || selection.rangeCount === 0) { return; }

      const range = selection.getRangeAt(0);
      const rect = range.getBoundingClientRect();

      const tooltipH = 58;
      const tooltipW = 220;
      const above = rect.top > tooltipH + 16;

      const x = Math.min(
        Math.max(rect.left + rect.width / 2 - tooltipW / 2, 8),
        window.innerWidth - tooltipW - 8,
      );
      const y = above
        ? rect.top + window.scrollY - tooltipH - 10
        : rect.bottom + window.scrollY + 10;

      this.selectionSubject.next({ text, x, y, above });
    }, 0);
  }

  @HostListener('document:click', ['$event'])
  onDocumentClick(event: MouseEvent): void {
    const target = event.target as HTMLElement;
    if (!target.closest('.sel-tooltip')) {
      this.tooltip = null;
      this.cdr.detectChanges();
    }
  }

  close(): void {
    this.tooltip = null;
    this.cdr.detectChanges();
  }
}
