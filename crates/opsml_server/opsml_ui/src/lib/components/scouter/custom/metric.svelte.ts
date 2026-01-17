// $lib/components/scouter/custom/custom.svelte.ts
import { getCustomDriftMetrics } from "$lib/components/scouter/custom/utils";
import type { DashboardContext } from "../dashboard/dashboard.svelte";
import type { CustomMetricDriftConfig, BinnedMetrics } from "./types";

interface CustomStoreProps {
  config: CustomMetricDriftConfig;
  ctx: DashboardContext;
  initialMetrics: BinnedMetrics | null; // Changed to allow null for client-side switches
}

export function createCustomStore({
  config,
  ctx,
  initialMetrics,
}: CustomStoreProps) {
  // -- State --
  let isLoading = $state(false);
  // Default to empty object if null, fetchAll will populate it shortly
  let metrics = $state<BinnedMetrics>(initialMetrics || { metrics: {} });
  let currentMetricName = $state<string>("");

  const currentMetricsObj = $derived(metrics);

  const availableMetricNames = $derived(
    currentMetricsObj && currentMetricsObj.metrics
      ? Object.keys(currentMetricsObj.metrics)
      : []
  );

  const currentMetricData = $derived(
    currentMetricsObj && currentMetricName && currentMetricsObj.metrics
      ? currentMetricsObj.metrics[currentMetricName]
      : null
  );

  // -- Effects --

  // 1. React to TimeRange, Screen Size, OR missing initial data
  $effect(() => {
    const range = ctx.timeRange;
    const points = ctx.maxDataPoints;

    // Logic: If we have no keys (empty metrics) OR the context changed, we fetch.
    // This covers the initial client-side switch (empty metrics) AND time updates.
    const hasData = Object.keys(metrics.metrics).length > 0;

    // We fetch if we don't have data, or if the user actively changes the time/window
    // Note: We might want a separate flag for "isInitialMount" to avoid double fetching
    // if initialMetrics WERE provided. But checking hasData is a safe simple heuristic.
    if (!hasData || (range && points)) {
      fetchAll(range, points);
    }
  });

  // 2. Ensure a valid metric name is selected
  $effect(() => {
    if (
      availableMetricNames.length > 0 &&
      !availableMetricNames.includes(currentMetricName)
    ) {
      // Default to the first metric available
      currentMetricName = availableMetricNames[0];
    }
  });

  // -- Actions --
  async function fetchAll(range: typeof ctx.timeRange, maxPoints: number) {
    // Prevent overlapping fetches or fetching if unnecessary
    if (isLoading) return;

    isLoading = true;
    try {
      const newMetrics = await getCustomDriftMetrics(
        fetch,
        config.space,
        config.uid,
        range,
        maxPoints
      );

      metrics = newMetrics;
    } catch (e) {
      console.error("Failed to refresh Custom data", e);
    } finally {
      isLoading = false;
    }
  }

  return {
    get isLoading() {
      return isLoading;
    },
    get currentMetricName() {
      return currentMetricName;
    },
    set currentMetricName(v) {
      currentMetricName = v;
    },
    get availableMetricNames() {
      return availableMetricNames;
    },
    get currentMetricData() {
      return currentMetricData;
    },
  };
}
