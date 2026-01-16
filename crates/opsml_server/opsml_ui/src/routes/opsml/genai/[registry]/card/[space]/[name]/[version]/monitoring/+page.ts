export const ssr = false;

import type { PageLoad } from "./$types";
import {
  getMonitoringDriftProfiles,
  getProfileConfig,
} from "$lib/components/scouter/utils";
import { getRegistryPath, RegistryType, getMaxDataPoints } from "$lib/utils";
import { redirect } from "@sveltejs/kit";
import { getCookie, calculateTimeRange } from "$lib/components/trace/utils";
import type { TimeRange } from "$lib/components/trace/types";
import { DriftType } from "$lib/components/scouter/types";
import {
  getDriftProfileUriMap,
  loadAllMetrics,
  getServerDriftAlerts,
} from "$lib/components/scouter/utils";
import {
  getServerGenAIEvalRecordPage,
  getServerGenAIEvalWorkflowPage,
} from "$lib/components/scouter/genai/utils";

export const load: PageLoad = async ({ parent, fetch }) => {
  const parentData = await parent();
  const { registryType, metadata } = parentData;

  if (
    registryType !== RegistryType.Model &&
    registryType !== RegistryType.Prompt
  ) {
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
      label: savedRange,
      value: savedRange,
      startTime,
      endTime,
      bucketInterval,
    };

    console.log("MeGetting profile map");

    const profileMap = getDriftProfileUriMap(metadata, registryType);
    const profiles = await getMonitoringDriftProfiles(
      fetch,
      metadata.uid,
      profileMap,
      registryType
    );

    const driftTypes = Object.keys(profiles)
      .filter((key): key is DriftType =>
        Object.values(DriftType).includes(key as DriftType)
      )
      .sort();

    if (driftTypes.length === 0) {
      throw new Error("No valid drift types found in profiles");
    }

    console.log("Getting config");
    const initialDriftType = driftTypes[0];
    const initialProfile = profiles[initialDriftType];
    const initialConfig = getProfileConfig(
      initialDriftType,
      initialProfile.profile
    );

    const maxDataPoints = getMaxDataPoints();

    console.log("Getting Metrics");
    const [initialMetrics, driftAlerts] = await Promise.all([
      loadAllMetrics(fetch, profiles, timeRange, maxDataPoints),
      getServerDriftAlerts(fetch, {
        uid: initialConfig.uid,
        active: true,
        start_datetime: timeRange.startTime,
        end_datetime: timeRange.endTime,
      }),
    ]);

    let genAIEvalRecords = null;
    let genAIEvalWorkflows = null;

    if (initialDriftType === DriftType.GenAI) {
      [genAIEvalRecords, genAIEvalWorkflows] = await Promise.all([
        getServerGenAIEvalRecordPage(fetch, {
          service_info: {
            uid: initialConfig.uid,
            space: initialConfig.space,
          },
          start_datetime: timeRange.startTime,
          end_datetime: timeRange.endTime,
        }),
        getServerGenAIEvalWorkflowPage(fetch, {
          service_info: {
            uid: initialConfig.uid,
            space: initialConfig.space,
          },
          start_datetime: timeRange.startTime,
          end_datetime: timeRange.endTime,
        }),
      ]);
    }

    console.log("InitialDriftType:", initialDriftType);

    return {
      profiles,
      driftTypes,
      initialDriftType,
      uid: metadata.uid,
      registryType,
      initialTimeRange: timeRange,
      initialMetrics,
      driftAlerts,
      genAIEvalRecords,
      genAIEvalWorkflows,
      status: "success" as const,
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
