import { describe, expect, it } from "vitest";
import {
  andClause,
  attrClause,
  durationMaxClause,
  durationMinClause,
  hasErrorsClause,
  serviceClause,
  serviceInstanceIdClause,
  serviceNamespaceClause,
  serviceVersionClause,
  statusCodeClause,
} from "../clause";
import type { TracePageFilter } from "../types";
import { derivedActiveFilters, removeActiveFilter } from "./filterState.svelte";

function makeFilterState(): TracePageFilter {
  return {
    bucket_interval: "minute",
    selected_range: "15min",
    filters: {
      clause: andClause(
        serviceClause("svc-a"),
        serviceNamespaceClause("prod"),
        serviceVersionClause("1.2.3"),
        serviceInstanceIdClause("pod-a"),
        statusCodeClause(2),
        hasErrorsClause(true),
        durationMinClause(100),
        durationMaxClause(300),
        attrClause("component", "kafka"),
        attrClause("env", "prod"),
      ),
    },
  };
}

describe("derivedActiveFilters", () => {
  it("derives all active chips from the clause state", () => {
    const chips = derivedActiveFilters(makeFilterState());
    expect(chips.map((chip) => chip.label)).toEqual([
      "Service: svc-a",
      "Namespace: prod",
      "Version: 1.2.3",
      "Instance: pod-a",
      "Status: 2",
      "Has errors: true",
      "Min duration: 100ms",
      "Max duration: 300ms",
      "Attr: component=kafka",
      "Attr: env=prod",
    ]);
  });
});

describe("removeActiveFilter", () => {
  it("removes duration bounds from server-backed filters", () => {
    const chips = derivedActiveFilters(makeFilterState());
    const next = removeActiveFilter(
      makeFilterState(),
      chips.find((chip) => chip.label === "Min duration: 100ms")!,
    );
    expect(derivedActiveFilters(next).map((chip) => chip.label)).not.toContain(
      "Min duration: 100ms",
    );
    expect(derivedActiveFilters(next).map((chip) => chip.label)).toContain(
      "Max duration: 300ms",
    );
  });

  it("removes a single attribute filter", () => {
    const initial = makeFilterState();
    const chips = derivedActiveFilters(initial);
    const oneRemoved = removeActiveFilter(
      initial,
      chips.find((chip) => chip.label === "Attr: component=kafka")!,
    );
    expect(derivedActiveFilters(oneRemoved).map((chip) => chip.label)).toContain(
      "Attr: env=prod",
    );
    expect(derivedActiveFilters(oneRemoved).map((chip) => chip.label)).not.toContain(
      "Attr: component=kafka",
    );
  });

  it("removes service identity/status/error chips from the clause", () => {
    let next = makeFilterState();
    for (const label of [
      "Service: svc-a",
      "Namespace: prod",
      "Version: 1.2.3",
      "Instance: pod-a",
      "Status: 2",
      "Has errors: true",
    ]) {
      const chip = derivedActiveFilters(next).find((item) => item.label === label);
      expect(chip).toBeDefined();
      next = removeActiveFilter(next, chip!);
    }
    const labels = derivedActiveFilters(next).map((chip) => chip.label);
    expect(labels).not.toContain("Service: svc-a");
    expect(labels).not.toContain("Namespace: prod");
    expect(labels).not.toContain("Version: 1.2.3");
    expect(labels).not.toContain("Instance: pod-a");
    expect(labels).not.toContain("Status: 2");
    expect(labels).not.toContain("Has errors: true");
  });
});
