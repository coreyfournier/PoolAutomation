import { Component, Input } from '@angular/core';
import { Trend } from './trend';

/**
 * Shows how far a reading has moved over each window the backend reported.
 * The arrow and the sign carry the meaning, the color only reinforces it.
 */
@Component({
  selector: 'app-trend-indicator',
  templateUrl: './trend-indicator.component.html',
  styleUrls: ['./trend-indicator.component.css']
})
export class TrendIndicatorComponent {
  /** Windows to show. Null or empty renders nothing at all. */
  @Input() trends: Trend[] | null = null;
  /** Digits to show, in the DecimalPipe format. Chemistry wants more than temperature does. */
  @Input() digits: string = '1.1-1';
  /** Unit to show after the change. Optional, the panel usually shows it already. */
  @Input() unit: string = '';

  /** A window with nothing to compare against is left out rather than shown as a zero. */
  get measured(): Trend[] {
    return (this.trends ?? []).filter(t => t.change != null);
  }

  direction(trend: Trend): string {
    if (trend.change == null || trend.change === 0) {
      return 'flat';
    }
    return trend.change > 0 ? 'rising' : 'falling';
  }

  arrow(trend: Trend): string {
    switch (this.direction(trend)) {
      case 'rising': return '\u25B2';
      case 'falling': return '\u25BC';
      default: return '\u2013';
    }
  }

  /** The arrow already says which way it went, so the number itself is unsigned. */
  magnitude(trend: Trend): number {
    return Math.abs(trend.change ?? 0);
  }

  /** 3 stays as 3h, 72 becomes 3d. */
  window(trend: Trend): string {
    if (trend.hours >= 24 && trend.hours % 24 === 0) {
      return `${trend.hours / 24}d`;
    }
    return `${trend.hours}h`;
  }

  /** Hover text, so the two averages behind the number are not a mystery. */
  describe(trend: Trend): string {
    return `${trend.start} to ${trend.end} over the last ${this.window(trend)}, while the pump was running`;
  }
}
