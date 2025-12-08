// Base data for trace page.
// This needs to be client-side because we need to calculate max data points from window size
export const ssr = false;

import type { PageLoad } from "./$types";
import {
  mockTraceMetrics,
  mockTracePaginationResponse,
} from "$lib/components/card/trace/mock";

export const load: PageLoad = async ({ parent, fetch }) => {
  return {
    space: "space",
    name: "name",
    version: "1.0.0",
    trace_page: mockTracePaginationResponse,
    trace_metrics: mockTraceMetrics,
  };
};
