import { type RequestHandler, json } from "@sveltejs/kit";
import { getGenAIEvalTaskDriftMetrics } from "$lib/server/scouter/drift/utils";

/** Get a page of latest metrics for drift profiles
 */
export const POST: RequestHandler = async ({ request, fetch }) => {
  const { profiles, time_range, max_data_points } = await request.json();
  const response = await getGenAIEvalTaskDriftMetrics(
    fetch,
    profiles,
    time_range,
    max_data_points
  );
  return json(response);
};
