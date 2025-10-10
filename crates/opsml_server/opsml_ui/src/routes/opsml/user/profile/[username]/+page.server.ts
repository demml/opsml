import type { PageServerLoad } from "./$types";
import { getUser } from "$lib/server/user/util";

export const load: PageServerLoad = async ({ params, cookies }) => {
  const username = params.username;
  const userInfo = await getUser(username, cookies.get("jwt_token"));
  return { userInfo };
};
