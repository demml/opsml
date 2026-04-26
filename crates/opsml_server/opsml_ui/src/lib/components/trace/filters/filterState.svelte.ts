import type {
  ActiveFilter,
  TraceFilters,
  TracePageFilter,
} from "../types";

export function derivedActiveFilters(
  page: TracePageFilter,
): ActiveFilter[] {
  const f = page.filters;
  const out: ActiveFilter[] = [];

  if (f.service_name) {
    out.push({ key: "service_name", label: "Service", value: f.service_name });
  }
  if (typeof f.status_code === "number") {
    out.push({
      key: "status_code",
      label: "Status",
      value: String(f.status_code),
    });
  }
  if (f.has_errors) {
    out.push({ key: "has_errors", label: "Has errors", value: "true" });
  }
  if (typeof f.duration_min_ms === "number") {
    out.push({
      key: "duration_min_ms",
      label: "Min duration",
      value: `${f.duration_min_ms}ms`,
    });
  }
  if (typeof f.duration_max_ms === "number") {
    out.push({
      key: "duration_max_ms",
      label: "Max duration",
      value: `${f.duration_max_ms}ms`,
    });
  }
  for (const raw of f.attribute_filters ?? []) {
    out.push({
      key: "attribute",
      label: "Attr",
      value: raw,
      attributeRaw: raw,
    });
  }

  return out;
}

export function removeActiveFilter(
  page: TracePageFilter,
  filter: ActiveFilter,
): TracePageFilter {
  const nextFilters: TraceFilters = { ...page.filters };

  switch (filter.key) {
    case "service_name":
      delete nextFilters.service_name;
      break;
    case "status_code":
      delete nextFilters.status_code;
      break;
    case "has_errors":
      delete nextFilters.has_errors;
      break;
    case "duration_min_ms":
      delete nextFilters.duration_min_ms;
      break;
    case "duration_max_ms":
      delete nextFilters.duration_max_ms;
      break;
    case "attribute":
      nextFilters.attribute_filters = (nextFilters.attribute_filters ?? []).filter(
        (a) => a !== filter.attributeRaw,
      );
      if (nextFilters.attribute_filters.length === 0) {
        delete nextFilters.attribute_filters;
      }
      break;
  }

  return { ...page, filters: nextFilters };
}
