import type { PageServerLoad } from "./$types";
import { getUser } from "$lib/server/user/util";

export const load: PageServerLoad = async ({ params, cookies, fetch }) => {
  const username = params.username;
  const userInfo = await getUser(username, fetch, cookies.get("jwt_token"));
  return { userInfo };
};
