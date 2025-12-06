import { type RequestHandler, json } from "@sveltejs/kit";
import { getDashboardStats } from "$lib/server/card/utils";

/** Get dashboard stats
 */
export const POST: RequestHandler = async ({ request, fetch }) => {
  const { card } = await request.json();
  const response = await getDashboardStats(fetch);
  return json(response);
};
