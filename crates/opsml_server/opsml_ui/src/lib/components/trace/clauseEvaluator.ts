import type { FilterClause } from "./clause";
import type { Attribute, TraceListItem } from "./types";

export function resourceAttr(
  attrs: Attribute[] | undefined,
  key: string,
): string | undefined {
  const hit = attrs?.find((attr) => attr.key === key);
  return hit === undefined ? undefined : String(hit.value);
}

export function evaluateClause(
  item: TraceListItem,
  clause: FilterClause,
): boolean {
  switch (clause.op) {
    case "and":
      return clause.value.every((child) => evaluateClause(item, child));
    case "or":
      return clause.value.some((child) => evaluateClause(item, child));
    case "not":
      return !evaluateClause(item, clause.value);
    case "service":
      return item.service_name === clause.value;
    case "service_namespace":
      return resourceAttr(item.resource_attributes, "service.namespace") === clause.value;
    case "service_version":
      return resourceAttr(item.resource_attributes, "service.version") === clause.value;
    case "service_instance_id":
      return resourceAttr(item.resource_attributes, "service.instance.id") === clause.value;
    case "status_code":
      return item.status_code === clause.value;
    case "has_errors":
      return item.has_errors === clause.value;
    case "duration_min_ms":
      return (item.duration_ms ?? 0) >= clause.value;
    case "duration_max_ms":
      return (item.duration_ms ?? Number.POSITIVE_INFINITY) <= clause.value;
    case "attr":
      return resourceAttr(item.resource_attributes, clause.value.key) === clause.value.value;
    case "phrase": {
      const haystack = `${item.root_operation} ${item.service_name}`.toLowerCase();
      return haystack.includes(clause.value.toLowerCase());
    }
  }
}
