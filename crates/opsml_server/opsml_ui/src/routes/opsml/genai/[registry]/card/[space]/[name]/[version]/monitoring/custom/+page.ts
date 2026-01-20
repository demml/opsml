export const ssr = false;

import type { PageLoad } from "./$types";
import { DriftType, driftTypeFromString } from "$lib/components/scouter/types";
import { error } from "@sveltejs/kit";
import {
  loadInitialData,
  getTimeRange,
  type MonitoringPageData,
} from "$lib/components/scouter/dashboard/utils";

export const load: PageLoad = async ({ parent, fetch }) => {
  const parentData = await parent();
  const { registryType, metadata, profiles, driftTypes } = parentData;

  const timeRange = getTimeRange();

  try {
    const selectedData = await loadInitialData(
      fetch,
      [DriftType.Custom],
      profiles,
      timeRange
    );

    const monitoringData: Extract<MonitoringPageData, { status: "success" }> = {
      status: "success",
      driftTypes,
      profiles,
      selectedData,
      uid: metadata.uid,
      registryType,
      selectedTimeRange: timeRange,
    };

    return {
      monitoringData,
      metadata,
      driftType: DriftType.Custom,
      registryType,
    };
  } catch (err) {
    const message =
      err instanceof Error ? err.message : "Unknown monitoring error";
    console.error(`[Monitoring Load Error]: ${message}`, err);

    const errorData: Extract<MonitoringPageData, { status: "error" }> = {
      status: "error",
      uid: metadata.uid,
      registryType,
      selectedTimeRange: timeRange,
      errorMsg: message,
      driftTypes: [],
      profiles: {},
    };

    return {
      monitoringData: errorData,
      driftType: DriftType.Custom,
      metadata,
      registryType,
    };
  }
};
