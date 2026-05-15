import { describe, expect, it } from "vitest";
import {
  andClause,
  attrClause,
  durationMaxClause,
  durationMinClause,
  hasErrorsClause,
  notClause,
  orClause,
  serviceClause,
  serviceNamespaceClause,
  statusCodeClause,
} from "../clause";
import { getMockTraceFacets, getMockTracePage } from "../mockData";

describe("trace mock FilterClause evaluation", () => {
  it("filters by AND of service and status code", () => {
    const page = getMockTracePage({
      clause: andClause(serviceClause("inference-api"), statusCodeClause(2)),
      limit: 100,
    });
    expect(page.items.length).toBeGreaterThan(0);
    expect(page.items.every((item) => item.service_name === "inference-api" && item.status_code === 2)).toBe(true);
  });

  it("filters by OR of two services", () => {
    const page = getMockTracePage({
      clause: orClause(serviceClause("inference-api"), serviceClause("llm-gateway")),
      limit: 100,
    });
    expect(page.items.length).toBeGreaterThan(0);
    expect(page.items.every((item) => ["inference-api", "llm-gateway"].includes(item.service_name))).toBe(true);
  });

  it("filters by NOT has_errors", () => {
    const page = getMockTracePage({
      clause: notClause(hasErrorsClause(true)),
      limit: 100,
    });
    expect(page.items.length).toBeGreaterThan(0);
    expect(page.items.every((item) => item.has_errors === false)).toBe(true);
  });

  it("matches service namespace through resource attributes", () => {
    const matched = getMockTracePage({
      clause: serviceNamespaceClause("models"),
      limit: 100,
    });
    const missing = getMockTracePage({
      clause: serviceNamespaceClause("missing"),
      limit: 100,
    });
    expect(matched.items.length).toBeGreaterThan(0);
    expect(missing.items).toHaveLength(0);
  });

  it("matches arbitrary resource attributes", () => {
    const page = getMockTracePage({
      clause: attrClause("service.version", "1.0.0"),
      limit: 100,
    });
    expect(page.items.length).toBeGreaterThan(0);
    expect(page.items.every((item) => item.service_name === "llm-gateway")).toBe(true);
  });

  it("bounds duration with min and max clauses", () => {
    const page = getMockTracePage({
      clause: andClause(durationMinClause(300), durationMaxClause(1000)),
      limit: 100,
    });
    expect(page.items.length).toBeGreaterThan(0);
    expect(page.items.every((item) => (item.duration_ms ?? 0) >= 300 && (item.duration_ms ?? 0) <= 1000)).toBe(true);
  });

  it("returns all items when no clause is present", () => {
    const withoutClause = getMockTracePage({ limit: 100 });
    const withImpossibleClause = getMockTracePage({
      clause: serviceClause("does-not-exist"),
      limit: 100,
    });
    expect(withoutClause.items.length).toBeGreaterThan(withImpossibleClause.items.length);
    expect(withImpossibleClause.items).toHaveLength(0);
  });

  it("applies time and entity filters consistently to page and facet mocks", () => {
    const filters = {
      start_time: "2099-01-01T00:00:00Z",
      end_time: "2099-01-01T00:15:00Z",
      entity_uid: "missing-entity",
      limit: 100,
    };

    const page = getMockTracePage(filters);
    const facets = getMockTraceFacets(filters);

    expect(page.items).toHaveLength(0);
    expect(facets.total_count).toBe(0);
    expect(facets.services).toHaveLength(0);
    expect(facets.status_codes).toHaveLength(0);
  });
});
