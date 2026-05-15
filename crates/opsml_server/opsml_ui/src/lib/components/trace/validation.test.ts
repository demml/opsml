import { describe, expect, it } from "vitest";
import { andClause, serviceClause, statusCodeClause } from "./clause";
import { validateTraceFilters, validateTraceMetricsRequest } from "./validation";

describe("trace request validation", () => {
  it("accepts representative clause-shaped trace filters", () => {
    const input = {
      clause: andClause(serviceClause("checkout"), statusCodeClause(500)),
      start_time: "2026-01-01T00:00:00Z",
      end_time: "2026-01-02T00:00:00Z",
      limit: 50,
    };
    expect(validateTraceFilters(input)).toEqual({ ok: true, value: input });
  });

  it("rejects unknown top-level fields", () => {
    expect(validateTraceFilters({ service_name: "checkout" })).toEqual({
      ok: false,
      error: "unknown field: service_name",
    });
  });

  it("rejects unknown clause fields", () => {
    expect(validateTraceFilters({ clause: { op: "service", value: "checkout", extra: true } })).toEqual({
      ok: false,
      error: "clause contains unknown field: extra",
    });
  });

  it("rejects unsupported clause ops", () => {
    expect(validateTraceFilters({ clause: { op: "service_name", value: "checkout" } })).toEqual({
      ok: false,
      error: "unsupported clause op: service_name",
    });
  });

  it("rejects invalid limits and inverted time ranges", () => {
    expect(validateTraceFilters({ limit: 1000 })).toEqual({
      ok: false,
      error: "limit must be between 1 and 500",
    });
    expect(validateTraceFilters({
      start_time: "2026-01-02T00:00:00Z",
      end_time: "2026-01-01T00:00:00Z",
    })).toEqual({
      ok: false,
      error: "start_time must be before end_time",
    });
  });

  it("requires metrics start and end times", () => {
    expect(validateTraceMetricsRequest({ end_time: "2026-01-02T00:00:00Z" })).toEqual({
      ok: false,
      error: "start_time and end_time are required",
    });
  });

  it("accepts metrics requests with optional bucket interval", () => {
    const input = {
      start_time: "2026-01-01T00:00:00Z",
      end_time: "2026-01-02T00:00:00Z",
      bucket_interval: "1 hours",
    };
    expect(validateTraceMetricsRequest(input)).toEqual({ ok: true, value: input });
  });
});
