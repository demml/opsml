import { type RequestHandler, json } from "@sveltejs/kit";
import { updateUser } from "$lib/server/user/utils";

/** Update user details
 */
export const PUT: RequestHandler = async ({ request, fetch }) => {
  const { options, username } = await request.json();
  const response = await updateUser(fetch, options, username);
  return json(response);
};
