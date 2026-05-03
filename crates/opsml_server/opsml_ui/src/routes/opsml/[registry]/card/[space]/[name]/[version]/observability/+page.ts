export const ssr = false;

import type { PageLoad } from "./$types";
import type {
  ScouterEntityIdResponse,
  ScouterEntityIdTagsRequest,
  Tag,
} from "$lib/components/tags/types";
import { getScouterServerEntityIdFromTags } from "$lib/components/tags/utils";
import {
  getCardKeyAttribute,
  getServerTraceSpans,
  getServerTracePage,
  getServerGenAiTraceMetrics,
  buildGenAiBySpanId,
} from "$lib/components/trace/utils";
import {
  getMockTracePage,
  getMockTraceSpans,
} from "$lib/components/trace/mockData";
import { getMockGenAiTraceMetrics } from "$lib/components/trace/genai/mockData";
import type { GenAiTraceMetricsResponse } from "$lib/components/scouter/genai/types";

function buildMockBundle(metadata_uid: string) {
  const tracePage = getMockTracePage({ entity_uid: metadata_uid });
  const trace = tracePage.items[0] ?? null;
  const spans = trace ? getMockTraceSpans({ trace_id: trace.trace_id }) : null;
  const spanIds = spans?.spans.map((s) => s.span_id) ?? [];
  const genai = trace
    ? getMockGenAiTraceMetrics(trace.trace_id, spanIds)
    : null;
  const genAiBySpanId = buildGenAiBySpanId(genai);
  return { trace, spans, genai, genAiBySpanId };
}

export const load: PageLoad = async ({ parent }) => {
  const { metadata, registryType, settings, devMockEnabled } = await parent();
  const useMockFallback = Boolean(devMockEnabled);

  if (!settings?.scouter_enabled) {
    if (useMockFallback) {
      return {
        ...buildMockBundle(metadata.uid),
        errorMessage: "none",
        mockMode: true,
      };
    }

    return {
      trace: null,
      spans: null,
      genai: null,
      genAiBySpanId: {},
      type: "not_found" as const,
      errorMessage: "Scouter is not enabled.",
      mockMode: false,
    };
  }

  try {
    const key = getCardKeyAttribute(registryType);

    const tag: Tag = {
      key,
      value: metadata.uid,
    };

    const request: ScouterEntityIdTagsRequest = {
      entity_type: "trace",
      tags: [tag],
      match_all: true,
    };

    const response: ScouterEntityIdResponse =
      await getScouterServerEntityIdFromTags(fetch, request);

    if (response.entity_id.length === 0) {
      if (useMockFallback) {
        return {
          ...buildMockBundle(metadata.uid),
          errorMessage: "none",
          mockMode: true,
        };
      }

      return {
        trace: null,
        spans: null,
        genai: null,
        genAiBySpanId: {},
        type: "not_found" as const,
        errorMessage:
          "No trace found for this card. Ensure that the application is generating traces with the correct tags.",
        mockMode: false,
      };
    }

    const trace_id = response.entity_id[0];
    const [spansDetails, tracePage] = await Promise.all([
      getServerTraceSpans(fetch, { trace_id }),
      getServerTracePage(fetch, { trace_ids: response.entity_id }),
    ]);

    let genai: GenAiTraceMetricsResponse | null = null;
    try {
      genai = await getServerGenAiTraceMetrics(fetch, trace_id);
    } catch {
      // GenAI metrics are non-critical; trace view remains functional without them
    }

    const genAiBySpanId = buildGenAiBySpanId(genai);

    return {
      trace: tracePage.items[0],
      spans: spansDetails,
      genai,
      genAiBySpanId,
      errorMessage: "none",
      mockMode: false,
    };
  } catch (error) {
    if (useMockFallback) {
      return {
        ...buildMockBundle(metadata.uid),
        errorMessage: "none",
        mockMode: true,
      };
    }

    console.error("Error loading span data:", error);

    let errorMessage =
      "An unexpected error occurred while loading span data. Please try again.";

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
        errorMessage = "An unexpected error occurred while loading trace data.";
      }
    }

    return {
      errorMessage,
      trace: null,
      spans: null,
      genai: null,
      genAiBySpanId: {},
      type: "error" as const,
      mockMode: false,
    };
  }
};
