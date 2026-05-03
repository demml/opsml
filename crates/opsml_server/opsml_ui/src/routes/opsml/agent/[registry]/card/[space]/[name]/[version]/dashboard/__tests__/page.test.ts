import { describe, it, expect, vi } from 'vitest';
import { load } from '../+page';
import { toEvalProfileOptions } from '$lib/components/card/agent/observability/utils';
import { RegistryType } from '$lib/utils';
import type { PromptCard } from '$lib/components/card/card_interfaces/promptcard';

function makeCard(overrides: Partial<PromptCard> = {}): PromptCard {
  return {
    name: 'my-prompt',
    space: 'test',
    version: '1.0.0',
    uid: 'uid-1',
    tags: [],
    metadata: {},
    registry_type: RegistryType.Prompt,
    app_env: 'dev',
    created_at: '2026-01-01T00:00:00Z',
    is_card: true,
    opsml_version: '0.1.0',
    prompt: {} as never,
    ...overrides,
  };
}

// ── load() smoke tests ────────────────────────────────────────────────────────
// These call the real load() function to verify the route doesn't throw (i.e.
// no 500) and returns a correctly-shaped bundle. Mock mode is used so no real
// network calls are made.

const AGENT_METADATA = {
  space: 'fraud-detection',
  name: 'triage-agent',
  version: '1.0.0',
  uid: 'agent-uid-1',
  tags: [],
  metadata: {},
  registry_type: RegistryType.Agent,
  app_env: 'dev',
  created_at: '2026-01-01T00:00:00Z',
  is_card: true,
  opsml_version: '0.1.0',
};

const PROMPT_METADATA: PromptCard = {
  name: 'my-prompt',
  space: 'acme',
  version: '1.0.0',
  uid: 'prompt-uid-1',
  tags: [],
  metadata: {},
  registry_type: RegistryType.Prompt,
  app_env: 'dev',
  created_at: '2026-01-01T00:00:00Z',
  is_card: true,
  opsml_version: '0.1.0',
  prompt: {} as never,
  eval_profile: { alias: 'v1', config: { uid: 'eval-uid-abc' } } as never,
};

function makeLoadCtx(
  parentData: Record<string, unknown>,
  fetchImpl?: typeof fetch,
) {
  return {
    fetch: fetchImpl ?? vi.fn(),
    parent: vi.fn().mockResolvedValue(parentData),
    params: {},
    url: new URL('http://localhost'),
    route: { id: '' },
    depends: vi.fn(),
    untrack: (fn: () => unknown) => fn(),
  } as unknown as Parameters<typeof load>[0];
}

describe('dashboard +page.ts load() — agent mock mode', () => {
  it('returns bundle without throwing (no fetch call)', async () => {
    const ctx = makeLoadCtx({
      metadata: AGENT_METADATA,
      registryType: RegistryType.Agent,
      devMockEnabled: true,
      promptCardsWithEval: [],
    });
    const result = await load(ctx);
    expect(result.bundle).toBeDefined();
    expect(result.mockMode).toBe(true);
  });

  it('bundle has required dashboard shape', async () => {
    const ctx = makeLoadCtx({
      metadata: AGENT_METADATA,
      registryType: RegistryType.Agent,
      devMockEnabled: true,
      promptCardsWithEval: [],
    });
    const { bundle } = await load(ctx);
    expect(bundle.dashboard).toHaveProperty('applied_filters');
    expect(bundle.dashboard).toHaveProperty('available_filters');
    expect(bundle.dashboard).toHaveProperty('agent_dashboard');
    expect(bundle.range).toHaveProperty('selected_range');
  });

  it('service_name uses colon-joined space:name format', async () => {
    const ctx = makeLoadCtx({
      metadata: AGENT_METADATA,
      registryType: RegistryType.Agent,
      devMockEnabled: true,
      promptCardsWithEval: [],
    });
    const { bundle } = await load(ctx);
    expect(bundle.dashboard.applied_filters.service_name).toBe('fraud-detection:triage-agent');
    expect(bundle.dashboard.applied_filters.entity_id).toBeNull();
  });

  it('eval_profiles populated from promptCardsWithEval', async () => {
    const promptCard = makeCard({
      name: 'linked-prompt',
      eval_profile: { alias: 'my-alias', config: { uid: 'ep-uid-1' } } as never,
    });
    const ctx = makeLoadCtx({
      metadata: AGENT_METADATA,
      registryType: RegistryType.Agent,
      devMockEnabled: true,
      promptCardsWithEval: [promptCard],
    });
    const { bundle } = await load(ctx);
    expect(bundle.eval_profiles).toHaveLength(1);
    expect(bundle.eval_profiles[0].uid).toBe('ep-uid-1');
    expect(bundle.eval_profiles[0].alias).toBe('my-alias');
  });

  it('fetch is never called in mock mode', async () => {
    const mockFetch = vi.fn();
    const ctx = makeLoadCtx(
      {
        metadata: AGENT_METADATA,
        registryType: RegistryType.Agent,
        devMockEnabled: true,
        promptCardsWithEval: [],
      },
      mockFetch as unknown as typeof fetch,
    );
    await load(ctx);
    expect(mockFetch).not.toHaveBeenCalled();
  });
});

describe('dashboard +page.ts load() — prompt mock mode', () => {
  it('scopes by entity_id and sets service_name to null', async () => {
    const ctx = makeLoadCtx({
      metadata: PROMPT_METADATA,
      registryType: RegistryType.Prompt,
      devMockEnabled: true,
      promptCardsWithEval: [],
    });
    const result = await load(ctx);
    expect(result.bundle.dashboard.applied_filters.entity_id).toBe('eval-uid-abc');
    expect(result.bundle.dashboard.applied_filters.service_name).toBeNull();
    expect(result.mockMode).toBe(true);
  });

  it('eval_profiles contains the prompt own profile as single locked option', async () => {
    const ctx = makeLoadCtx({
      metadata: PROMPT_METADATA,
      registryType: RegistryType.Prompt,
      devMockEnabled: true,
      promptCardsWithEval: [],
    });
    const { bundle } = await load(ctx);
    expect(bundle.eval_profiles).toHaveLength(1);
    expect(bundle.eval_profiles[0].uid).toBe('eval-uid-abc');
    expect(bundle.eval_profiles[0].alias).toBe('v1');
  });
});

describe('dashboard +page.ts load() — API live mode', () => {
  it('calls fetch and returns mockMode: false on success', async () => {
    const dashboardResponse = {
      applied_filters: {
        service_name: 'fraud-detection:triage-agent',
        entity_id: null,
        agent_name: null,
        provider_name: null,
        operation_name: null,
        model: null,
        start_time: '2026-01-01T00:00:00Z',
        end_time: '2026-01-02T00:00:00Z',
        bucket_interval: 'hour',
      },
      available_filters: { agents: [], providers: [], models: [], operations: [] },
      metadata: { generated_at: '2026-01-02T00:00:00Z', schema_version: 1, total_spans: 0 },
      token_metrics: { buckets: [] },
      operation_breakdown: { operations: [] },
      model_usage: { models: [] },
      agent_dashboard: {
        summary: {
          total_requests: 0, avg_duration_ms: 0, p50_duration_ms: null, p95_duration_ms: null,
          p99_duration_ms: null, overall_error_rate: 0, total_input_tokens: 0,
          total_output_tokens: 0, total_cache_creation_tokens: 0, total_cache_read_tokens: 0,
          unique_agent_count: 0, unique_conversation_count: 0, cost_by_model: [],
        },
        buckets: [],
      },
      tool_dashboard: { aggregates: [], time_series: [] },
      error_breakdown: { errors: [] },
      buckets_truncated: false,
    };

    const mockFetch = vi.fn().mockResolvedValue(
      new Response(JSON.stringify(dashboardResponse), {
        status: 200,
        headers: { 'Content-Type': 'application/json' },
      }),
    );

    const ctx = makeLoadCtx(
      {
        metadata: AGENT_METADATA,
        registryType: RegistryType.Agent,
        devMockEnabled: false,
        promptCardsWithEval: [],
      },
      mockFetch as unknown as typeof fetch,
    );

    const result = await load(ctx);
    expect(mockFetch).toHaveBeenCalledOnce();
    expect(result.mockMode).toBe(false);
    expect(result.bundle.dashboard.applied_filters.service_name).toBe('fraud-detection:triage-agent');
  });

  it('falls back to mock bundle when API throws', async () => {
    const mockFetch = vi.fn().mockRejectedValue(new Error('network error'));

    const ctx = makeLoadCtx(
      {
        metadata: AGENT_METADATA,
        registryType: RegistryType.Agent,
        devMockEnabled: false,
        promptCardsWithEval: [],
      },
      mockFetch as unknown as typeof fetch,
    );

    const result = await load(ctx);
    expect(result.mockMode).toBe(true);
    expect(result.bundle).toBeDefined();
    expect(result.bundle.dashboard).toHaveProperty('agent_dashboard');
  });
});

describe('toEvalProfileOptions', () => {
  it('returns empty array when no cards have eval_profile', () => {
    const cards = [makeCard(), makeCard({ name: 'other' })];
    expect(toEvalProfileOptions(cards)).toEqual([]);
  });

  it('includes only cards that have eval_profile', () => {
    const withProfile = makeCard({
      name: 'with-profile',
      eval_profile: {
        alias: 'my-alias',
        config: { uid: 'profile-uid-1' },
      } as never,
    });
    const withoutProfile = makeCard({ name: 'no-profile' });
    const result = toEvalProfileOptions([withProfile, withoutProfile]);
    expect(result).toHaveLength(1);
    expect(result[0].uid).toBe('profile-uid-1');
  });

  it('maps alias and name correctly', () => {
    const card = makeCard({
      name: 'my-prompt',
      eval_profile: {
        alias: 'eval-alias',
        config: { uid: 'uid-abc' },
      } as never,
    });
    const result = toEvalProfileOptions([card]);
    expect(result[0]).toEqual({ uid: 'uid-abc', alias: 'eval-alias', name: 'my-prompt' });
  });

  it('sets alias to null when eval_profile.alias is undefined', () => {
    const card = makeCard({
      name: 'my-prompt',
      eval_profile: {
        alias: undefined,
        config: { uid: 'uid-xyz' },
      } as never,
    });
    const result = toEvalProfileOptions([card]);
    expect(result[0].alias).toBeNull();
  });
});
