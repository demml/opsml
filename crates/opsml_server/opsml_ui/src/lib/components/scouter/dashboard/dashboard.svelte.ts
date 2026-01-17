// $lib/components/scouter/dashboard/dashboard.svelte.ts
import { debounce, getMaxDataPoints } from "$lib/utils";
import type { TimeRange } from "$lib/components/trace/types";

export class DashboardContext {
  timeRange = $state<TimeRange>(null!);
  maxDataPoints = $state<number>(getMaxDataPoints());
  isGlobalLoading = $state(false);

  constructor(initialTimeRange: TimeRange) {
    this.timeRange = initialTimeRange;
    this.initResizeListener();
  }

  updateTimeRange(range: TimeRange) {
    this.timeRange = range;
  }

  private initResizeListener() {
    if (typeof window === "undefined") return;

    const handleResize = debounce(() => {
      const newMax = getMaxDataPoints();
      if (newMax !== this.maxDataPoints) {
        this.maxDataPoints = newMax;
      }
    }, 400);

    window.addEventListener("resize", handleResize);

    // Cleanup logic if needed, though this context usually lives as long as the page
    return () => window.removeEventListener("resize", handleResize);
  }
}
