import type { PageLoad } from './$types';
import { createInternalApiClient } from '$lib/api/internalClient';
import { ServerPaths } from '$lib/components/api/routes';
import { calculateTimeRange, getCookie } from '$lib/components/trace/utils';
import type { DateTime } from '$lib/types';
import type { CardMetadata } from '$lib/server/card/layout';
import { RegistryType } from '$lib/utils';
import { buildMockGenAiBundle } from '$lib/components/card/agent/observability/mockData';
import type {
  AgentGenAiBundle,
  EvalProfileOption,
  GenAiDashboardRequest,
  GenAiDashboardResponse,
} from '$lib/components/card/agent/observability/types';
import type { PromptCard } from '$lib/components/card/card_interfaces/promptcard';
import { toEvalProfileOptions } from '$lib/components/card/agent/observability/utils';

export const ssr = false;

/**
 * Loads the composite GenAI dashboard for the current card.
 *
 * - Agent registry: scopes by `service_name = "{space}:{name}"` (matches the
 *   Rust `ServiceInfo::namespace()`, which is what the tracer stamps onto every
 *   span via `service.name`).
 * - Prompt registry: scopes by `entity_id = eval_profile.config.uid`.
 *
 * The two scopes are mutually exclusive in practice — only one is non-null per
 * request. The composite endpoint applies AND if both are set.
 */
export const load: PageLoad = async ({ fetch, parent }) => {
  const parentData = await parent();
  const metadata = parentData.metadata as CardMetadata;
  const registryType = parentData.registryType as RegistryType;
  const useMockFallback = Boolean(parentData.devMockEnabled);

  const isPrompt = registryType === RegistryType.Prompt;
  const promptUid = isPrompt
    ? (metadata as PromptCard).eval_profile?.config.uid ?? null
    : null;
  const serviceName = isPrompt ? null : `${metadata.space}:${metadata.name}`;

  // FilterBar Profile dropdown sourcing.
  // - Agent registry: every associated prompt card with an eval profile
  //   becomes a selectable scope (parent layout already filters to those).
  // - Prompt registry: the only valid scope is this prompt's own profile,
  //   which the FilterBar will render as a disabled (locked) select.
  const promptCardsWithEval =
    (parentData.promptCardsWithEval as PromptCard[] | undefined) ?? [];
  const evalProfiles: EvalProfileOption[] = isPrompt
    ? promptUid
      ? [
          {
            uid: promptUid,
            alias: (metadata as PromptCard).eval_profile?.alias ?? null,
            name: (metadata as PromptCard).name,
          },
        ]
      : []
    : toEvalProfileOptions(promptCardsWithEval);

  const selectedRange = getCookie('monitoring_range') ?? '24hours';
  const {
    startTime: start_time,
    endTime: end_time,
    bucketInterval: bucket_interval,
  } = calculateTimeRange(selectedRange);

  if (useMockFallback) {
    return {
      bundle: buildMockGenAiBundle({
        selectedRange,
        bucketInterval: bucket_interval,
        serviceName,
        entityId: promptUid,
        evalProfiles: isPrompt ? evalProfiles : evalProfiles.length > 0 ? evalProfiles : undefined,
      }),
      mockMode: true,
    };
  }

  const body: GenAiDashboardRequest = {
    service_name: serviceName,
    entity_id: promptUid,
    start_time: start_time as DateTime,
    end_time: end_time as DateTime,
    bucket_interval,
    agent_name: null,
    provider_name: null,
    operation_name: null,
    model: null,
    model_pricing: {},
  };

  const client = createInternalApiClient(fetch);

  try {
    const response = await client.post(ServerPaths.GENAI_DASHBOARD, body);
    const dashboard = (await response.json()) as GenAiDashboardResponse;
    const bundle: AgentGenAiBundle = {
      dashboard,
      range: { start_time, end_time, bucket_interval, selected_range: selectedRange },
      eval_profiles: evalProfiles,
    };
    return { bundle, mockMode: false };
  } catch (error) {
    console.error('Failed to load GenAI dashboard:', error);
    return {
      bundle: buildMockGenAiBundle({
        selectedRange,
        bucketInterval: bucket_interval,
        serviceName,
        entityId: promptUid,
        evalProfiles: isPrompt ? evalProfiles : evalProfiles.length > 0 ? evalProfiles : undefined,
      }),
      mockMode: true,
    };
  }
};
