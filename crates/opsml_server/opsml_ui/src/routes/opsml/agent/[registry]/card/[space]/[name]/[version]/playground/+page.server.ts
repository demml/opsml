import type { PageServerLoad } from "./$types";

/**
 * Pass through layout data to the playground page
 */
export const load: PageServerLoad = async ({ parent }) => {
  return await parent();
};
