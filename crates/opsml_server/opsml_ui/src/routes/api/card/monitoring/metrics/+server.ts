import type { RequestHandler } from "../$types";
import { json } from "@sveltejs/kit";
import { getLatestMetrics } from "$lib/server/card/monitoring/utils";

/** Get a page of latest metrics for drift profiles
 */
export const POST: RequestHandler = async ({ request, fetch }) => {
  const { profiles, time_interval, max_data_points } = await request.json();
  const response = await getLatestMetrics(
    fetch,
    profiles,
    time_interval,
    max_data_points
  );
  return json(response);
};
