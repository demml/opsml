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
} from "$lib/components/trace/utils";

export const load: PageLoad = async ({ parent }) => {
  const { metadata, registryType, settings } = await parent();

  if (!settings?.scouter_enabled) {
    return {
      trace: null,
      spans: null,
      type: "not_found" as const,
      errorMessage: "Scouter is not enabled.",
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
      return {
        trace: null,
        spans: null,
        type: "not_found" as const,
        errorMessage:
          "No trace found for this card. Ensure that the application is generating traces with the correct tags.",
      };
    }

    // Fetch spans and trace page in parallel for better performance
    const [spansDetails, tracePage] = await Promise.all([
      getServerTraceSpans(fetch, {
        trace_id: response.entity_id[0],
      }),
      getServerTracePage(fetch, {
        trace_ids: response.entity_id,
      }),
    ]);

    return {
      trace: tracePage.items[0],
      spans: spansDetails,
      errorMessage: "none",
    };
  } catch (error) {
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
        errorMessage = `Error: ${error.message}`;
      }
    }

    return {
      errorMessage,
      trace: null,
      spans: null,
      type: "error" as const,
    };
  }
};
