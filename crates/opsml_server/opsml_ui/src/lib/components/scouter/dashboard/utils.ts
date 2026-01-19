import { getSpcDriftMetrics } from "$lib/components/scouter/spc/utils";
import { getPsiDriftMetrics } from "$lib/components/scouter/psi/utils";
import { getCustomDriftMetrics } from "$lib/components/scouter/custom/utils";
import {
  getServerGenAIEvalRecordPage,
  getGenAIEvalTaskDriftMetrics,
  getGenAIEvalWorkflowDriftMetrics,
  getServerGenAIEvalWorkflowPage,
} from "$lib/components/scouter/genai/utils";
import { DriftType } from "../types";
import type { TimeRange } from "$lib/components/trace/types";
import type { RecordCursor } from "$lib/components/scouter/types";
import {
  getDriftProfileUriMap,
  getMonitoringDriftProfiles,
  getProfileFromResponse,
  getServerDriftAlerts,
  type DriftProfile,
  type DriftProfileResponse,
} from "../utils";
import type {
  GenAIEvalRecordPaginationResponse,
  GenAIEvalWorkflowPaginationResponse,
} from "../genai/types";
import { calculateTimeRange, getCookie } from "$lib/components/trace/utils";
import { getMaxDataPoints, type RegistryType } from "$lib/utils";
import type {
  DriftAlertPaginationRequest,
  DriftAlertPaginationResponse,
} from "../alert/types";

export interface DriftMetricMapping {
  [DriftType.Spc]: Awaited<ReturnType<typeof getSpcDriftMetrics>>;
  [DriftType.Psi]: Awaited<ReturnType<typeof getPsiDriftMetrics>>;
  [DriftType.Custom]: Awaited<ReturnType<typeof getCustomDriftMetrics>>;
  [DriftType.GenAI]: {
    task: Awaited<ReturnType<typeof getGenAIEvalTaskDriftMetrics>>;
    workflow: Awaited<ReturnType<typeof getGenAIEvalWorkflowDriftMetrics>>;
  };
}

/** Helper for retrieving metrics for a given drift type
 * This routes the request to the internal API client
 * which then send the request to opsml and then scouter to retrieve the data
 * **CLIENT SIDE ONLY FUNCTION**
 * @param fetch - the fetch function
 * @param driftType - the type of drift to get metrics for
 * @param profile - the drift profile to get metrics for
 * @param timeRange - the time range to get metrics for
 * @param maxDataPoints - the maximum number of data points to retrieve
 * @returns DriftMetricMapping[T] - the drift metrics for the given drift type
 */
export async function loadMetricsForDriftType<T extends DriftType>(
  fetch: typeof globalThis.fetch,
  space: string,
  uid: string,
  driftType: DriftType,
  timeRange: TimeRange,
  maxDataPoints: number
): Promise<DriftMetricMapping[T]> {
  switch (driftType) {
    case DriftType.Spc: {
      const data = await getSpcDriftMetrics(
        fetch,
        space,
        uid,
        timeRange,
        maxDataPoints
      );
      return data as DriftMetricMapping[T];
    }
    case DriftType.Psi: {
      const data = await getPsiDriftMetrics(
        fetch,
        space,
        uid,
        timeRange,
        maxDataPoints
      );
      return data as DriftMetricMapping[T];
    }
    case DriftType.Custom: {
      const data = await getCustomDriftMetrics(
        fetch,
        space,
        uid,
        timeRange,
        maxDataPoints
      );
      return data as DriftMetricMapping[T];
    }
    case DriftType.GenAI: {
      const [task, workflow] = await Promise.all([
        getGenAIEvalTaskDriftMetrics(
          fetch,
          space,
          uid,
          timeRange,
          maxDataPoints
        ),
        getGenAIEvalWorkflowDriftMetrics(
          fetch,
          space,
          uid,
          timeRange,
          maxDataPoints
        ),
      ]);
      return { task, workflow } as DriftMetricMapping[T];
    }
    default:
      const exhaustiveCheck: never = driftType as never;
      throw new Error(`Unhandled drift type: ${exhaustiveCheck}`);
  }
}

/** Helper for retrieving GenAI records and workflows
 * This routes the request to the internal API client
 * which then send the request to opsml and then scouter to retrieve the data
 * **CLIENT SIDE ONLY FUNCTION**
 * @param fetch - the fetch function
 * @param uid - the service uid
 * @param space - the service space
 * @param timeRange - the time range to get records for
 * @returns records and workflows - the genai eval records and workflows
 */
async function loadGenAIRecords(
  fetch: typeof globalThis.fetch,
  uid: string,
  space: string,
  timeRange: TimeRange
): Promise<{
  records: GenAIEvalRecordPaginationResponse;
  workflows: GenAIEvalWorkflowPaginationResponse;
}> {
  const [records, workflows] = await Promise.all([
    getServerGenAIEvalRecordPage(fetch, {
      service_info: { uid, space },
      start_datetime: timeRange.startTime,
      end_datetime: timeRange.endTime,
    }),
    getServerGenAIEvalWorkflowPage(fetch, {
      service_info: { uid, space },
      start_datetime: timeRange.startTime,
      end_datetime: timeRange.endTime,
    }),
  ]);
  return { records, workflows };
}

/** Helper for retrieving the current time range based on saved cookie or default */
export function getTimeRange(): TimeRange {
  const savedRange = getCookie("monitoring_range") || "15min";
  const { startTime, endTime, bucketInterval } = calculateTimeRange(savedRange);
  const timeRange: TimeRange = {
    label: savedRange,
    value: savedRange,
    startTime,
    endTime,
    bucketInterval,
  };

  return timeRange;
}

/** Get Profiles from metadata
 * This retrieves the drift profiles based on the metadata and registry type
 * @param metadata - the card metadata
 * @param registryType - the registry type
 * @returns DriftProfileResponse - the drift profiles
 */
export async function getProfilesFromMetadata(
  fetch: typeof globalThis.fetch,
  metadata: any,
  registryType: RegistryType
): Promise<DriftProfileResponse> {
  const profileMap = getDriftProfileUriMap(metadata, registryType);
  const profiles = await getMonitoringDriftProfiles(
    fetch,
    metadata.uid,
    profileMap,
    registryType
  );

  return profiles;
}

/** Sort drift types from responses */
export function getSortedDriftTypes(
  profiles: DriftProfileResponse
): DriftType[] {
  const driftTypes = Object.keys(profiles)
    .filter((key): key is DriftType =>
      Object.values(DriftType).includes(key as DriftType)
    )
    .sort();
  return driftTypes;
}

export type SelectedData = {
  driftType: DriftType;
  metrics: DriftMetricMapping[DriftType];
  driftAlerts: DriftAlertPaginationResponse;
  profile: DriftProfile[DriftType];
  profileUri: string;
  genAIData?: {
    records: GenAIEvalRecordPaginationResponse;
    workflows: GenAIEvalWorkflowPaginationResponse;
  };
};

/** Load initial data for the dashboard
 * @param driftTypes - available drift types
 * @param profiles - drift profiles
 * @param timeRange - time range for metrics
 * @returns initial data for the dashboard
 */
export async function loadInitialData<T extends DriftType>(
  fetch: typeof globalThis.fetch,
  driftTypes: T[],
  profiles: DriftProfileResponse,
  timeRange: TimeRange
): Promise<SelectedData> {
  const selectedDriftType = driftTypes[0];

  // profile: DriftProfile[T]
  const selectedProfile = getProfileFromResponse(selectedDriftType, profiles);
  const selectedConfig = selectedProfile.config;
  const maxDataPoints = getMaxDataPoints();
  const profileUri = profiles[selectedDriftType].profile_uri;

  // Parallel fetch to optimize Rust API response times
  const [selectedMetrics, driftAlerts] = await Promise.all([
    loadMetricsForDriftType(
      fetch,
      selectedConfig.space,
      selectedConfig.uid,
      selectedDriftType,
      timeRange,
      maxDataPoints
    ),
    getServerDriftAlerts(fetch, {
      uid: selectedConfig.uid,
      active: true,
      start_datetime: timeRange.startTime,
      end_datetime: timeRange.endTime,
    }),
  ]);

  let genAIData: SelectedData["genAIData"] = undefined;

  if (selectedDriftType === DriftType.GenAI) {
    const genAIResponse = await loadGenAIRecords(
      fetch,
      selectedConfig.uid,
      selectedConfig.space,
      timeRange
    );
    genAIData = {
      records: genAIResponse.records,
      workflows: genAIResponse.workflows,
    };
  }

  return {
    driftType: selectedDriftType,
    metrics: selectedMetrics as DriftMetricMapping[T],
    driftAlerts,
    profile: selectedProfile,
    profileUri,
    genAIData,
  };
}

export type MonitoringPageData =
  | {
      status: "success";
      driftTypes: DriftType[];
      profiles: DriftProfileResponse;
      selectedData: SelectedData;
      uid: string;
      registryType: RegistryType;
      selectedTimeRange: TimeRange;
    }
  | {
      status: "error";
      uid: string;
      registryType: RegistryType;
      selectedTimeRange: TimeRange;
      errorMsg: string;
      driftTypes: never[];
      profiles: Record<string, never>;
    };

/**
 * Orchestrates the data fetching for the monitoring dashboard.
 * Designed for SvelteKit load functions or client-side initialization.
 */
export async function getMonitoringPageData(
  fetch: typeof globalThis.fetch,
  metadata: { uid: string; [key: string]: any },
  registryType: RegistryType,
  driftType: DriftType
): Promise<MonitoringPageData> {
  const timeRange = getTimeRange();

  try {
    const profiles = await getProfilesFromMetadata(
      fetch,
      metadata,
      registryType
    );
    const driftTypes = getSortedDriftTypes(profiles);

    if (driftTypes.length === 0) {
      throw new Error("No drift profiles configured for this asset.");
    }

    const selectedData = await loadInitialData(
      fetch,
      driftTypes,
      profiles,
      timeRange
    );

    return {
      status: "success",
      driftTypes,
      profiles,
      selectedData,
      uid: metadata.uid,
      registryType,
      selectedTimeRange: timeRange,
    };
  } catch (err) {
    const message =
      err instanceof Error ? err.message : "Unknown monitoring error";
    console.error(`[Monitoring Load Error]: ${message}`, err);

    return {
      status: "error",
      uid: metadata.uid,
      registryType,
      selectedTimeRange: timeRange,
      errorMsg: message,
      driftTypes: [],
      profiles: {},
    };
  }
}

/** Change Alert Page
 *
 * @param fetch
 * @param cursor
 * @param monitoringData
 */
export async function changeAlertPage(
  fetch: typeof globalThis.fetch,
  cursor: { cursor: RecordCursor; direction: string },
  monitoringData: Extract<MonitoringPageData, { status: "success" }>
) {
  const request: DriftAlertPaginationRequest = {
    uid: monitoringData.selectedData.profile.config.uid,
    active: true,
    cursor_id: cursor.cursor.id,
    direction: cursor.direction,
    cursor_created_at: cursor.cursor.created_at,
    start_datetime: monitoringData.selectedTimeRange.startTime,
    end_datetime: monitoringData.selectedTimeRange.endTime,
  };

  const alertResp = await getServerDriftAlerts(fetch, request);

  // Update State in Place
  monitoringData.selectedData = {
    ...monitoringData.selectedData,
    driftAlerts: alertResp,
  };
}

// Update type definition to include optional cursors
export interface RefreshOptions {
  recordCursor?: { cursor: RecordCursor; direction: string };
  workflowCursor?: { cursor: RecordCursor; direction: string };
}

/**
 * Refactored Refresh Logic
 * Handles full refreshes (Time/Type changes) and partial refreshes (Pagination)
 */
export async function refreshMonitoringData(
  fetch: typeof globalThis.fetch,
  type: DriftType,
  monitoringData: Extract<MonitoringPageData, { status: "success" }>,
  options: RefreshOptions = {}
): Promise<void> {
  const profile = getProfileFromResponse(type, monitoringData.profiles); // accessing specific profile based on structure
  const config = profile.config; // assuming standardized config structure
  const timeRange = monitoringData.selectedTimeRange;
  const maxPoints = getMaxDataPoints(); // This usually relies on window.innerWidth

  const promises: Promise<any>[] = [];
  const isPaginationOnly = options.recordCursor || options.workflowCursor;

  let metricsPromise;
  let alertPromise;
  if (!isPaginationOnly) {
    metricsPromise = loadMetricsForDriftType(
      fetch,
      config.space,
      config.uid,
      type,
      timeRange,
      maxPoints
    );
    alertPromise = getServerDriftAlerts(fetch, {
      uid: config.uid,
      active: true,
      start_datetime: timeRange.startTime,
      end_datetime: timeRange.endTime,
    });
  } else {
    // Return existing metrics to preserve state
    metricsPromise = Promise.resolve(monitoringData.selectedData.metrics);
    alertPromise = Promise.resolve(monitoringData.selectedData.driftAlerts);
  }
  promises.push(metricsPromise);
  promises.push(alertPromise);

  if (type === DriftType.GenAI) {
    // Records Table
    if (options.recordCursor) {
      promises.push(
        getServerGenAIEvalRecordPage(fetch, {
          service_info: { uid: config.uid, space: config.space },
          cursor_created_at: options.recordCursor.cursor.created_at,
          cursor_id: options.recordCursor.cursor.id,
          direction: options.recordCursor.direction,
          start_datetime: timeRange.startTime,
          end_datetime: timeRange.endTime,
        })
      );
    } else {
      // Default load (Time/Type change)
      promises.push(
        getServerGenAIEvalRecordPage(fetch, {
          service_info: { uid: config.uid, space: config.space },
          start_datetime: timeRange.startTime,
          end_datetime: timeRange.endTime,
        })
      );
    }

    if (options.workflowCursor) {
      promises.push(
        getServerGenAIEvalWorkflowPage(fetch, {
          service_info: { uid: config.uid, space: config.space },
          cursor_created_at: options.workflowCursor.cursor.created_at,
          cursor_id: options.workflowCursor.cursor.id,
          direction: options.workflowCursor.direction,
          start_datetime: timeRange.startTime,
          end_datetime: timeRange.endTime,
        })
      );
    } else {
      // Default load
      promises.push(
        getServerGenAIEvalWorkflowPage(fetch, {
          service_info: { uid: config.uid, space: config.space },
          start_datetime: timeRange.startTime,
          end_datetime: timeRange.endTime,
        })
      );
    }
  } else {
    // Placeholders for non-GenAI types to maintain Promise.all alignment
    promises.push(Promise.resolve(null));
    promises.push(Promise.resolve(null));
  }

  // Execute Parallel Fetch
  const [newMetrics, alertResp, recordsResp, workflowsResp] =
    await Promise.all(promises);

  // Update State in Place
  monitoringData.selectedData = {
    ...monitoringData.selectedData,
    driftType: type,
    metrics: newMetrics,
    driftAlerts: alertResp,
    // Update GenAI data if relevant
    ...(type === DriftType.GenAI
      ? {
          genAIData: {
            records: recordsResp,
            workflows: workflowsResp,
          },
        }
      : {}),
  };
}

export async function performRefresh(
  monitoringData: Extract<MonitoringPageData, { status: "success" }>, // bindable monitoring data
  isRefreshing: boolean, // bindable flag to indicate refresh state
  type: DriftType,
  rCursor?: { cursor: RecordCursor; direction: string },
  wCursor?: { cursor: RecordCursor; direction: string }
) {
  if (monitoringData.status !== "success") return;

  isRefreshing = true;
  try {
    await refreshMonitoringData(fetch, type, monitoringData, {
      recordCursor: rCursor,
      workflowCursor: wCursor,
    });
  } catch (e) {
    console.error("Dashboard Refresh Failed", e);
  } finally {
    isRefreshing = false;
  }
}
