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
  GenAIEvalProfile,
  GenAIEvalRecordPaginationResponse,
  GenAIEvalWorkflowPaginationResponse,
} from "../genai/types";
import { calculateTimeRange, getCookie } from "$lib/components/trace/utils";
import { getMaxDataPoints, type RegistryType } from "$lib/utils";
import type {
  DriftAlertPaginationRequest,
  DriftAlertPaginationResponse,
} from "../alert/types";

// ─── Error Classification ────────────────────────────────────────────────────

export type MonitoringErrorKind =
  | "not_found"
  | "server_error"
  | "unknown"
  | "not_enabled";

export function classifyError(err: unknown): MonitoringErrorKind {
  const msg = err instanceof Error ? err.message : String(err);
  if (/\bHTTP 404\b/.test(msg)) return "not_found";
  if (/\bHTTP 5\d{2}\b/.test(msg)) return "server_error";
  return "unknown";
}

// ─── Metric Type Map ──────────────────────────────────────────────────────────

export interface DriftMetricMapping {
  [DriftType.Spc]: Awaited<ReturnType<typeof getSpcDriftMetrics>>;
  [DriftType.Psi]: Awaited<ReturnType<typeof getPsiDriftMetrics>>;
  [DriftType.Custom]: Awaited<ReturnType<typeof getCustomDriftMetrics>>;
  [DriftType.GenAI]: {
    task: Awaited<ReturnType<typeof getGenAIEvalTaskDriftMetrics>>;
    workflow: Awaited<ReturnType<typeof getGenAIEvalWorkflowDriftMetrics>>;
  };
}

// ─── Selected Data Types ──────────────────────────────────────────────────────

/** Selected data for SPC, PSI, and Custom drift dashboards */
export type SelectedData = {
  driftType: DriftType;
  metrics: DriftMetricMapping[DriftType];
  driftAlerts: DriftAlertPaginationResponse;
  profile: DriftProfile[DriftType];
  profileUri: string;
};

/** Selected data for the GenAI evaluation dashboard */
export type SelectedGenAIData = {
  metrics: DriftMetricMapping[DriftType.GenAI];
  driftAlerts: DriftAlertPaginationResponse;
  records: GenAIEvalRecordPaginationResponse;
  workflows: GenAIEvalWorkflowPaginationResponse;
};

// ─── Page Data Types ──────────────────────────────────────────────────────────

export type GenAIMonitoringPageData =
  | {
      status: "success";
      profile: GenAIEvalProfile;
      profileUri: string;
      selectedData: SelectedGenAIData;
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
      errorKind: MonitoringErrorKind;
    };

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
      errorKind: MonitoringErrorKind;
    };

// ─── Time Range ───────────────────────────────────────────────────────────────

export function getTimeRange(): TimeRange {
  const savedRange = getCookie("monitoring_range") || "15min";
  const { startTime, endTime, bucketInterval } = calculateTimeRange(savedRange);
  return {
    label: savedRange,
    value: savedRange,
    startTime,
    endTime,
    bucketInterval,
  };
}

// ─── Profile Helpers ──────────────────────────────────────────────────────────

export async function getProfilesFromMetadata(
  fetch: typeof globalThis.fetch,
  metadata: any,
  registryType: RegistryType,
): Promise<DriftProfileResponse> {
  const profileMap = getDriftProfileUriMap(metadata);
  return getMonitoringDriftProfiles(
    fetch,
    metadata.uid,
    profileMap,
    registryType,
  );
}

export function getSortedDriftTypes(
  profiles: DriftProfileResponse,
): DriftType[] {
  return Object.keys(profiles)
    .filter((key): key is DriftType =>
      Object.values(DriftType).includes(key as DriftType),
    )
    .sort();
}

// ─── Metric Loaders ───────────────────────────────────────────────────────────

/** Loads binned metrics for any drift type. For GenAI, fetches task and workflow metrics in parallel. */
export async function loadMetricsForDriftType<T extends DriftType>(
  fetch: typeof globalThis.fetch,
  space: string,
  uid: string,
  driftType: T,
  timeRange: TimeRange,
  maxDataPoints: number,
): Promise<DriftMetricMapping[T]> {
  switch (driftType) {
    case DriftType.Spc:
      return getSpcDriftMetrics(
        fetch,
        space,
        uid,
        timeRange,
        maxDataPoints,
      ) as Promise<DriftMetricMapping[T]>;
    case DriftType.Psi:
      return getPsiDriftMetrics(
        fetch,
        space,
        uid,
        timeRange,
        maxDataPoints,
      ) as Promise<DriftMetricMapping[T]>;
    case DriftType.Custom:
      return getCustomDriftMetrics(
        fetch,
        space,
        uid,
        timeRange,
        maxDataPoints,
      ) as Promise<DriftMetricMapping[T]>;
    case DriftType.GenAI: {
      const [task, workflow] = await Promise.all([
        getGenAIEvalTaskDriftMetrics(
          fetch,
          space,
          uid,
          timeRange,
          maxDataPoints,
        ),
        getGenAIEvalWorkflowDriftMetrics(
          fetch,
          space,
          uid,
          timeRange,
          maxDataPoints,
        ),
      ]);
      return { task, workflow } as DriftMetricMapping[T];
    }
    default: {
      const _exhaustive: never = driftType as never;
      throw new Error(`Unhandled drift type: ${_exhaustive}`);
    }
  }
}

// ─── GenAI Data Loaders ───────────────────────────────────────────────────────

async function loadGenAIRecordsAndWorkflows(
  fetch: typeof globalThis.fetch,
  uid: string,
  space: string,
  timeRange: TimeRange,
  recordCursor?: { cursor: RecordCursor; direction: string },
  workflowCursor?: { cursor: RecordCursor; direction: string },
): Promise<{
  records: GenAIEvalRecordPaginationResponse;
  workflows: GenAIEvalWorkflowPaginationResponse;
}> {
  const [records, workflows] = await Promise.all([
    getServerGenAIEvalRecordPage(fetch, {
      service_info: { uid, space },
      ...(recordCursor
        ? {
            cursor_id: recordCursor.cursor.id,
            cursor_created_at: recordCursor.cursor.created_at,
            direction: recordCursor.direction,
          }
        : {}),
      start_datetime: timeRange.startTime,
      end_datetime: timeRange.endTime,
    }),
    getServerGenAIEvalWorkflowPage(fetch, {
      service_info: { uid, space },
      ...(workflowCursor
        ? {
            cursor_id: workflowCursor.cursor.id,
            cursor_created_at: workflowCursor.cursor.created_at,
            direction: workflowCursor.direction,
          }
        : {}),
      start_datetime: timeRange.startTime,
      end_datetime: timeRange.endTime,
    }),
  ]);
  return { records, workflows };
}

/** Loads all data for the GenAI evaluation dashboard (metrics, alerts, records, workflows) */
export async function loadGenAIData(
  fetch: typeof globalThis.fetch,
  eval_profile: GenAIEvalProfile,
  timeRange: TimeRange,
): Promise<SelectedGenAIData> {
  const { uid, space } = eval_profile.config;
  const maxDataPoints = getMaxDataPoints();

  const [metrics, driftAlerts, { records, workflows }] = await Promise.all([
    loadMetricsForDriftType(
      fetch,
      space,
      uid,
      DriftType.GenAI,
      timeRange,
      maxDataPoints,
    ),
    getServerDriftAlerts(fetch, {
      uid,
      active: true,
      start_datetime: timeRange.startTime,
      end_datetime: timeRange.endTime,
    }),
    loadGenAIRecordsAndWorkflows(fetch, uid, space, timeRange),
  ]);

  return { metrics, driftAlerts, records, workflows };
}

// ─── Standard (SPC / PSI / Custom) Load ──────────────────────────────────────

/** Loads all data for SPC, PSI, or Custom drift dashboards */
export async function loadInitialData(
  fetch: typeof globalThis.fetch,
  driftTypes: DriftType[],
  profiles: DriftProfileResponse,
  timeRange: TimeRange,
): Promise<SelectedData> {
  const driftType = driftTypes[0];
  const profile = getProfileFromResponse(driftType, profiles);
  const { uid, space } = profile.config;
  const maxDataPoints = getMaxDataPoints();
  const profileUri = profiles[driftType].profile_uri;

  const [metrics, driftAlerts] = await Promise.all([
    loadMetricsForDriftType(
      fetch,
      space,
      uid,
      driftType,
      timeRange,
      maxDataPoints,
    ),
    getServerDriftAlerts(fetch, {
      uid,
      active: true,
      start_datetime: timeRange.startTime,
      end_datetime: timeRange.endTime,
    }),
  ]);

  return { driftType, metrics, driftAlerts, profile, profileUri };
}

// ─── Page Data Orchestrators ──────────────────────────────────────────────────

/** Builds the full GenAI monitoring page data from a single eval profile */
export async function getGenAIMonitoringPageData(
  fetch: typeof globalThis.fetch,
  metadata: { uid: string; [key: string]: any },
  eval_profile: GenAIEvalProfile,
  registryType: RegistryType,
  profileUri: string = "",
): Promise<GenAIMonitoringPageData> {
  const timeRange = getTimeRange();

  try {
    const selectedData = await loadGenAIData(fetch, eval_profile, timeRange);

    return {
      status: "success",
      profile: eval_profile,
      profileUri,
      selectedData,
      uid: metadata.uid,
      registryType,
      selectedTimeRange: timeRange,
    };
  } catch (err) {
    const message =
      err instanceof Error ? err.message : "Unknown monitoring error";
    console.error(`[GenAI Monitoring Load Error]: ${message}`, err);

    return {
      status: "error",
      uid: metadata.uid,
      registryType,
      selectedTimeRange: timeRange,
      errorMsg: message,
      errorKind: classifyError(err),
    };
  }
}

/** Builds the full standard monitoring page data from a profiles map */
export async function getMonitoringPageData(
  fetch: typeof globalThis.fetch,
  metadata: { uid: string; [key: string]: any },
  registryType: RegistryType,
): Promise<MonitoringPageData> {
  const timeRange = getTimeRange();

  try {
    const profiles = await getProfilesFromMetadata(
      fetch,
      metadata,
      registryType,
    );
    const driftTypes = getSortedDriftTypes(profiles);

    if (driftTypes.length === 0) {
      throw new Error("No drift profiles configured for this asset.");
    }

    const selectedData = await loadInitialData(
      fetch,
      driftTypes,
      profiles,
      timeRange,
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
      errorKind: classifyError(err),
    };
  }
}

// ─── Refresh Functions ────────────────────────────────────────────────────────

export interface GenAIRefreshOptions {
  recordCursor?: { cursor: RecordCursor; direction: string };
  workflowCursor?: { cursor: RecordCursor; direction: string };
}

/** Refreshes GenAI dashboard data. Supports full refresh (time change) and paginated refresh (cursor navigation). */
export async function refreshGenAIMonitoringData(
  fetch: typeof globalThis.fetch,
  monitoringData: Extract<GenAIMonitoringPageData, { status: "success" }>,
  options: GenAIRefreshOptions = {},
): Promise<void> {
  const { uid, space } = monitoringData.profile.config;
  const timeRange = monitoringData.selectedTimeRange;
  const maxPoints = getMaxDataPoints();
  const isPaginationOnly = options.recordCursor || options.workflowCursor;

  const metricsPromise = isPaginationOnly
    ? Promise.resolve(monitoringData.selectedData.metrics)
    : loadMetricsForDriftType(
        fetch,
        space,
        uid,
        DriftType.GenAI,
        timeRange,
        maxPoints,
      );

  const alertsPromise = isPaginationOnly
    ? Promise.resolve(monitoringData.selectedData.driftAlerts)
    : getServerDriftAlerts(fetch, {
        uid,
        active: true,
        start_datetime: timeRange.startTime,
        end_datetime: timeRange.endTime,
      });

  const [metrics, driftAlerts, { records, workflows }] = await Promise.all([
    metricsPromise,
    alertsPromise,
    loadGenAIRecordsAndWorkflows(
      fetch,
      uid,
      space,
      timeRange,
      options.recordCursor,
      options.workflowCursor,
    ),
  ]);

  monitoringData.selectedData = { metrics, driftAlerts, records, workflows };
}

/** Refreshes standard (SPC/PSI/Custom) monitoring dashboard data. */
export async function refreshMonitoringData(
  fetch: typeof globalThis.fetch,
  type: DriftType,
  monitoringData: Extract<MonitoringPageData, { status: "success" }>,
): Promise<void> {
  const profile = getProfileFromResponse(type, monitoringData.profiles);
  const { uid, space } = profile.config;
  const timeRange = monitoringData.selectedTimeRange;
  const maxPoints = getMaxDataPoints();

  const [metrics, driftAlerts] = await Promise.all([
    loadMetricsForDriftType(fetch, space, uid, type, timeRange, maxPoints),
    getServerDriftAlerts(fetch, {
      uid,
      active: true,
      start_datetime: timeRange.startTime,
      end_datetime: timeRange.endTime,
    }),
  ]);

  monitoringData.selectedData = {
    ...monitoringData.selectedData,
    driftType: type,
    metrics,
    driftAlerts,
  };
}

// ─── Alert Helpers ────────────────────────────────────────────────────────────

export async function changeAlertPage(
  fetch: typeof globalThis.fetch,
  cursor: { cursor: RecordCursor; direction: string },
  monitoringData: Extract<MonitoringPageData, { status: "success" }>,
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

  monitoringData.selectedData = {
    ...monitoringData.selectedData,
    driftAlerts: alertResp,
  };
}
