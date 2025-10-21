// Health check endpoint

import type { RequestHandler } from "@sveltejs/kit";

export const GET: RequestHandler = async () => {
  return new Response("OK", { status: 200 });
};
