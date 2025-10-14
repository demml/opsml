import type { LayoutServerLoad } from "./$types";
import { loadCardLayout } from "$lib/server/card/layout";

// @ts-ignore
export const load: LayoutServerLoad = async ({ params, parent, fetch }) => {
  const { registryType } = await parent();
  const { space, name, version } = params;

  return await loadCardLayout(registryType, space, name, version, fetch);
};
