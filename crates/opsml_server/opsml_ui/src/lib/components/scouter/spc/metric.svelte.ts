// $lib/components/scouter/genai/dashboard/genai.svelte.ts
import { getSpcDriftMetrics } from "$lib/server/scouter/drift/utils";
import type { DashboardContext } from "../dashboard/dashboard.svelte";
import type { BinnedSpcFeatureMetrics, SpcDriftConfig } from "./types";

interface SpcStoreProps {
  config: SpcDriftConfig;
  ctx: DashboardContext; // Injected dependency
  initialMetrics: BinnedSpcFeatureMetrics;
}

export function createSpcStore({ config, ctx, initialMetrics }: SpcStoreProps) {
  // -- State --
  let isLoading = $state(false);
  let metrics = $state(initialMetrics);
  let currentMetricName = $state<string>("");

  const currentMetricsObj = $derived(metrics);

  const availableMetricNames = $derived(
    currentMetricsObj ? Object.keys(currentMetricsObj.features) : []
  );

  const currentMetricData = $derived(
    currentMetricsObj && currentMetricName
      ? currentMetricsObj.features[currentMetricName]
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
      const newMetrics = await getSpcDriftMetrics(
        fetch,
        config.space,
        config.uid,
        range,
        maxPoints
      );

      metrics = newMetrics;
    } catch (e) {
      console.error("Failed to refresh GenAI data", e);
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
