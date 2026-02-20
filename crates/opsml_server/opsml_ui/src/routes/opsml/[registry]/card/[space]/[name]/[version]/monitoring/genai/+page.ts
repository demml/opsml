export const ssr = false;

import type { PageLoad } from "./$types";
import { DriftType } from "$lib/components/scouter/types";
import {
  getTimeRange,
  loadGenAIData,
  type GenAIMonitoringPageData,
} from "$lib/components/scouter/dashboard/utils";
import type { GenAIEvalProfile } from "$lib/components/scouter/genai/types";

export const load: PageLoad = async ({ parent, fetch }) => {
  const parentData = await parent();
  const { registryType, metadata, profiles } = parentData;

  const timeRange = getTimeRange();

  try {
    const genAIProfileEntry = profiles[DriftType.GenAI];
    const eval_profile = genAIProfileEntry.profile.GenAI as GenAIEvalProfile;
    const profileUri = genAIProfileEntry.profile_uri ?? "";

    const selectedData = await loadGenAIData(fetch, eval_profile, timeRange);

    const monitoringData: Extract<
      GenAIMonitoringPageData,
      { status: "success" }
    > = {
      status: "success",
      profile: eval_profile,
      profileUri,
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

    const errorData: Extract<GenAIMonitoringPageData, { status: "error" }> = {
      status: "error",
      uid: metadata.uid,
      registryType,
      selectedTimeRange: timeRange,
      errorMsg: message,
    };

    return {
      monitoringData: errorData,
      driftType: DriftType.GenAI,
      metadata,
      registryType,
    };
  }
};
