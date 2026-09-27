/** How much a reading moved over one window of time. */
export interface Trend {
  /** Size of the window in hours. 3 is three hours, 72 is three days. */
  hours: number;
  /** Averaged value at the start of the window. Null when nothing was logged. */
  start: number | null;
  /** Averaged value at the end of the window. Null when nothing was logged. */
  end: number | null;
  /** end - start. Null when either side had nothing to average, usually because the pump never ran. */
  change: number | null;
}

/**
 * Trends are optional. An install without a database answers available=false and the panels
 * simply show the readings on their own.
 */
export interface TrendResponse {
  available: boolean;
  /** Keyed by sensor id for temperature, or by reading name (ph, orp) for chemistry. */
  trends: { [key: string]: Trend[] };
}

export const NO_TRENDS: TrendResponse = { available: false, trends: {} };
