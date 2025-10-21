// Base data for monitoring page.
// This needs to be client-side because we need to calculate max data points from window size
export const ssr = false;

import type { PageLoad } from "./$types";
import { TimeInterval } from "$lib/components/card/monitoring/types";
import { loadMonitoringDashboardData } from "$lib/components/card/monitoring/getMonitoringDashboardData";
import { getRegistryPath, RegistryType } from "$lib/utils";
import { goto } from "$app/navigation";

export const load: PageLoad = async ({ parent, fetch }) => {
  const { registryType, metadata } = await parent();

  // redirect to card layout if registryType is not 'model'
  if (registryType !== RegistryType.Model) {
    throw goto(
      `/opsml/${getRegistryPath(registryType)}/card/${metadata.space}/${
        metadata.name
      }/${metadata.version}`
    );
  }
  return loadMonitoringDashboardData(fetch, await parent(), {
    initialTimeInterval: TimeInterval.SixHours,
    loadLLMRecords: false,
    loadAlerts: true,
  });
};
