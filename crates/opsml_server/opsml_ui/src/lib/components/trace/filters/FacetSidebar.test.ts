import { fireEvent, render, screen } from "@testing-library/svelte";
import { describe, expect, it, vi } from "vitest";
import { andClause, serviceClause, statusCodeClause } from "../clause";
import type { TracePageFilter } from "../types";
import FacetSidebar from "./FacetSidebar.svelte";

function renderSidebar(overrides: Partial<TracePageFilter["filters"]> = {}) {
  const filters: TracePageFilter = {
    bucket_interval: "1 minutes",
    selected_range: "15min",
    filters: {
      clause: andClause(serviceClause("checkout"), statusCodeClause(500)),
      ...overrides,
    },
  };
  const props = {
    filters,
    services: [
      { value: "checkout", count: 3 },
      { value: "payments", count: 2 },
    ],
    namespaces: [],
    versions: [],
    instances: [],
    statuses: [{ value: "500", count: 3 }],
    onSetService: vi.fn(),
    onClearService: vi.fn(),
    onSetNamespace: vi.fn(),
    onClearNamespace: vi.fn(),
    onSetVersion: vi.fn(),
    onClearVersion: vi.fn(),
    onSetInstance: vi.fn(),
    onClearInstance: vi.fn(),
    onSetStatus: vi.fn(),
    onClearStatus: vi.fn(),
    onToggleErrors: vi.fn(),
    onSetDuration: vi.fn(),
    onSetAttributes: vi.fn(),
  };

  render(FacetSidebar, { props });
  return props;
}

describe("FacetSidebar", () => {
  it("uses clause state for service and status selection callbacks", async () => {
    const props = renderSidebar();
    await fireEvent.click(screen.getByText("payments"));
    await fireEvent.click(screen.getByText("500"));
    expect(props.onSetService).toHaveBeenCalledWith("payments");
    expect(props.onSetStatus).toHaveBeenCalledWith(500);
  });

  it("keeps unsupported facet axes as manual controls", async () => {
    const props = renderSidebar();
    await fireEvent.input(screen.getByPlaceholderText("namespace"), {
      target: { value: "prod" },
    });
    await fireEvent.click(screen.getAllByText("Apply")[0]);
    expect(props.onSetNamespace).toHaveBeenCalledWith("prod");
  });
});
