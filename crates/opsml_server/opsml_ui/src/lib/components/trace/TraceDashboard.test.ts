import { beforeEach, describe, expect, it, vi } from "vitest";
import { fireEvent, render, screen, waitFor } from "@testing-library/svelte";
import TraceDashboard from "./TraceDashboard.svelte";
import { andClause, serviceClause, statusCodeClause } from "./clause";
import type { TracePageFilter } from "./types";

const traceCalls = vi.hoisted(() => ({
  metrics: [] as unknown[],
  pages: [] as unknown[],
  facets: [] as unknown[],
}));

vi.mock("$app/navigation", () => ({
  replaceState: vi.fn(),
}));

vi.mock("$app/paths", () => ({
  resolve: (path: string) => path,
}));

vi.mock("chart.js/auto", () => ({
  Chart: class {
    static register = vi.fn();
    destroy = vi.fn();
    resetZoom = vi.fn();
  },
}));
vi.mock("chart.js", () => ({ Filler: {} }));
vi.mock("chartjs-plugin-zoom", () => ({ default: {} }));
vi.mock("chartjs-plugin-annotation", () => ({ default: {} }));
vi.mock("chartjs-adapter-date-fns", () => ({}));

vi.mock("./utils", async () => {
  const actual = await vi.importActual<typeof import("./utils")>("./utils");
  return {
    ...actual,
    setCookie: vi.fn(),
    getServerTraceMetrics: vi.fn(async (_fetch, body) => {
      traceCalls.metrics.push(body);
      return { metrics: [] };
    }),
    getServerTracePage: vi.fn(async (_fetch, body) => {
      traceCalls.pages.push(body);
      return {
        items: [],
        has_next: false,
        has_previous: false,
      };
    }),
    getServerTraceFacets: vi.fn(async (_fetch, body) => {
      traceCalls.facets.push(body);
      return {
        services: [{ value: "payments", trace_count: 2 }],
        status_codes: [{ value: "500", trace_count: 1 }],
        total_count: 2,
      };
    }),
  };
});

/** Builds the initial trace filter state used by the dashboard regression. */
function initialFilters(): TracePageFilter {
  return {
    bucket_interval: "1 hours",
    selected_range: "custom",
    filters: {
      clause: andClause(serviceClause("checkout"), statusCodeClause(500)),
      start_time: "2026-01-01T00:00:00Z",
      end_time: "2026-01-02T00:00:00Z",
    },
  };
}

describe("TraceDashboard filter requests", () => {
  beforeEach(() => {
    Object.defineProperty(window, "matchMedia", {
      writable: true,
      value: vi.fn().mockImplementation((query: string) => ({
        matches: false,
        media: query,
        onchange: null,
        addEventListener: vi.fn(),
        removeEventListener: vi.fn(),
        addListener: vi.fn(),
        removeListener: vi.fn(),
        dispatchEvent: vi.fn(),
      })),
    });
    Object.defineProperty(HTMLCanvasElement.prototype, "getContext", {
      writable: true,
      value: vi.fn(() => ({})),
    });
    Object.defineProperty(window, "ResizeObserver", {
      writable: true,
      value: class {
        observe = vi.fn();
        unobserve = vi.fn();
        disconnect = vi.fn();
      },
    });
    traceCalls.metrics.length = 0;
    traceCalls.pages.length = 0;
    traceCalls.facets.length = 0;
  });

  it("posts clause-shaped bodies for facet selection and chip removal", async () => {
    render(TraceDashboard, {
      props: {
        trace_page: { items: [], has_next: false, has_previous: false },
        trace_metrics: [],
        trace_facets: {
          services: [
            { value: "checkout", trace_count: 1 },
            { value: "payments", trace_count: 2 },
          ],
          status_codes: [{ value: "500", trace_count: 1 }],
          total_count: 2,
        },
        initialFilters: initialFilters(),
      },
    });

    await fireEvent.click(screen.getByText("payments"));

    await waitFor(() => expect(traceCalls.metrics).toHaveLength(1));
    expect(traceCalls.metrics[0]).toMatchObject({
      start_time: "2026-01-01T00:00:00Z",
      end_time: "2026-01-02T00:00:00Z",
      clause: andClause(serviceClause("payments"), statusCodeClause(500)),
    });
    expect(traceCalls.metrics[0]).not.toHaveProperty("service_name");
    expect(traceCalls.pages[0]).toMatchObject({
      limit: 50,
      clause: andClause(serviceClause("payments"), statusCodeClause(500)),
    });
    expect(traceCalls.facets[0]).toMatchObject({
      clause: statusCodeClause(500),
    });
    expect(traceCalls.facets[1]).toMatchObject({
      clause: serviceClause("payments"),
    });

    await fireEvent.click(screen.getByRole("button", { name: "Remove Service: payments" }));

    await waitFor(() => expect(traceCalls.metrics).toHaveLength(2));
    expect(traceCalls.metrics[1]).toMatchObject({
      clause: statusCodeClause(500),
    });
  });
});
