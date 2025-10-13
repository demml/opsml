import type { PageServerLoad } from "./$types";
import { getUser } from "$lib/server/user/util";

export const load: PageServerLoad = async ({ params, cookies, fetch }) => {
  const username = params.username ?? cookies.get("username") ?? "";
  const userInfo = await getUser(username, fetch);
  return { userInfo };
};
