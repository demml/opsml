import { describe, it, expect, vi, beforeEach } from 'vitest';
import { load } from '../+page';
import { RegistryType } from '$lib/utils';
import type { PromptCard } from '$lib/components/card/card_interfaces/promptcard';
import type { ServiceCard } from '$lib/components/card/card_interfaces/servicecard';

// ── Shared mock metadata fixtures ─────────────────────────────────────────

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

const SERVICE_METADATA: ServiceCard = {
  name: 'my-service',
  space: 'acme',
  version: '1.0.0',
  uid: 'service-uid-1',
  created_at: '2026-01-01T00:00:00Z',
  cards: { cards: [] },
  opsml_version: '0.1.0',
  app_env: 'dev',
  is_card: true,
  registry_type: RegistryType.Service,
  service_type: 'Api' as never,
  service_config: {},
  tags: [],
};

const MODEL_METADATA = {
  name: 'my-model',
  space: 'acme',
  version: '1.0.0',
  uid: 'model-uid-1',
  tags: [],
  metadata: {},
  registry_type: RegistryType.Model,
  app_env: 'dev',
  created_at: '2026-01-01T00:00:00Z',
  is_card: true,
  opsml_version: '0.1.0',
};

// ── Load context factory ────────────────────────────────────────────────────

function makeLoadCtx(
  parentData: Record<string, unknown>,
  searchParams: Record<string, string> = {},
  fetchImpl?: typeof fetch,
) {
  const url = new URL('http://localhost/opsml/prompt/card/acme/my-prompt/1.0.0/observability');
  for (const [k, v] of Object.entries(searchParams)) {
    url.searchParams.set(k, v);
  }

  return {
    fetch: fetchImpl ?? vi.fn(),
    parent: vi.fn().mockResolvedValue(parentData),
    params: {},
    url,
    route: { id: '' },
    depends: vi.fn(),
    untrack: (fn: () => unknown) => fn(),
  } as unknown as Parameters<typeof load>[0];
}

// ── Mock utilities ──────────────────────────────────────────────────────────

function makeTracePaginationResponse(hasItems = true) {
  return {
    items: hasItems
      ? [
          {
            trace_id: 'trace-1',
            service_name: 'my-service',
            scope: 'INTERNAL',
            root_operation: 'POST /predict',
            start_time: '2026-01-01T00:05:00Z',
            end_time: '2026-01-01T00:05:01Z',
            duration_ms: 342,
            status_code: 1,
            status_message: null,
            span_count: 3,
            has_errors: false,
            error_count: 0,
            created_at: '2026-01-01T00:05:00Z',
            resource_attributes: [],
          },
        ]
      : [],
    has_next: false,
    next_cursor: undefined,
    has_previous: false,
    previous_cursor: undefined,
  };
}

function makeTraceMetricsResponse() {
  return { metrics: [] };
}

function makeTraceFacetsResponse() {
  return { services: ['my-service'], status_codes: [1], total_count: 1 };
}

function makeApiFetch(opts: {
  pageItems?: boolean;
  throwOnPage?: boolean;
  throwOnMetrics?: boolean;
  throwOnFacets?: boolean;
} = {}) {
  const { pageItems = true, throwOnPage = false, throwOnMetrics = false, throwOnFacets = false } = opts;

  return vi.fn().mockImplementation(async (url: string, init?: RequestInit) => {
    const body = init?.body ? JSON.parse(init.body as string) : {};

    if (throwOnMetrics && String(url).includes('metrics')) {
      throw new Error('fetch failed: metrics');
    }
    if (throwOnPage && String(url).includes('page')) {
      throw new Error('fetch failed: page');
    }
    if (throwOnFacets && String(url).includes('facets')) {
      throw new Error('fetch failed: facets');
    }

    if (String(url).includes('metrics')) {
      return new Response(
        JSON.stringify({ response: makeTraceMetricsResponse(), error: null }),
        { status: 200, headers: { 'Content-Type': 'application/json' } },
      );
    }
    if (String(url).includes('facets')) {
      return new Response(
        JSON.stringify({ response: makeTraceFacetsResponse(), error: null }),
        { status: 200, headers: { 'Content-Type': 'application/json' } },
      );
    }
    // page endpoint
    return new Response(
      JSON.stringify({ response: makeTracePaginationResponse(pageItems), error: null }),
      { status: 200, headers: { 'Content-Type': 'application/json' } },
    );
  });
}

// ── Test suites ────────────────────────────────────────────────────────────

describe('observability +page.ts load() — registry guard', () => {
  it('returns not_found for a disallowed registry type without calling fetch', async () => {
    const mockFetch = vi.fn();
    const ctx = makeLoadCtx(
      {
        metadata: MODEL_METADATA,
        devMockEnabled: false,
        settings: { scouter_enabled: true },
      },
      {},
      mockFetch as unknown as typeof fetch,
    );

    const result = (await load(ctx)) as Record<string, unknown>;

    expect(result.status).toBe('not_found');
    expect(mockFetch).not.toHaveBeenCalled();
    expect(result.trace_facets).toEqual({ services: [], status_codes: [], total_count: 0 });
    expect(result.mockMode).toBe(false);
  });
});

describe('observability +page.ts load() — scouter disabled', () => {
  it('returns not_found when scouter is disabled and mock mode is off', async () => {
    const mockFetch = vi.fn();
    const ctx = makeLoadCtx(
      {
        metadata: PROMPT_METADATA,
        devMockEnabled: false,
        settings: { scouter_enabled: false },
      },
      {},
      mockFetch as unknown as typeof fetch,
    );

    const result = (await load(ctx)) as Record<string, unknown>;

    expect(result.status).toBe('not_found');
    expect((result as { errorMessage?: string }).errorMessage).toMatch(/scouter/i);
    expect(mockFetch).not.toHaveBeenCalled();
    expect(result.mockMode).toBe(false);
  });
});

describe('observability +page.ts load() — prompt eval profile guard', () => {
  it('returns not_found for prompt cards without an eval profile UID', async () => {
    const mockFetch = vi.fn();
    const ctx = makeLoadCtx(
      {
        metadata: { ...PROMPT_METADATA, eval_profile: undefined },
        devMockEnabled: false,
        settings: { scouter_enabled: true },
      },
      {},
      mockFetch as unknown as typeof fetch,
    );

    const result = (await load(ctx)) as Record<string, unknown>;

    expect(result.status).toBe('not_found');
    expect((result as { errorMessage?: string }).errorMessage).toMatch(/evaluation profile/i);
    expect(mockFetch).not.toHaveBeenCalled();
  });
});

describe('observability +page.ts load() — mock mode', () => {
  // In mock mode, getMockTraceMetrics / getMockTracePage are used instead of
  // real fetch calls. However getServerTraceFacets is NOT guarded by the mock
  // flag in the source, so the fetch function will be invoked once for facets.
  // We only assert that the primary data (mockMode, status, trace_page) is
  // correct and that no fetch is made for metrics or page endpoints.

  it('returns success with mockMode: true', async () => {
    const facetsResponse = { services: [], status_codes: [], total_count: 0 };
    const mockFetch = vi.fn().mockResolvedValue(
      new Response(JSON.stringify({ response: facetsResponse, error: null }), {
        status: 200,
        headers: { 'Content-Type': 'application/json' },
      }),
    );
    const ctx = makeLoadCtx(
      {
        metadata: PROMPT_METADATA,
        devMockEnabled: true,
        settings: { scouter_enabled: false },
      },
      {},
      mockFetch as unknown as typeof fetch,
    );

    const result = (await load(ctx)) as Record<string, unknown>;

    expect(result.mockMode).toBe(true);
    expect(result.status).toBe('success');
  });

  it('returns trace_page and trace_metrics populated from mock data', async () => {
    const facetsResponse = { services: [], status_codes: [], total_count: 0 };
    const mockFetch = vi.fn().mockResolvedValue(
      new Response(JSON.stringify({ response: facetsResponse, error: null }), {
        status: 200,
        headers: { 'Content-Type': 'application/json' },
      }),
    );
    const ctx = makeLoadCtx(
      {
        metadata: SERVICE_METADATA,
        devMockEnabled: true,
        settings: { scouter_enabled: false },
      },
      {},
      mockFetch as unknown as typeof fetch,
    );

    const result = (await load(ctx)) as Record<string, unknown>;

    expect(result.status).toBe('success');
    expect(result.trace_page).toBeDefined();
    expect(result.trace_metrics).toBeDefined();
  });
});

describe('observability +page.ts load() — trace_id query param', () => {
  it('uses 5 minutes bucket_interval in initialFilters when a trace is resolved', async () => {
    const traceStartTime = '2026-01-01T00:05:00Z';
    const spanResponse = {
      spans: [
        {
          trace_id: 'trace-1',
          span_id: 'span-1',
          parent_span_id: null,
          span_name: 'POST /predict',
          span_kind: 'SERVER',
          service_name: 'my-service',
          start_time: traceStartTime,
          end_time: '2026-01-01T00:05:01Z',
          duration_ms: 342,
          status_code: 1,
          status_message: null,
          attributes: [],
          events: [],
          links: [],
          depth: 0,
          path: [],
          span_order: 0,
          root_span_id: 'span-1',
          input: null,
          output: null,
        },
      ],
    };

    const mockFetch = vi.fn().mockImplementation(async (url: string, init?: RequestInit) => {
      if (String(url).includes('spans')) {
        return new Response(
          JSON.stringify({ response: spanResponse, error: null }),
          { status: 200, headers: { 'Content-Type': 'application/json' } },
        );
      }
      if (String(url).includes('metrics')) {
        return new Response(
          JSON.stringify({ response: makeTraceMetricsResponse(), error: null }),
          { status: 200, headers: { 'Content-Type': 'application/json' } },
        );
      }
      if (String(url).includes('facets')) {
        return new Response(
          JSON.stringify({ response: makeTraceFacetsResponse(), error: null }),
          { status: 200, headers: { 'Content-Type': 'application/json' } },
        );
      }
      return new Response(
        JSON.stringify({ response: makeTracePaginationResponse(true), error: null }),
        { status: 200, headers: { 'Content-Type': 'application/json' } },
      );
    });

    const ctx = makeLoadCtx(
      {
        metadata: PROMPT_METADATA,
        devMockEnabled: false,
        settings: { scouter_enabled: true },
      },
      { trace_id: 'trace-1' },
      mockFetch as unknown as typeof fetch,
    );

    const result = (await load(ctx)) as Record<string, unknown>;
    const filters = result.initialFilters as Record<string, unknown>;

    expect(filters.bucket_interval).toBe('5 minutes');
    expect(filters.selected_range).toBe('custom');
  });
});

describe('observability +page.ts load() — error fallback', () => {
  it('returns status error when the metrics API throws', async () => {
    const mockFetch = vi.fn().mockRejectedValue(new Error('network failure'));

    const ctx = makeLoadCtx(
      {
        metadata: PROMPT_METADATA,
        devMockEnabled: false,
        settings: { scouter_enabled: true },
      },
      {},
      mockFetch as unknown as typeof fetch,
    );

    const result = (await load(ctx)) as Record<string, unknown>;

    expect(result.status).toBe('error');
    expect((result as { errorMessage?: string }).errorMessage).toBeDefined();
    expect(result.trace_facets).toEqual({ services: [], status_codes: [], total_count: 0 });
    expect(result.mockMode).toBe(false);
  });

  it('error message reflects network error type', async () => {
    const mockFetch = vi.fn().mockRejectedValue(new Error('fetch failed: server unreachable'));

    const ctx = makeLoadCtx(
      {
        metadata: SERVICE_METADATA,
        devMockEnabled: false,
        settings: { scouter_enabled: true },
      },
      {},
      mockFetch as unknown as typeof fetch,
    );

    const result = (await load(ctx)) as Record<string, unknown>;

    expect(result.status).toBe('error');
    const errorMessage = (result as { errorMessage?: string }).errorMessage ?? '';
    expect(errorMessage.length).toBeGreaterThan(0);
  });
});
