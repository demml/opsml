import type { PageLoad } from "./$types";
import {
  type TraceMetricsRequest,
  type TracePageFilter,
  type TraceFilters,
} from "$lib/components/trace/types";

import {
  getServerTracePage,
  getServerTraceMetrics,
  getCookie,
  calculateTimeRange,
} from "$lib/components/trace/utils";
import {
  getMockTraceMetrics,
  getMockTracePage,
} from "$lib/components/trace/mockData";
import { getEvalProfileOrUid } from "$lib/components/card/card_interfaces/enum";
import type { CardMetadata } from "$lib/server/card/layout";
import type { PromptCard } from "$lib/components/card/card_interfaces/promptcard";
import type { ServiceCard } from "$lib/components/card/card_interfaces/servicecard";
import { RegistryType } from "$lib/utils";

export const ssr = false;

export const load: PageLoad = async ({ fetch, depends, parent }) => {
  const parentData = await parent();
  const metadata = parentData.metadata as CardMetadata;
  const useMockFallback = Boolean(parentData.devMockEnabled);

  try {
    depends("trace:data");

    const registryTypeLower = metadata.registry_type.toLowerCase();
    if (
      registryTypeLower !== RegistryType.Prompt &&
      registryTypeLower !== RegistryType.Agent
    ) {
      throw new Error(
        `Observability is not supported for ${metadata.registry_type} cards`,
      );
    }
    const card = metadata as PromptCard | ServiceCard;

    const entity_uid = getEvalProfileOrUid(card);
    const selectedRange = getCookie("trace_range") || "15min";

    const { startTime, endTime, bucketInterval } =
      calculateTimeRange(selectedRange);

    const metricsRequest: TraceMetricsRequest = {
      service_name: undefined,
      start_time: startTime,
      end_time: endTime,
      bucket_interval: bucketInterval,
      entity_uid: entity_uid,
    };

    let traceMetrics = useMockFallback
      ? getMockTraceMetrics(metricsRequest)
      : await getServerTraceMetrics(fetch, metricsRequest);
    let tracePage = useMockFallback
      ? getMockTracePage({
          start_time: startTime,
          end_time: endTime,
          limit: 50,
          entity_uid: entity_uid,
        })
      : await getServerTracePage(fetch, {
          start_time: startTime,
          end_time: endTime,
          limit: 50,
          entity_uid: entity_uid,
        });

    if (!tracePage.items || tracePage.items.length === 0) {
      let filters: TraceFilters = {
        start_time: startTime,
        end_time: endTime,
        entity_uid: entity_uid,
      };
      let initialFilters: TracePageFilter = {
        filters: { ...filters },
        bucket_interval: bucketInterval,
        selected_range: selectedRange,
      };
      return {
        status: "not_found" as const,
        errorMessage:
          "No traces found for the selected time range. Try adjusting your time range or check if your application is generating traces.",
        initialFilters: initialFilters,
        mockMode: useMockFallback,
      };
    }
    let traceFilter: TraceFilters = {
      start_time: startTime,
      end_time: endTime,
      entity_uid: entity_uid,
    };
    let initialFilters: TracePageFilter = {
      filters: { ...traceFilter },
      bucket_interval: bucketInterval,
      selected_range: selectedRange,
    };

    return {
      status: "success" as const,
      trace_page: tracePage,
      trace_metrics: traceMetrics,
      initialFilters,
      mockMode: useMockFallback,
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

    let initialFilters: TracePageFilter = {
      filters: {
        start_time: new Date(Date.now() - 15 * 60 * 1000).toISOString(),
        end_time: new Date().toISOString(),
      },
      bucket_interval: "1 minutes",
      selected_range: "15min",
    };
    return {
      status: "error" as const,
      errorMessage,
      initialFilters,
      mockMode: false,
    };
  }
};
