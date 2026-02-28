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

  /** Incremented each time the user clicks the manual refresh button. */
  refreshSignal = $state(0);

  updateTimeRange(newRange: TimeRange) {
    this.selectedTimeRange = newRange;
  }

  /** Recalculates start/end for the current range value and triggers a refresh. */
  refresh() {
    const current = this.selectedTimeRange;
    if (!current) return;

    const now = new Date();
    const endTime = now.toISOString() as DateTime;
    let startTime: DateTime;

    switch (current.value) {
      case "15min-live":
      case "15min":
        startTime = new Date(now.getTime() - 15 * 60 * 1000).toISOString() as DateTime;
        break;
      case "30min":
        startTime = new Date(now.getTime() - 30 * 60 * 1000).toISOString() as DateTime;
        break;
      case "1hour":
        startTime = new Date(now.getTime() - 60 * 60 * 1000).toISOString() as DateTime;
        break;
      case "4hours":
        startTime = new Date(now.getTime() - 4 * 60 * 60 * 1000).toISOString() as DateTime;
        break;
      case "12hours":
        startTime = new Date(now.getTime() - 12 * 60 * 60 * 1000).toISOString() as DateTime;
        break;
      case "24hours":
        startTime = new Date(now.getTime() - 24 * 60 * 60 * 1000).toISOString() as DateTime;
        break;
      case "7days":
        startTime = new Date(now.getTime() - 7 * 24 * 60 * 60 * 1000).toISOString() as DateTime;
        break;
      case "30days":
        startTime = new Date(now.getTime() - 30 * 24 * 60 * 60 * 1000).toISOString() as DateTime;
        break;
      default:
        // Custom range — keep existing start/end, just signal a refresh
        this.refreshSignal += 1;
        return;
    }

    this.selectedTimeRange = { ...current, startTime, endTime };
    this.refreshSignal += 1;
  }
}

export const timeRangeState = new TimeRangeState();
