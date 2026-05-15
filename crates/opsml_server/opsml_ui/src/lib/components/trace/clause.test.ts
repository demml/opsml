import { describe, expect, it } from "vitest";
import {
  addToClause,
  andClause,
  attrClause,
  clauseToActiveFilters,
  durationMaxClause,
  durationMinClause,
  findClauses,
  hasDimension,
  hasErrorsClause,
  notClause,
  orClause,
  phraseClause,
  removeAttr,
  removeClauseDimension,
  replaceClauseDimension,
  serviceClause,
  serviceInstanceIdClause,
  serviceNamespaceClause,
  serviceVersionClause,
  statusCodeClause,
} from "./clause";

describe("FilterClause builders and combinators", () => {
  it("builds leaf clauses", () => {
    expect(serviceClause("checkout")).toEqual({ op: "service", value: "checkout" });
    expect(serviceNamespaceClause("prod")).toEqual({ op: "service_namespace", value: "prod" });
    expect(serviceVersionClause("1.2.3")).toEqual({ op: "service_version", value: "1.2.3" });
    expect(serviceInstanceIdClause("pod-a")).toEqual({ op: "service_instance_id", value: "pod-a" });
    expect(statusCodeClause(500)).toEqual({ op: "status_code", value: 500 });
    expect(hasErrorsClause(true)).toEqual({ op: "has_errors", value: true });
    expect(durationMinClause(100)).toEqual({ op: "duration_min_ms", value: 100 });
    expect(durationMaxClause(500)).toEqual({ op: "duration_max_ms", value: 500 });
    expect(attrClause("env", "prod")).toEqual({ op: "attr", value: { key: "env", value: "prod" } });
    expect(phraseClause("timeout")).toEqual({ op: "phrase", value: "timeout" });
  });

  it("handles empty and single-child AND clauses", () => {
    const service = serviceClause("checkout");
    expect(andClause()).toBeUndefined();
    expect(andClause(service)).toEqual(service);
  });

  it("builds and flattens AND clauses", () => {
    const a = serviceClause("checkout");
    const b = statusCodeClause(500);
    const c = hasErrorsClause(true);
    expect(andClause(a, b)).toEqual({ op: "and", value: [a, b] });
    expect(andClause(andClause(a, b), c)).toEqual({ op: "and", value: [a, b, c] });
  });

  it("handles empty and single-child OR clauses", () => {
    const service = serviceClause("checkout");
    expect(orClause()).toBeUndefined();
    expect(orClause(service)).toEqual(service);
  });

  it("builds and flattens OR clauses", () => {
    const a = serviceClause("checkout");
    const b = serviceClause("payments");
    const c = serviceClause("catalog");
    expect(orClause(a, b)).toEqual({ op: "or", value: [a, b] });
    expect(orClause(orClause(a, b), c)).toEqual({ op: "or", value: [a, b, c] });
  });

  it("builds explicit NOT clauses without simplification", () => {
    const service = serviceClause("checkout");
    expect(notClause(service)).toEqual({ op: "not", value: service });
    expect(notClause(notClause(service))).toEqual({
      op: "not",
      value: { op: "not", value: service },
    });
  });
});

describe("FilterClause mutators", () => {
  it("adds a clause to an empty tree", () => {
    expect(addToClause(undefined, serviceClause("checkout"))).toEqual(serviceClause("checkout"));
  });

  it("adds a clause by flattening with AND", () => {
    const service = serviceClause("checkout");
    const status = statusCodeClause(500);
    const errors = hasErrorsClause(true);
    expect(addToClause(andClause(service, status), errors)).toEqual({
      op: "and",
      value: [service, status, errors],
    });
  });

  it("removes one dimension and unwraps the remaining child", () => {
    expect(removeClauseDimension(andClause(serviceClause("a"), statusCodeClause(500)), "service")).toEqual(
      statusCodeClause(500),
    );
  });

  it("collapses when every matching dimension disappears", () => {
    expect(removeClauseDimension(andClause(serviceClause("a"), serviceClause("b")), "service")).toBeUndefined();
  });

  it("removes duration min and max together", () => {
    expect(
      removeClauseDimension(
        andClause(durationMinClause(100), durationMaxClause(500), statusCodeClause(500)),
        "duration",
      ),
    ).toEqual(statusCodeClause(500));
  });

  it("collapses NOT when the inner leaf is removed", () => {
    expect(removeClauseDimension(notClause(serviceClause("a")), "service")).toBeUndefined();
  });

  it("removes one matching attribute leaf", () => {
    expect(removeAttr(andClause(attrClause("env", "prod"), attrClause("region", "us")), "env", "prod")).toEqual(
      attrClause("region", "us"),
    );
  });

  it("replaces an absent dimension by adding it", () => {
    expect(replaceClauseDimension(undefined, "service", serviceClause("b"))).toEqual(serviceClause("b"));
  });

  it("replaces an existing dimension in place", () => {
    expect(
      replaceClauseDimension(andClause(serviceClause("a"), statusCodeClause(500)), "service", serviceClause("b")),
    ).toEqual(andClause(serviceClause("b"), statusCodeClause(500)));
  });

  it("finds clauses and dimensions anywhere in the tree", () => {
    const clause = andClause(notClause(serviceClause("a")), durationMinClause(100));
    expect(findClauses(clause, "service")).toEqual([serviceClause("a")]);
    expect(hasDimension(clause, "duration")).toBe(true);
    expect(hasDimension(clause, "status_code")).toBe(false);
  });

  it("removes phrase leaves by dimension", () => {
    expect(removeClauseDimension(andClause(phraseClause("timeout"), serviceClause("a")), "phrase")).toEqual(
      serviceClause("a"),
    );
  });
});

describe("FilterClause projection", () => {
  it("returns no chips for an empty clause", () => {
    expect(clauseToActiveFilters(undefined)).toEqual([]);
  });

  it("projects a single leaf", () => {
    expect(clauseToActiveFilters(serviceClause("checkout")).map((chip) => chip.label)).toEqual([
      "Service: checkout",
    ]);
  });

  it("projects AND leaves in document order", () => {
    const labels = clauseToActiveFilters(
      andClause(serviceClause("checkout"), statusCodeClause(500), attrClause("env", "prod")),
    ).map((chip) => chip.label);
    expect(labels).toEqual(["Service: checkout", "Status: 500", "Attr: env=prod"]);
  });

  it("removes only the selected attr chip through its closure", () => {
    const clause = andClause(attrClause("env", "prod"), attrClause("region", "us"));
    const chips = clauseToActiveFilters(clause);
    expect(chips[0].remove(clause)).toEqual(attrClause("region", "us"));
  });

  it("removes every service leaf through a service chip closure", () => {
    const clause = andClause(serviceClause("a"), serviceClause("b"), statusCodeClause(500));
    const chips = clauseToActiveFilters(clause);
    expect(chips[0].remove(clause)).toEqual(statusCodeClause(500));
  });

  it("gives every chip a unique id", () => {
    const chips = clauseToActiveFilters(andClause(serviceClause("a"), serviceClause("a"), statusCodeClause(500)));
    expect(new Set(chips.map((chip) => chip.id)).size).toBe(chips.length);
  });

  it("projects phrase chips", () => {
    expect(clauseToActiveFilters(phraseClause("timeout")).map((chip) => chip.label)).toEqual([
      "Phrase: timeout",
    ]);
  });
});
