import type { TracePageFilter } from "../types";
import {
  clauseToActiveFilters,
  type ActiveFilter,
} from "../clause";

export function derivedActiveFilters(page: TracePageFilter): ActiveFilter[] {
  return clauseToActiveFilters(page.filters.clause);
}

export function removeActiveFilter(
  page: TracePageFilter,
  filter: ActiveFilter,
): TracePageFilter {
  const nextClause = filter.remove(page.filters.clause);
  return {
    ...page,
    filters: {
      ...page.filters,
      clause: nextClause,
    },
  };
}
