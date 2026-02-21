export const ssr = false;

import type { PageLoad } from "./$types";
import { DriftType, driftTypeFromString } from "$lib/components/scouter/types";
import { error } from "@sveltejs/kit";
import {
  loadInitialData,
  getTimeRange,
  type MonitoringPageData,
  classifyError,
} from "$lib/components/scouter/dashboard/utils";
import type { DriftProfileResponse } from "$lib/components/scouter/utils";

export const load: PageLoad = async ({ parent, fetch }) => {
  const parentData = await parent();
  const { registryType, metadata, profiles, driftTypes, settings } = parentData;

  const timeRange = getTimeRange();

  if (!settings?.scouter_enabled) {
    return {
      monitoringData: {
        status: "error" as const,
        uid: metadata.uid,
        registryType,
        selectedTimeRange: timeRange,
        errorMsg: "Scouter is not enabled.",
        driftTypes: [] as never[],
        profiles: {} as Record<string, never>,
        errorKind: "not_found" as const,
      },
      metadata,
      driftType: DriftType.Custom,
      registryType,
    };
  }

  try {
    const selectedData = await loadInitialData(
      fetch,
      [DriftType.Custom],
      profiles as DriftProfileResponse,
      timeRange,
    );

    const monitoringData: Extract<MonitoringPageData, { status: "success" }> = {
      status: "success",
      driftTypes,
      profiles: profiles as DriftProfileResponse,
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
      errorKind: classifyError(err),
    };

    return {
      monitoringData: errorData,
      driftType: DriftType.Custom,
      metadata,
      registryType,
    };
  }
};
