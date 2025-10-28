import type { PageServerLoad } from "./$types";
import { getUser } from "$lib/server/user/utils";
import { logger } from "$lib/server/logger";

export const load: PageServerLoad = async ({ cookies, fetch }) => {
  const username = cookies.get("username") ?? "";
  const userInfo = await getUser(username, fetch);
  logger.debug(
    `Fetched user info for profile page: ${JSON.stringify(userInfo)}`
  );
  return { userInfo };
};
