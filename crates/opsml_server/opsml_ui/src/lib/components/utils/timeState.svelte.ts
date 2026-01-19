import { type TimeRange } from "../trace/types";

class TimeRangeState {
  selectedTimeRange = $state<TimeRange | null>(null);

  updateTimeRange(newRange: TimeRange) {
    console.log("Updating time range to:", newRange);
    this.selectedTimeRange = newRange;

    console.log("Time range updated:", this.selectedTimeRange);
  }
}

export const timeRangeState = new TimeRangeState();
