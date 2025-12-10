import type { PageLoad } from "./$types";
import type { TraceMetricsRequest } from "$lib/components/trace/types";
import {
  getServerTracePage,
  getServerTraceMetrics,
  getCookie,
  calculateTimeRange,
} from "$lib/components/trace/utils";

export const ssr = false; // Client-side only

export const load: PageLoad = async ({ fetch, url, depends }) => {
  try {
    depends("trace:data");

    const selectedRange = getCookie("trace_range") || "15min";

    const { startTime, endTime, bucketInterval } =
      calculateTimeRange(selectedRange);

    const metricsRequest: TraceMetricsRequest = {
      service_name: undefined,
      start_time: startTime,
      end_time: endTime,
      bucket_interval: bucketInterval,
    };

    let traceMetrics = await getServerTraceMetrics(fetch, metricsRequest);
    let tracePage = await getServerTracePage(fetch, {
      start_time: startTime,
      end_time: endTime,
      limit: 50,
    });

    if (!tracePage.items || tracePage.items.length === 0) {
      return {
        status: "not_found" as const,
        errorMessage:
          "No traces found for the selected time range. Try adjusting your time range or check if your application is generating traces.",
        initialFilters: {
          start_time: startTime,
          end_time: endTime,
          bucket_interval: bucketInterval,
          selected_range: selectedRange,
        },
      };
    }

    return {
      status: "success" as const,
      trace_page: tracePage,
      trace_metrics: traceMetrics,
      initialFilters: {
        start_time: startTime,
        end_time: endTime,
        bucket_interval: bucketInterval,
        selected_range: selectedRange,
      },
    };
  } catch (error) {
    console.error("Error loading trace data:", error);

    let errorMessage =
      "An unexpected error occurred while loading trace data. Please try again.";

    if (error instanceof Error) {
      if (
        error.message.includes("fetch") ||
        error.message.includes("network")
      ) {
        errorMessage =
          "Unable to connect to the trace service. Please check your network connection and try again.";
      } else if (error.message.includes("timeout")) {
        errorMessage =
          "The request timed out while loading trace data. Please try again.";
      } else if (
        error.message.includes("unauthorized") ||
        error.message.includes("403")
      ) {
        errorMessage =
          "You do not have permission to access trace data. Please contact your administrator.";
      } else {
        errorMessage = `Error: ${error.message}`;
      }
    }

    return {
      status: "error" as const,
      errorMessage,
      initialFilters: {
        start_time: new Date(Date.now() - 15 * 60 * 1000).toISOString(),
        end_time: new Date().toISOString(),
        bucket_interval: "1 minutes",
        selected_range: "15min",
      },
    };
  }
};
