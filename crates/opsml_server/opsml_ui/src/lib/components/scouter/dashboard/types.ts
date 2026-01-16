import type { TimeRange } from "$lib/components/trace/types";

/**
 * Base interface for all profile-specific dashboard state
 */
export interface BaseProfileDashboardState {
  isUpdating: boolean;
  selectedTimeRange: TimeRange; // Non-nullable
  maxDataPoints: number;

  checkScreenSize(): Promise<void>;
  handleTimeRangeChange(range: TimeRange): Promise<void>;
}
/**
 * Common props passed to all profile dashboards
 */
export interface BaseProfileDashboardProps {
  uid: string;
  initialTimeRange: TimeRange;
}
