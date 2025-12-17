export const ssr = false;

import type { PageLoad } from "./$types";
import { loadMonitoringDashboardData } from "$lib/components/card/monitoring/getMonitoringDashboardData";
import { getRegistryPath, RegistryType } from "$lib/utils";
import { redirect } from "@sveltejs/kit";
import { getCookie, calculateTimeRange } from "$lib/components/trace/utils";
import type { TimeRange } from "$lib/components/trace/types";
import { getLabelFromValue } from "$lib/components/card/monitoring/utils";

/**
 * Monitoring page load function with error handling and time range management
 * Returns either successful data or error state using discriminated union
 */
export const load: PageLoad = async ({ parent, fetch }) => {
  const parentData = await parent();
  const { registryType, metadata } = parentData;

  if (registryType !== RegistryType.Model) {
    throw redirect(
      303,
      `/opsml/${getRegistryPath(registryType)}/card/${metadata.space}/${
        metadata.name
      }/${metadata.version}/card`
    );
  }

  try {
    const savedRange = getCookie("monitoring_range") || "15min";

    const { startTime, endTime, bucketInterval } =
      calculateTimeRange(savedRange);

    const timeRange: TimeRange = {
      label: getLabelFromValue(savedRange),
      value: savedRange,
      startTime,
      endTime,
      bucketInterval,
    };

    const dashboardData = await loadMonitoringDashboardData(fetch, parentData, {
      loadLLMRecords: false,
      loadAlerts: true,
      timeRange: timeRange,
    });

    return {
      status: "success" as const,
      data: dashboardData,
      metadata,
      registryType,
      initialTimeRange: timeRange,
    };
  } catch (err) {
    console.error("Monitoring page load error:", err);

    return {
      status: "error" as const,
      errorMessage:
        err instanceof Error ? err.message : "Failed to load monitoring data",
      metadata,
      registryType,
    };
  }
};
