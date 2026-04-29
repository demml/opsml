import { afterEach, describe, expect, it } from "vitest";
import { timeRangeState } from "./timeState.svelte";

const originalRange = { ...timeRangeState.selectedTimeRange };
const originalSignal = timeRangeState.refreshSignal;

afterEach(() => {
  timeRangeState.selectedTimeRange = { ...originalRange };
  timeRangeState.refreshSignal = originalSignal;
  timeRangeState.isRefreshing = false;
});

describe("timeRangeState.refresh", () => {
  it("recomputes relative ranges and increments the refresh signal", () => {
    timeRangeState.selectedTimeRange = {
      ...originalRange,
      value: "1hour",
    };

    const beforeSignal = timeRangeState.refreshSignal;
    timeRangeState.refresh();

    expect(timeRangeState.refreshSignal).toBe(beforeSignal + 1);
    expect(new Date(timeRangeState.selectedTimeRange.endTime).getTime()).toBeGreaterThan(
      new Date(timeRangeState.selectedTimeRange.startTime).getTime(),
    );
  });

  it("keeps custom start and end times intact", () => {
    timeRangeState.selectedTimeRange = {
      ...originalRange,
      value: "custom",
      startTime: "2026-01-01T00:00:00.000Z",
      endTime: "2026-01-01T01:00:00.000Z",
    };

    timeRangeState.refresh();

    expect(timeRangeState.selectedTimeRange.startTime).toBe("2026-01-01T00:00:00.000Z");
    expect(timeRangeState.selectedTimeRange.endTime).toBe("2026-01-01T01:00:00.000Z");
  });

  it("does not increment signal while isRefreshing", () => {
    timeRangeState.selectedTimeRange = { ...originalRange, value: "15min" };
    const beforeSignal = timeRangeState.refreshSignal;
    timeRangeState.isRefreshing = true;

    timeRangeState.refresh();

    expect(timeRangeState.refreshSignal).toBe(beforeSignal);
  });
});

describe("timeRangeState.updateTimeRange", () => {
  it("mutates selectedTimeRange without touching refreshSignal", () => {
    const beforeSignal = timeRangeState.refreshSignal;
    const newRange = {
      ...originalRange,
      value: "4hours",
      label: "Past 4 Hours",
    };

    timeRangeState.updateTimeRange(newRange);

    expect(timeRangeState.selectedTimeRange.value).toBe("4hours");
    expect(timeRangeState.refreshSignal).toBe(beforeSignal);
  });
});

describe("timeRangeState busy flag", () => {
  it("beginRefresh sets isRefreshing and endRefresh clears it", () => {
    expect(timeRangeState.isRefreshing).toBe(false);

    timeRangeState.beginRefresh();
    expect(timeRangeState.isRefreshing).toBe(true);

    timeRangeState.endRefresh();
    expect(timeRangeState.isRefreshing).toBe(false);
  });
});
