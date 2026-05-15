export type FilterClause =
  | { op: "and"; value: FilterClause[] }
  | { op: "or"; value: FilterClause[] }
  | { op: "not"; value: FilterClause }
  | { op: "phrase"; value: string }
  | { op: "service"; value: string }
  | { op: "service_namespace"; value: string }
  | { op: "service_version"; value: string }
  | { op: "service_instance_id"; value: string }
  | { op: "status_code"; value: number }
  | { op: "has_errors"; value: boolean }
  | { op: "duration_min_ms"; value: number }
  | { op: "duration_max_ms"; value: number }
  | { op: "attr"; value: { key: string; value: string } };

export type FilterClauseOp = FilterClause["op"];

export type ClauseDimension =
  | "service"
  | "service_namespace"
  | "service_version"
  | "service_instance_id"
  | "status_code"
  | "has_errors"
  | "duration_min_ms"
  | "duration_max_ms"
  | "duration"
  | "attr"
  | "phrase";

export interface ActiveFilter {
  id: string;
  label: string;
  remove: (clause: FilterClause | undefined) => FilterClause | undefined;
}

export const FACET_AXIS_TO_CLAUSE_OP = {
  service_name: "service",
  status_code: "status_code",
} as const satisfies Record<string, FilterClauseOp>;

export const serviceClause = (value: string): FilterClause => ({
  op: "service",
  value,
});
export const serviceNamespaceClause = (value: string): FilterClause => ({
  op: "service_namespace",
  value,
});
export const serviceVersionClause = (value: string): FilterClause => ({
  op: "service_version",
  value,
});
export const serviceInstanceIdClause = (value: string): FilterClause => ({
  op: "service_instance_id",
  value,
});
export const statusCodeClause = (value: number): FilterClause => ({
  op: "status_code",
  value,
});
export const hasErrorsClause = (value: boolean): FilterClause => ({
  op: "has_errors",
  value,
});
export const durationMinClause = (value: number): FilterClause => ({
  op: "duration_min_ms",
  value,
});
export const durationMaxClause = (value: number): FilterClause => ({
  op: "duration_max_ms",
  value,
});
export const attrClause = (key: string, value: string): FilterClause => ({
  op: "attr",
  value: { key, value },
});
export const phraseClause = (value: string): FilterClause => ({
  op: "phrase",
  value,
});

export function andClause(
  ...children: (FilterClause | undefined)[]
): FilterClause | undefined {
  return combineClause("and", children);
}

export function orClause(
  ...children: (FilterClause | undefined)[]
): FilterClause | undefined {
  return combineClause("or", children);
}

export function notClause(value: FilterClause): FilterClause {
  return { op: "not", value };
}

export function* iterateLeaves(
  clause: FilterClause | undefined,
): Iterable<FilterClause> {
  if (!clause) return;
  switch (clause.op) {
    case "and":
    case "or":
      for (const child of clause.value) {
        yield* iterateLeaves(child);
      }
      return;
    case "not":
      yield* iterateLeaves(clause.value);
      return;
    default:
      yield clause;
  }
}

export function findClauses<Op extends FilterClauseOp>(
  clause: FilterClause | undefined,
  op: Op,
): Extract<FilterClause, { op: Op }>[] {
  return Array.from(iterateLeaves(clause)).filter(
    (leaf): leaf is Extract<FilterClause, { op: Op }> => leaf.op === op,
  );
}

export function hasDimension(
  clause: FilterClause | undefined,
  dim: ClauseDimension,
): boolean {
  for (const leaf of iterateLeaves(clause)) {
    if (matchesDimension(leaf, dim)) return true;
  }
  return false;
}

export function addToClause(
  existing: FilterClause | undefined,
  added: FilterClause,
): FilterClause {
  return andClause(existing, added) ?? added;
}

export function removeClauseDimension(
  clause: FilterClause | undefined,
  dim: ClauseDimension,
): FilterClause | undefined {
  if (!clause) return undefined;

  switch (clause.op) {
    case "and":
    case "or": {
      const children = clause.value
        .map((child) => removeClauseDimension(child, dim))
        .filter((child): child is FilterClause => child !== undefined);
      return combineClause(clause.op, children);
    }
    case "not": {
      const inner = removeClauseDimension(clause.value, dim);
      return inner ? { op: "not", value: inner } : undefined;
    }
    default:
      return matchesDimension(clause, dim) ? undefined : cloneClause(clause);
  }
}

export function replaceClauseDimension(
  clause: FilterClause | undefined,
  dim: ClauseDimension,
  next: FilterClause | undefined,
): FilterClause | undefined {
  if (!next) return removeClauseDimension(clause, dim);

  const [replaced, found] = replaceDimensionInner(clause, dim, next);
  if (found) return replaced;
  return addToClause(replaced, next);
}

export function removeAttr(
  clause: FilterClause | undefined,
  key: string,
  value: string,
): FilterClause | undefined {
  if (!clause) return undefined;

  switch (clause.op) {
    case "and":
    case "or": {
      const children = clause.value
        .map((child) => removeAttr(child, key, value))
        .filter((child): child is FilterClause => child !== undefined);
      return combineClause(clause.op, children);
    }
    case "not": {
      const inner = removeAttr(clause.value, key, value);
      return inner ? { op: "not", value: inner } : undefined;
    }
    case "attr":
      return clause.value.key === key && clause.value.value === value
        ? undefined
        : cloneClause(clause);
    default:
      return cloneClause(clause);
  }
}

export function clauseToActiveFilters(
  clause: FilterClause | undefined,
): ActiveFilter[] {
  return Array.from(iterateLeaves(clause)).map((leaf, index) => ({
    id: `${index}:${leaf.op}:${leafLabelValue(leaf)}`,
    label: labelForLeaf(leaf),
    remove: removeForLeaf(leaf),
  }));
}

function combineClause(
  op: "and" | "or",
  children: (FilterClause | undefined)[],
): FilterClause | undefined {
  const flattened: FilterClause[] = [];
  for (const child of children) {
    if (!child) continue;
    if (child.op === op) flattened.push(...child.value.map(cloneClause));
    else flattened.push(cloneClause(child));
  }
  if (flattened.length === 0) return undefined;
  if (flattened.length === 1) return flattened[0];
  return { op, value: flattened };
}

function replaceDimensionInner(
  clause: FilterClause | undefined,
  dim: ClauseDimension,
  next: FilterClause,
): [FilterClause | undefined, boolean] {
  if (!clause) return [undefined, false];

  switch (clause.op) {
    case "and":
    case "or": {
      let found = false;
      let inserted = false;
      const children: FilterClause[] = [];
      for (const child of clause.value) {
        const [updated, childFound] = replaceDimensionInner(child, dim, next);
        found ||= childFound;
        if (childFound && !inserted) {
          children.push(cloneClause(next));
          inserted = true;
        }
        if (updated) children.push(updated);
      }
      return [combineClause(clause.op, children), found];
    }
    case "not": {
      const [inner, found] = replaceDimensionInner(clause.value, dim, next);
      return [inner ? { op: "not", value: inner } : undefined, found];
    }
    default:
      return matchesDimension(clause, dim)
        ? [undefined, true]
        : [cloneClause(clause), false];
  }
}

function matchesDimension(clause: FilterClause, dim: ClauseDimension): boolean {
  if (dim === "duration") {
    return clause.op === "duration_min_ms" || clause.op === "duration_max_ms";
  }
  return clause.op === dim;
}

function labelForLeaf(clause: FilterClause): string {
  switch (clause.op) {
    case "service":
      return `Service: ${clause.value}`;
    case "service_namespace":
      return `Namespace: ${clause.value}`;
    case "service_version":
      return `Version: ${clause.value}`;
    case "service_instance_id":
      return `Instance: ${clause.value}`;
    case "status_code":
      return `Status: ${clause.value}`;
    case "has_errors":
      return `Has errors: ${clause.value}`;
    case "duration_min_ms":
      return `Min duration: ${clause.value}ms`;
    case "duration_max_ms":
      return `Max duration: ${clause.value}ms`;
    case "attr":
      return `Attr: ${clause.value.key}=${clause.value.value}`;
    case "phrase":
      return `Phrase: ${clause.value}`;
    case "and":
    case "or":
    case "not":
      throw new Error(`Cannot label non-leaf clause ${clause.op}`);
  }
}

function leafLabelValue(clause: FilterClause): string {
  return clause.op === "attr"
    ? `${clause.value.key}=${clause.value.value}`
    : String(clause.value);
}

function removeForLeaf(
  clause: FilterClause,
): (clause: FilterClause | undefined) => FilterClause | undefined {
  if (clause.op === "attr") {
    const { key, value } = clause.value;
    return (current) => removeAttr(current, key, value);
  }
  const dim = dimensionForLeaf(clause);
  return (current) => removeClauseDimension(current, dim);
}

/**
 * Clones a clause without `structuredClone`.
 *
 * Clause objects can be wrapped in Svelte proxies when they come from component
 * state. `structuredClone` rejects those proxies, so the discriminated union is
 * copied manually before returning data to mutators.
 */
function cloneClause(clause: FilterClause): FilterClause {
  switch (clause.op) {
    case "and":
    case "or":
      return { op: clause.op, value: clause.value.map(cloneClause) };
    case "not":
      return { op: "not", value: cloneClause(clause.value) };
    case "attr":
      return { op: "attr", value: { key: clause.value.key, value: clause.value.value } };
    case "phrase":
    case "service":
    case "service_namespace":
    case "service_version":
    case "service_instance_id":
      return { op: clause.op, value: clause.value };
    case "status_code":
    case "duration_min_ms":
    case "duration_max_ms":
      return { op: clause.op, value: clause.value };
    case "has_errors":
      return { op: "has_errors", value: clause.value };
  }
}

function dimensionForLeaf(clause: FilterClause): ClauseDimension {
  switch (clause.op) {
    case "service":
    case "service_namespace":
    case "service_version":
    case "service_instance_id":
    case "status_code":
    case "has_errors":
    case "duration_min_ms":
    case "duration_max_ms":
    case "attr":
    case "phrase":
      return clause.op;
    case "and":
    case "or":
    case "not":
      throw new Error(`Cannot derive a filter dimension from ${clause.op}`);
  }
}
