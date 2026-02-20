export const ssr = false;

import type { PageLoad } from "./$types";
import { DriftType } from "$lib/components/scouter/types";
import {
  getTimeRange,
  loadGenAIData,
  classifyError,
  type GenAIMonitoringPageData,
  type MonitoringErrorKind,
} from "$lib/components/scouter/dashboard/utils";

export const load: PageLoad = async ({ parent, fetch }) => {
  const parentData = await parent();
  const { registryType, metadata, eval_profile } = parentData;

  const timeRange = getTimeRange();

  console.log("GenAI page");

  try {
    const selectedData = await loadGenAIData(fetch, eval_profile, timeRange);

    const monitoringData: Extract<
      GenAIMonitoringPageData,
      { status: "success" }
    > = {
      status: "success",
      profile: eval_profile,
      profileUri: "",
      selectedData,
      uid: metadata.uid,
      registryType,
      selectedTimeRange: timeRange,
    };

    return {
      monitoringData,
      metadata,
      driftType: DriftType.GenAI,
      registryType,
    };
  } catch (err) {
    const message =
      err instanceof Error ? err.message : "Unknown monitoring error";
    console.error(`[Monitoring Load Error]: ${message}`, err);

    const errorKind: MonitoringErrorKind = classifyError(err);

    const errorData: Extract<GenAIMonitoringPageData, { status: "error" }> = {
      status: "error",
      uid: metadata.uid,
      registryType,
      selectedTimeRange: timeRange,
      errorMsg: message,
      errorKind,
    };

    return {
      monitoringData: errorData,
      driftType: DriftType.GenAI,
      metadata,
      registryType,
    };
  }
};
