import { type RequestHandler, json } from "@sveltejs/kit";
import type { TraceSpansResponse } from "$lib/components/trace/types";
import { getTraceSpansById } from "$lib/server/trace/utils";

export const GET: RequestHandler = async ({ params, fetch }) => {
  const { id } = params;

  if (!id) {
    return json({ response: null, error: "Missing trace ID" }, { status: 400 });
  }

  try {
    const response: TraceSpansResponse = await getTraceSpansById(fetch, id);
    return json({ response, error: null });
  } catch (error) {
    console.error("Error fetching trace spans by id:", error);
    return json(
      {
        response: null,
        error: error instanceof Error ? error.message : "Failed to fetch trace spans",
      },
      { status: 500 },
    );
  }
};
