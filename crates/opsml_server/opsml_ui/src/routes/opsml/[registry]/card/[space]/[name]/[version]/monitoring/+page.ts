export const ssr = false;

import type { PageLoad } from "./$types";
import { TimeInterval } from "$lib/components/card/monitoring/types";
import { loadMonitoringDashboardData } from "$lib/components/card/monitoring/getMonitoringDashboardData";
import { getRegistryPath, RegistryType } from "$lib/utils";
import { redirect } from "@sveltejs/kit";

/**
 * Monitoring page load function with error handling
 * Returns either successful data or error state using discriminated union
 */
export const load: PageLoad = async ({ parent, fetch }) => {
  const { registryType, metadata } = await parent();

  // Redirect to card layout if registryType is not 'model'
  if (registryType !== RegistryType.Model) {
    throw redirect(
      303,
      `/opsml/${getRegistryPath(registryType)}/card/${metadata.space}/${
        metadata.name
      }/${metadata.version}`
    );
  }

  try {
    const dashboardData = await loadMonitoringDashboardData(
      fetch,
      await parent(),
      {
        initialTimeInterval: TimeInterval.SixHours,
        loadLLMRecords: false,
        loadAlerts: true,
      }
    );

    // Return success state with data
    return {
      status: "success" as const,
      data: dashboardData,
      metadata,
      registryType,
    };
  } catch (err) {
    console.error("Monitoring page load error:", err);

    // Return error state with minimal required data
    return {
      status: "error" as const,
      errorMessage:
        err instanceof Error ? err.message : "Failed to load monitoring data",
      metadata,
      registryType,
    };
  }
};
