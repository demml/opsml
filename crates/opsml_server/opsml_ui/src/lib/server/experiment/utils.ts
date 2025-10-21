import { createOpsmlClient } from "../api/opsmlClient";
import { RoutePaths } from "$lib/components/api/routes";
import type {
  Metric,
  Parameter,
} from "$lib/components/card/card_interfaces/experimentcard";
import { type CardQueryArgs } from "$lib/components/api/schema";
import type { Card } from "$lib/components/home/types";
import { RegistryType, getRegistryTableName } from "$lib/utils";
import type {
  GetMetricNamesRequest,
  GetMetricRequest,
  GetParameterRequest,
  GroupedMetrics,
  Experiment,
  UiMetricRequest,
  GetHardwareMetricRequest,
  HardwareMetrics,
  UiHardwareMetrics,
} from "$lib/components/card/experiment/types";
import { CommonPaths } from "$lib/components/card/experiment/types";
import type { RawFile, RawFileRequest } from "$lib/components/files/types";
import { extractAllHardwareMetrics } from "$lib/components/card/experiment/util";

// Get the metric names for a given experiment
export async function getCardMetricNames(
  fetch: typeof globalThis.fetch,
  uid: string
): Promise<string[]> {
  const request: GetMetricNamesRequest = {
    experiment_uid: uid,
  };

  const response = await createOpsmlClient(fetch).get(
    RoutePaths.EXPERIMENT_METRIC_NAMES,
    request
  );
  return (await response.json()) as string[];
}

export async function getCardParameters(
  fetch: typeof globalThis.fetch,
  uid: string
): Promise<Parameter[]> {
  const request: GetParameterRequest = {
    experiment_uid: uid,
    names: [],
  };

  const response = await createOpsmlClient(fetch).post(
    RoutePaths.EXPERIMENT_PARAMETERS,
    request
  );
  return (await response.json()) as Parameter[];
}

// Get the metrics for a given experiment
export async function getCardMetrics(
  fetch: typeof globalThis.fetch,
  uid: string,
  names: string[]
): Promise<Metric[]> {
  const request: GetMetricRequest = {
    experiment_uid: uid,
    names: names,
  };

  const response = await createOpsmlClient(fetch).post(
    RoutePaths.EXPERIMENT_METRICS,
    request
  );
  return (await response.json()) as Metric[];
}

export async function getRecentExperiments(
  fetch: typeof globalThis.fetch,
  space: string,
  name: string,
  currentVersion: string
): Promise<Experiment[]> {
  const params: CardQueryArgs = {
    registry_type: RegistryType.Experiment,
    name,
    space,
    limit: 50,
  };

  const response = await createOpsmlClient(fetch).get(
    RoutePaths.LIST_CARDS,
    params
  );
  const cards = (await response.json()) as Card[];

  return cards
    .filter((card) => {
      const version = card.data.version?.trim().toLowerCase();
      const current = currentVersion.trim().toLowerCase();
      return version && version !== current;
    })
    .map((card) => ({
      uid: card.data.uid,
      version: card.data.version,
    }));
}

export async function getGroupedMetrics(
  fetch: typeof globalThis.fetch,
  experiments: Experiment[],
  selectedMetrics: string[]
): Promise<GroupedMetrics> {
  let uiMetricRequest: UiMetricRequest = {
    experiments: experiments,
    metric_names: selectedMetrics,
  };

  // Process current card metrics
  const response = await createOpsmlClient(fetch).post(
    RoutePaths.EXPERIMENT_GROUPED_METRICS,
    uiMetricRequest
  );

  return (await response.json()) as GroupedMetrics;
}

export async function getHardwareMetrics(
  fetch: typeof globalThis.fetch,
  uid: string
): Promise<UiHardwareMetrics> {
  const request: GetHardwareMetricRequest = {
    experiment_uid: uid,
  };

  const response = await createOpsmlClient(fetch).get(
    RoutePaths.HARDWARE_METRICS,
    request
  );
  let metrics = (await response.json()) as HardwareMetrics[];

  return extractAllHardwareMetrics(metrics);
}

export async function getExperimentFigures(
  fetch: typeof globalThis.fetch,
  uid: string,
  space: string,
  name: string,
  version: string
): Promise<RawFile[]> {
  const tableName = getRegistryTableName(RegistryType.Experiment);
  const path = `${tableName}/${space}/${name}/v${version}/${CommonPaths.Artifacts}/${CommonPaths.Figures}`;

  const request: RawFileRequest = {
    uid,
    path,
    registry_type: RegistryType.Experiment,
  };

  const response = await createOpsmlClient(fetch).post(
    RoutePaths.FILE_CONTENT_BATCH,
    request
  );

  return (await response.json()) as RawFile[];
}
