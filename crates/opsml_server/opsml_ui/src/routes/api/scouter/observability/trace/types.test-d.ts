import { expectTypeOf } from "vitest";
import type {
  TraceFilters,
  TraceMetricsRequest,
} from "$lib/components/trace/types";

expectTypeOf<TraceFilters>().not.toHaveProperty("service_name");
expectTypeOf<TraceFilters>().not.toHaveProperty("status_code");
expectTypeOf<TraceFilters>().not.toHaveProperty("has_errors");
expectTypeOf<TraceFilters>().not.toHaveProperty("attribute_filters");
expectTypeOf<TraceFilters>().not.toHaveProperty("duration_min_ms");
expectTypeOf<TraceFilters>().not.toHaveProperty("duration_max_ms");
expectTypeOf<TraceFilters>().not.toHaveProperty("queue_uid");
expectTypeOf<TraceFilters>().toHaveProperty("clause");
expectTypeOf<TraceMetricsRequest>().not.toHaveProperty("service_name");
