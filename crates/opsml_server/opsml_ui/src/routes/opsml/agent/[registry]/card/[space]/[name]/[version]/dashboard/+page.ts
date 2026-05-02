import type { PageLoad } from './$types';
import { createInternalApiClient } from '$lib/api/internalClient';
import { ServerPaths } from '$lib/components/api/routes';
import { calculateTimeRange, getCookie } from '$lib/components/trace/utils';
import type { DateTime } from '$lib/types';
import type { CardMetadata } from '$lib/server/card/layout';
import { buildMockGenAiBundle } from '$lib/components/card/agent/observability/mockData';
import type {
  AgentDashboardRequest,
  AgentDashboardResponse,
  ToolDashboardRequest,
  ToolDashboardResponse,
  GenAiMetricsRequest,
  GenAiModelUsageResponse,
  GenAiOperationBreakdownResponse,
  GenAiErrorBreakdownResponse,
  GenAiAgentActivityResponse,
  AgentGenAiBundle,
} from '$lib/components/card/agent/observability/types';

export const ssr = false;

export const load: PageLoad = async ({ fetch, parent }) => {
  const parentData = await parent();
  const metadata = parentData.metadata as CardMetadata;
  const agentName = metadata.name;
  const useMockFallback = Boolean(parentData.devMockEnabled);

  const selectedRange = getCookie('trace_range') ?? '24hours';
  const { startTime: start_time, endTime: end_time, bucketInterval: bucket_interval } =
    calculateTimeRange(selectedRange);

  if (useMockFallback) {
    return { bundle: buildMockGenAiBundle({ selectedRange, bucketInterval: bucket_interval }), mockMode: true };
  }

  const client = createInternalApiClient(fetch);

  const agentBody: AgentDashboardRequest = {
    service_name: null,
    agent_name: agentName,
    provider_name: null,
    start_time: start_time as DateTime,
    end_time: end_time as DateTime,
    bucket_interval,
    model_pricing: {},
  };
  const toolBody: ToolDashboardRequest = {
    service_name: null,
    start_time: start_time as DateTime,
    end_time: end_time as DateTime,
    bucket_interval,
  };
  const metricsBody: GenAiMetricsRequest = {
    service_name: null,
    start_time: start_time as DateTime,
    end_time: end_time as DateTime,
    bucket_interval,
    operation_name: null,
    provider_name: null,
    model: null,
  };

  try {
    const [agentRes, toolRes, modelsRes, opsRes, errsRes, agentsRes] = await Promise.all([
      client.post(ServerPaths.GENAI_AGENT_METRICS, agentBody),
      client.post(ServerPaths.GENAI_TOOL_METRICS, toolBody),
      client.post(ServerPaths.GENAI_MODELS, metricsBody),
      client.post(ServerPaths.GENAI_OPERATIONS, metricsBody),
      client.post(ServerPaths.GENAI_ERRORS, metricsBody),
      client.post(ServerPaths.GENAI_AGENTS, metricsBody),
    ]);

    const bundle: AgentGenAiBundle = {
      agent_dashboard: (await agentRes.json()) as AgentDashboardResponse,
      tool_dashboard: (await toolRes.json()) as ToolDashboardResponse,
      model_usage: ((await modelsRes.json()) as GenAiModelUsageResponse).models,
      operation_breakdown: ((await opsRes.json()) as GenAiOperationBreakdownResponse).operations,
      errors: ((await errsRes.json()) as GenAiErrorBreakdownResponse).errors,
      agents: ((await agentsRes.json()) as GenAiAgentActivityResponse).agents,
      range: { start_time, end_time, bucket_interval, selected_range: selectedRange },
    };

    return { bundle, mockMode: false };
  } catch (error) {
    console.error('Failed to load GenAI metrics:', error);
    return {
      bundle: buildMockGenAiBundle({ selectedRange, bucketInterval: bucket_interval }),
      mockMode: true,
    };
  }
};
