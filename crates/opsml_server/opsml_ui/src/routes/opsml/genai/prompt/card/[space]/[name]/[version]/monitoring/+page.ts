// This needs to be client-side because we need to calculate max data points from window size
export const ssr = false;

import type { PageLoad } from "./$types";
import { TimeInterval } from "$lib/components/card/monitoring/types";
import { loadMonitoringDashboardData } from "$lib/components/card/monitoring/getMonitoringDashboardData";

export const load: PageLoad = async ({ parent, fetch }) => {
  return loadMonitoringDashboardData(fetch, await parent(), {
    initialTimeInterval: TimeInterval.SixHours,
    loadLLMRecords: true,
    loadAlerts: true,
  });
};
