import { type TimeRange } from "../trace/types";
import { type DateTime } from "$lib/types";

// set default time range to 15 minutes
class TimeRangeState {
  selectedTimeRange = $state<TimeRange>({
    label: "Past 15 minutes",
    value: "15min",
    startTime: new Date(
      new Date().getTime() - 15 * 60 * 1000
    ).toISOString() as DateTime,
    endTime: new Date().toISOString() as DateTime,
    bucketInterval: "30 seconds",
  });

  updateTimeRange(newRange: TimeRange) {
    this.selectedTimeRange = newRange;
  }
}

export const timeRangeState = new TimeRangeState();
