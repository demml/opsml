// $lib/components/scouter/genai/dashboard/genai.svelte.ts
import { getCustomDriftMetrics } from "$lib/server/scouter/drift/utils";
import type { DashboardContext } from "../dashboard/dashboard.svelte";
import type { CustomMetricDriftConfig, BinnedMetrics } from "./types";

interface CustomStoreProps {
  config: CustomMetricDriftConfig;
  ctx: DashboardContext; // Injected dependency
  initialMetrics: BinnedMetrics;
}

export function createCustomStore({
  config,
  ctx,
  initialMetrics,
}: CustomStoreProps) {
  // -- State --
  let isLoading = $state(false);
  let metrics = $state(initialMetrics);
  let currentMetricName = $state<string>("");

  const currentMetricsObj = $derived(metrics);

  const availableMetricNames = $derived(
    currentMetricsObj ? Object.keys(currentMetricsObj.metrics) : []
  );

  const currentMetricData = $derived(
    currentMetricsObj && currentMetricName
      ? currentMetricsObj.metrics[currentMetricName]
      : null
  );

  // -- Effects --

  // 1. React to TimeRange or Screen Size changes automatically
  $effect(() => {
    const range = ctx.timeRange;
    const points = ctx.maxDataPoints;

    fetchAll(range, points);
  });

  // 2. Ensure a valid metric name is selected
  $effect(() => {
    if (
      availableMetricNames.length > 0 &&
      !availableMetricNames.includes(currentMetricName)
    ) {
      currentMetricName = availableMetricNames[0];
    }
  });

  // -- Actions --
  async function fetchAll(range: typeof ctx.timeRange, maxPoints: number) {
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
