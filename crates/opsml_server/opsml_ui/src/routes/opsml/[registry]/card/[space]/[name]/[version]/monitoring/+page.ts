export const ssr = false;

import type { PageLoad } from "./$types";
import { loadMonitoringDashboardData } from "$lib/components/card/monitoring/getMonitoringDashboardData";
import { getRegistryPath, RegistryType } from "$lib/utils";
import { redirect } from "@sveltejs/kit";
import { getCookie, calculateTimeRange } from "$lib/components/trace/utils";
import type { TimeRange } from "$lib/components/trace/types";

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
    // Get saved time range preference or default to 6 hours
    const savedRange = getCookie("monitoring_range") || "15min";

    // Calculate time range based on saved preference
    const { startTime, endTime, bucketInterval } =
      calculateTimeRange(savedRange);

    // Create TimeRange object for conversion
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

/**
 * Helper to get label from time range value
 * Maps the value back to a human-readable label
 */
function getLabelFromValue(value: string): string {
  const labelMap: Record<string, string> = {
    "15min-live": "Live (15min)",
    "15min": "Past 15 Minutes",
    "30min": "Past 30 Minutes",
    "1hour": "Past 1 Hour",
    "4hours": "Past 4 Hours",
    "12hours": "Past 12 Hours",
    "24hours": "Past 24 Hours",
    "7days": "Past 7 Days",
    "30days": "Past 30 Days",
  };
  return labelMap[value] || "Custom Range";
}
