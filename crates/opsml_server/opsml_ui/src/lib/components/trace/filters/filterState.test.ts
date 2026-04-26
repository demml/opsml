import { describe, expect, it } from "vitest";
import { derivedActiveFilters, removeActiveFilter } from "./filterState.svelte";
import type { TracePageFilter } from "../types";

function makeFilterState(): TracePageFilter {
  return {
    bucket_interval: "minute",
    selected_range: "15min",
    filters: {
      service_name: "svc-a",
      status_code: 2,
      has_errors: true,
      duration_min_ms: 100,
      duration_max_ms: 300,
      attribute_filters: ["component=kafka", "env=prod"],
    },
  };
}

describe("derivedActiveFilters", () => {
  it("derives all active chips from the unified filter state", () => {
    const chips = derivedActiveFilters(makeFilterState());
    expect(chips).toEqual([
      { key: "service_name", label: "Service", value: "svc-a" },
      { key: "status_code", label: "Status", value: "2" },
      { key: "has_errors", label: "Has errors", value: "true" },
      { key: "duration_min_ms", label: "Min duration", value: "100ms" },
      { key: "duration_max_ms", label: "Max duration", value: "300ms" },
      {
        key: "attribute",
        label: "Attr",
        value: "component=kafka",
        attributeRaw: "component=kafka",
      },
      {
        key: "attribute",
        label: "Attr",
        value: "env=prod",
        attributeRaw: "env=prod",
      },
    ]);
  });
});

describe("removeActiveFilter", () => {
  it("removes duration bounds from server-backed filters", () => {
    const next = removeActiveFilter(makeFilterState(), {
      key: "duration_min_ms",
      label: "Min duration",
      value: "100ms",
    });
    expect(next.filters.duration_min_ms).toBeUndefined();
    expect(next.filters.duration_max_ms).toBe(300);
  });

  it("removes a single attribute filter and drops the list when empty", () => {
    const initial = makeFilterState();
    const oneRemoved = removeActiveFilter(initial, {
      key: "attribute",
      label: "Attr",
      value: "component=kafka",
      attributeRaw: "component=kafka",
    });
    expect(oneRemoved.filters.attribute_filters).toEqual(["env=prod"]);

    const allRemoved = removeActiveFilter(
      {
        ...initial,
        filters: { ...initial.filters, attribute_filters: ["env=prod"] },
      },
      {
        key: "attribute",
        label: "Attr",
        value: "env=prod",
        attributeRaw: "env=prod",
      },
    );
    expect(allRemoved.filters.attribute_filters).toBeUndefined();
  });

  it("removes service/status/error chips from the main filter object", () => {
    let next = removeActiveFilter(makeFilterState(), {
      key: "service_name",
      label: "Service",
      value: "svc-a",
    });
    next = removeActiveFilter(next, {
      key: "status_code",
      label: "Status",
      value: "2",
    });
    next = removeActiveFilter(next, {
      key: "has_errors",
      label: "Has errors",
      value: "true",
    });
    expect(next.filters.service_name).toBeUndefined();
    expect(next.filters.status_code).toBeUndefined();
    expect(next.filters.has_errors).toBeUndefined();
  });
});
